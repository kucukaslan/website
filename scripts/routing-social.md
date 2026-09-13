# Routing animation for social posts

Upload `static/media/routing/case-against-clusterip.mp4` directly as video on
LinkedIn or X. The 22-second square clip is silent and contains its own explanatory
text. A 720-pixel looping GIF is included for places where a GIF is preferable.
The matching `-poster.png` can be used as the video's thumbnail.

The article's existing `feature_image` stays a PNG for link previews. These files
are separate post attachments; they are not loaded by the article.

The animation uses the same deterministic 100-request workload as the article:
five closed-loop connections, one request in flight per connection, fixed
ClusterIP pins `[1, 1, 4, 7, 9]`, and round-robin proxy dispatch. It starts with
established connections, slows down the first requests, accelerates the remaining
workload, then holds the result for five seconds. Dots follow the drawn curves
and dwell at their destination before completion rings appear. Travel represents
request progress, not measured network latency. Each route handles its own copy
of the same workload.

## Regenerate

Requires Python 3.10+, the `fontTools` package, `rsvg-convert` (librsvg), and FFmpeg with libx264.
Download the site's **DM Sans** and **Cormorant Garamond** TTF fonts from their
[Google Fonts source](https://github.com/google/fonts/tree/main/ofl) into a temporary
directory as `DM-Sans.ttf` and `Cormorant-Garamond.ttf`. These fonts are distributed under the SIL Open Font License; they are
used to rasterize text and are not bundled with the media.

```sh
python3 scripts/render-routing-social.py --fonts /path/to/font-directory --preview-only --output /tmp/routing-preview
python3 scripts/render-routing-social.py --fonts /path/to/font-directory
```

The renderer validates request counts, connection pinning, maximum concurrency,
and curve endpoints before exporting. Temporary frames are removed automatically.
No runtime dependency is added to the site. The matching poster SVG remains
editable, with text outlined for consistent rendering; the script is the source
for the animation and its labels.

Suggested accessibility description: “Two routing diagrams send the same 100
requests through five persistent HTTP connections to ten pods. ClusterIP keeps
each connection attached to one pod: one pod completes 40 requests, three complete
20 each, and six remain unused. An illustrative round-robin HTTP proxy distributes
the requests evenly, with ten completed by each pod.”

Format references: [LinkedIn video specifications](https://www.linkedin.com/help/linkedin/answer/a1311816),
[X video help](https://help.x.com/en/using-x/x-videos), and
[X GIF help](https://help.x.com/en/using-x/posting-gifs-and-pictures).
