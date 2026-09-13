#!/usr/bin/env python3
"""Render a reproducible social clip using SVG, librsvg, and FFmpeg.

Requires Python 3.10+, fontTools, rsvg-convert, ffmpeg, and a directory containing the
site's Cormorant Garamond and DM Sans TTF fonts. See routing-social.md.
"""

import argparse
import bisect
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import html
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont


ROOT = Path(__file__).resolve().parents[1]
BG, TEXT, MUTED = "#FAF7F2", "#2C2C2C", "#6B6560"
SURFACE, BORDER, ACCENT = "#F3EFE8", "#E0DAD0", "#2A7F6F"
COLORS = ["#3D6F9F", "#B86432", "#2A7F6F", "#735E98", "#377985"]
PINS = [0, 0, 3, 6, 8]
SECONDS, FPS = 22, 30
FONTS = {}


def workload():
    """Same closed-loop workload and tie ordering as http-routing-article.js."""
    requests, active = [], []

    def dispatch(ident, connection, start):
        duration = 2 + ((ident * 17 + connection * 3 + 5) % 6)
        req = dict(id=ident, connection=connection, start=start,
                   duration=duration, end=start + duration,
                   cluster=PINS[connection], proxy=len(requests) % 10)
        requests.append(req)
        return req

    for connection in range(5):
        active.append(dispatch(connection, connection, 0))
    while any(active):
        event = min(r["end"] for r in active if r)
        for connection, req in enumerate(active):
            if req and req["end"] == event:
                active[connection] = (dispatch(req["id"] + 5, connection, event)
                                      if req["id"] + 5 < 100 else None)
    return requests


REQUESTS = workload()
END = max(r["end"] for r in REQUESTS)


def sim_time(seconds):
    if seconds < 2:
        return -1
    if seconds < 7:
        return seconds - 2
    return min(END, 5 + (seconds - 7) * (END - 5) / 10)


def wall_time(sim):
    return 2 + sim if sim <= 5 else 7 + (sim - 5) * 10 / (END - 5)


@lru_cache(maxsize=None)
def text_outline(value, family, weight):
    font = FONTS[family, weight]
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    output, advance = [], 0
    for char in value:
        name = cmap.get(ord(char), ".notdef")
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        output.append(f'<path transform="translate({advance} 0)" d="{pen.getCommands()}"/>')
        advance += font["hmtx"][name][0]
    return "".join(output), advance, font["head"].unitsPerEm


def text(x, y, value, size=24, fill=TEXT, weight=400, anchor="start", display=False):
    family = "Cormorant Garamond" if display else "DM Sans"
    outlines, advance, units = text_outline(str(value), family, weight)
    scale = size / units
    x -= advance * scale * ({"start":0, "middle":.5, "end":1}[anchor])
    return (f'<g aria-label="{html.escape(str(value), quote=True)}" '
            f'transform="translate({x} {y}) scale({scale} {-scale})" fill="{fill}">'
            f'{outlines}</g>')


def rect(x, y, w, h, fill=SURFACE, stroke=BORDER, radius=6, extra=""):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.5" {extra}/>')


def circle(x, y, r, fill, stroke="none", width=1, opacity=1):
    return (f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{width}" opacity="{opacity:.3f}"/>')


def cubic(a, b):
    dx = (b[0] - a[0]) * .46
    return a, (a[0] + dx, a[1]), (b[0] - dx, b[1]), b


@lru_cache(maxsize=None)
def route(connection, pod):
    cy = 83 + 31 * connection
    port = 497 + 10 * connection
    px = 90 + pod * 100
    return (
        cubic((194, 145), (260, cy)),
        cubic((260, cy), (308, cy)),
        cubic((308, cy), (426, 145)),
        ((426, 145), (460, 145), (port, 150), (port, 178)),
        ((port, 178), (port, 194), (port, 202), (port, 221)),
        ((port, 221), (port, 236), (px, 226), (px, 256)),
    )


def path_data(segments):
    x, y = segments[0][0]
    parts = [f"M{x} {y}"]
    for _, b, c, d in segments:
        parts.append(f"C{b[0]} {b[1]} {c[0]} {c[1]} {d[0]} {d[1]}")
    return " ".join(parts)


def path(segments, color, width=3, opacity=1):
    return (f'<path d="{path_data(segments)}" fill="none" stroke="{color}" '
            f'stroke-width="{width}" stroke-linecap="round" opacity="{opacity}"/>')


@lru_cache(maxsize=None)
def arc_table(connection, pod):
    points, distances = [], [0]
    for segment in route(connection, pod):
        for i in range(81):
            t = i / 80
            u = 1 - t
            weights = (u**3, 3*u*u*t, 3*u*t*t, t**3)
            p = tuple(sum(w * pt[axis] for w, pt in zip(weights, segment))
                      for axis in (0, 1))
            if points:
                distances.append(distances[-1] + math.dist(points[-1], p))
            points.append(p)
    return points, distances


def request_point(connection, pod, progress):
    points, distances = arc_table(connection, pod)
    distance = distances[-1] * min(1, max(0, progress))
    index = min(len(points)-1, bisect.bisect_left(distances, distance))
    if index == 0:
        return points[0]
    segment = distances[index] - distances[index-1]
    t = (distance - distances[index-1]) / segment if segment else 0
    return tuple(points[index-1][axis] * (1-t) + points[index][axis] * t
                 for axis in (0, 1))


def lane(kind, top, seconds):
    sim = sim_time(seconds)
    active = [r for r in REQUESTS if r["start"] <= sim < r["end"]]
    completed = [r for r in REQUESTS if r["end"] <= sim]
    counts = [sum(r[kind] == pod for r in completed) for pod in range(10)]
    final = sim >= END
    cluster = kind == "cluster"
    title = "ClusterIP" if cluster else "HTTP-aware proxy"
    subtitle = "One backend per persistent connection" if cluster else "One backend choice per request · round robin"
    out = [f'<g transform="translate(0 {top})">', text(48, 27, title, 33, weight=600),
           text(48, 61, subtitle, 23, fill=MUTED)]

    # Persistent paths are present even while no requests are active.
    for c in range(5):
        out.append(path(route(c, PINS[c])[:3], COLORS[c], 2.5, .8))
        if cluster:
            out.append(path(route(c, PINS[c])[3:], COLORS[c], 2.5, .8))
    for r in active:
        c, pod = r["connection"], r[kind]
        out.append(path(route(c, pod), COLORS[c], 3.2, .95))

    out.extend([rect(52, 117, 142, 56, BG), text(123, 152, "Client", 24, anchor="middle")])
    for c in range(5):
        out.extend([rect(260, 70 + 31*c, 48, 26, BG),
                    text(284, 90 + 31*c, f"C{c+1}", 19, anchor="middle")])
    out.extend([rect(426, 116, 182, 62, BG, ACCENT),
                text(517, 142, "ClusterIP" if cluster else "HTTP proxy", 25, anchor="middle"),
                text(517, 166, "virtual Service IP" if cluster else "selects per request", 18, fill=MUTED, anchor="middle")])

    if final:
        out.extend([text(1018, 123, "4 / 10" if cluster else "10 / 10", 42, weight=600, anchor="end"),
                    text(1018, 153, "pods used", 23, fill=MUTED, anchor="end"),
                    text(1018, 195, "6 pods received no requests" if cluster else "10 requests on every pod", 23, anchor="end")])
    else:
        out.extend([text(1018, 123, f"{len(completed)} / 100", 42, weight=600, anchor="end"),
                    text(1018, 153, "requests completed", 23, fill=MUTED, anchor="end"),
                    text(1018, 195, f"{len(active)} in flight", 23, anchor="end")])

    for pod in range(10):
        x = 46 + 100 * pod
        receiving = any(r[kind] == pod for r in active)
        used = counts[pod] > 0 or receiving or (cluster and pod in PINS)
        out.append(rect(x, 256, 88, 68, BG if used else SURFACE,
                        ACCENT if used else BORDER,
                        extra='' if used else 'stroke-dasharray="4 4"'))
        out.extend([text(x+44, 281, f"Pod {pod+1}", 20, anchor="middle"),
                    text(x+44, 312, counts[pod], 26, weight=600, anchor="middle")])
    out.append(text(1018, 350, "Completed requests per pod", 19, fill=MUTED, anchor="end"))

    # Finish traveling before completion, dwelling visibly at the destination.
    for r in active:
        c, pod = r["connection"], r[kind]
        progress = (sim - r["start"]) / r["duration"]
        x, y = request_point(c, pod, progress / .86)
        out.append(circle(x, y, 7.5, COLORS[c], BG, 2.5))
    for r in completed:
        age = seconds - wall_time(r["end"])
        if 0 <= age < .32:
            fade = 1 - age / .32
            out.append(circle(90 + 100*r[kind], 256, 8 + age*33,
                              "none", COLORS[r["connection"]], 3, fade))
    out.append('</g>')
    return "".join(out)


def frame(seconds):
    final = seconds >= 17
    status = ("Same five connections. A very different distribution." if final else
              "Five connections established. Watch where their requests go." if seconds < 2 else
              "Follow the dots: each request reaches a pod, then completes." if seconds < 7 else
              "Same connections · remaining requests accelerated")
    return """<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">""" + "".join([
        rect(0, 0, 1080, 1080, BG, BG, 0),
        text(48, 76, "Connections ≠ requests", 62, weight=600, display=True),
        text(48, 119, "1 client · 5 connections · 10 pods · 100 requests per route", 26),
        text(48, 170, status, 24, fill=MUTED),
        '<path d="M48 198 H1032 M48 582 H1032" stroke="'+BORDER+'" stroke-width="1.5"/>',
        lane("cluster", 218, seconds), lane("proxy", 602, seconds),
        text(48, 988, "Persistent HTTP/1.1 · one in-flight request per connection", 22, fill=MUTED),
        text(48, 1019, "Illustrative progress · equal pods · no retries, failures or affinity", 20, fill=MUTED),
        text(48, 1055, "Case against ClusterIP", 25, weight=600, display=True),
        text(1032, 1055, "kucukaslan.com.tr", 22, anchor="end"),
        '</svg>'
    ])


def validate():
    assert len(REQUESTS) == 100
    assert len({r["id"] for r in REQUESTS}) == 100
    for req in REQUESTS:
        assert req["cluster"] == PINS[req["connection"]]
    for time in sorted({r["start"] for r in REQUESTS} | {r["end"] for r in REQUESTS}):
        active = [r for r in REQUESTS if r["start"] <= time < r["end"]]
        assert len(active) <= 5
        assert len({r["connection"] for r in active}) == len(active)
    assert [sum(r["cluster"] == p for r in REQUESTS) for p in range(10)] == [40,0,0,20,0,0,20,0,20,0]
    assert [sum(r["proxy"] == p for r in REQUESTS) for p in range(10)] == [10]*10
    for c in range(5):
        for pod in range(10):
            assert math.dist(request_point(c, pod, 1), (90+100*pod, 256)) < .001


def run(args):
    validate()
    for binary in ("rsvg-convert", "ffmpeg"):
        if not shutil.which(binary):
            raise SystemExit(f"Required program missing: {binary}")
    for family, filename in (("DM Sans", "DM-Sans.ttf"), ("Cormorant Garamond", "Cormorant-Garamond.ttf")):
        for weight in (400, 600):
            font = TTFont(args.fonts / filename)
            axes = {axis.axisTag for axis in font["fvar"].axes} if "fvar" in font else set()
            location = {tag:value for tag, value in (("wght", weight), ("opsz", 24)) if tag in axes}
            FONTS[family, weight] = instantiateVariableFont(font, location) if location else font
    args.output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="routing-social-") as scratch:
        scratch = Path(scratch)

        def raster(svg, target):
            subprocess.run(["rsvg-convert", "-o", str(target)], input=svg.encode(), check=True)

        if args.preview_only:
            for second in (0, 4, 12, 19):
                svg = frame(second)
                (args.output / f"preview-{second:02}.svg").write_text(svg)
                raster(svg, args.output / f"preview-{second:02}.png")
            print("Preview frames ready.", flush=True)
            return

        stem = "case-against-clusterip"
        poster = frame(19)
        (args.output / f"{stem}-poster.svg").write_text(poster)
        raster(poster, args.output / f"{stem}-poster.png")

        def render(index):
            raster(frame(index/FPS), scratch / f"frame-{index:04}.png")
            return index

        with ThreadPoolExecutor(max_workers=4) as pool:
            for i in pool.map(render, range(SECONDS*FPS)):
                if i % 120 == 0:
                    print(f"Rendered {i}/{SECONDS*FPS} frames", flush=True)

        mp4 = args.output / f"{stem}.mp4"
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning",
                        "-framerate", str(FPS), "-i", str(scratch / "frame-%04d.png"),
                        "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.0",
                        "-pix_fmt", "yuv420p", "-preset", "slow", "-crf", "18",
                        "-maxrate", "6M", "-bufsize", "12M", "-movflags", "+faststart",
                        "-an", str(mp4)], check=True)
        print("MP4 ready. Encoding the looping GIF.", flush=True)
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-i", str(mp4),
                        "-filter_complex", "fps=10,scale=720:720:flags=lanczos,split[a][b];"
                        "[a]palettegen=max_colors=128:stats_mode=diff[p];"
                        "[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle",
                        "-loop", "0", str(args.output / f"{stem}.gif")], check=True)
        print(json.dumps({"seconds":SECONDS, "mp4":"1080×1080, H.264, 30 fps",
                          "gif":"720×720, 10 fps, loops forever", "peak_concurrency_per_route":5,
                          "cluster_completed":[40,0,0,20,0,0,20,0,20,0], "proxy_completed":[10]*10}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fonts", type=Path, required=True, help="Directory containing the two site fonts as TTF files")
    parser.add_argument("--output", type=Path, default=ROOT / "static/media/routing")
    parser.add_argument("--preview-only", action="store_true")
    run(parser.parse_args())
