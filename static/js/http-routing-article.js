(function () {
  "use strict";

  const NS = "http://www.w3.org/2000/svg";
  const TOTAL_REQUESTS = 100;
  const CONNECTIONS = 5;
  const PODS = 10;
  const CLUSTER_PINS = [0, 0, 3, 6, 8];
  const CONNECTION_COLORS = [
    "var(--routing-blue)",
    "var(--routing-orange)",
    "var(--routing-green)",
    "var(--routing-violet)",
    "var(--routing-cyan)",
  ];

  function svgElement(name, attributes, text) {
    const element = document.createElementNS(NS, name);
    Object.entries(attributes || {}).forEach(([key, value]) =>
      element.setAttribute(key, value),
    );
    if (text !== undefined) element.textContent = text;
    return element;
  }

  function curvedPath(fromX, fromY, toX, toY) {
    const bend = Math.max(40, Math.abs(toX - fromX) * 0.45);
    return `M${fromX} ${fromY} C${fromX + bend} ${fromY} ${toX - bend} ${toY} ${toX} ${toY}`;
  }

  function appendPath(group, d, className, stroke) {
    const path = svgElement("path", { d, class: className });
    if (stroke) path.style.stroke = stroke;
    group.appendChild(path);
    return path;
  }

  function appendNode(group, x, y, width, height, label, secondary, className) {
    const node = svgElement("g", {
      transform: `translate(${x} ${y})`,
      class: className || "",
    });
    node.appendChild(
      svgElement("rect", {
        width,
        height,
        rx: 6,
        class: "routing-svg__node",
      }),
    );
    node.appendChild(
      svgElement(
        "text",
        { x: width / 2, y: secondary ? 20 : height / 2 + 4, "text-anchor": "middle" },
        label,
      ),
    );
    if (secondary) {
      node.appendChild(
        svgElement(
          "text",
          {
            x: width / 2,
            y: 37,
            "text-anchor": "middle",
            class: "routing-svg__secondary",
          },
          secondary,
        ),
      );
    }
    group.appendChild(node);
    return node;
  }

  function durationFor(requestId, connection) {
    return 2 + ((requestId * 17 + connection * 3 + 5) % 6);
  }

  function buildWorkload() {
    const requests = Array(TOTAL_REQUESTS);
    const frames = [];
    const activeByConnection = Array(CONNECTIONS).fill(null);
    let dispatchOrdinal = 0;

    function createRequest(id, connection, start) {
      const request = {
        id,
        connection,
        start,
        duration: durationFor(id, connection),
        clusterPod: CLUSTER_PINS[connection],
        proxyPod: dispatchOrdinal % PODS,
      };
      request.completion = request.start + request.duration;
      requests[id] = request;
      activeByConnection[connection] = request;
      dispatchOrdinal += 1;
      return request;
    }

    const initialStarts = [];
    for (let connection = 0; connection < CONNECTIONS; connection += 1) {
      initialStarts.push(createRequest(connection, connection, 0).id);
    }
    frames.push({ time: 0, starts: initialStarts, completes: [] });

    while (activeByConnection.some(Boolean)) {
      const time = Math.min(
        ...activeByConnection.filter(Boolean).map((request) => request.completion),
      );
      const completes = activeByConnection
        .map((request, connection) => ({ request, connection }))
        .filter(({ request }) => request && request.completion === time)
        .sort((a, b) => a.connection - b.connection);
      const starts = [];

      completes.forEach(({ request, connection }) => {
        activeByConnection[connection] = null;
        const nextId = request.id + CONNECTIONS;
        if (nextId < TOTAL_REQUESTS) {
          starts.push(createRequest(nextId, connection, time).id);
        }
      });

      frames.push({
        time,
        completes: completes.map(({ request }) => request.id),
        starts,
      });
    }

    return { requests, frames };
  }

  function freshRuntime() {
    return {
      active: new Set(),
      activeByPod: Array(PODS).fill(0),
      completedByPod: Array(PODS).fill(0),
      completed: 0,
    };
  }

  function pointAlongPaths(paths, progress) {
    const lengths = paths.map((path) => path.getTotalLength());
    const total = lengths.reduce((sum, length) => sum + length, 0);
    let remaining = total * Math.max(0, Math.min(1, progress));
    for (let index = 0; index < paths.length; index += 1) {
      if (remaining <= lengths[index]) {
        return paths[index].getPointAtLength(remaining);
      }
      remaining -= lengths[index];
    }
    return paths.at(-1).getPointAtLength(lengths.at(-1));
  }

  function setupScenario(svg, scenario) {
    svg.replaceChildren();
    const title = svgElement(
      "title",
      {},
      scenario === "cluster"
        ? "Five persistent connections pinned to four of ten pods"
        : "An HTTP proxy selecting a backend for every request",
    );
    const description = svgElement(
      "desc",
      {},
      scenario === "cluster"
        ? "Each connection keeps one colored route from the client through the ClusterIP to a fixed backend pod. Request markers travel along those routes."
        : "Client connections terminate at the proxy. Each request marker then travels from the proxy to the next pod selected by round robin.",
    );
    svg.append(title, description);

    const base = svgElement("g", { class: "routing-svg__base" });
    const active = svgElement("g", { class: "routing-svg__active" });
    const nodes = svgElement("g", { class: "routing-svg__nodes" });
    const tokens = svgElement("g", { class: "routing-svg__tokens" });
    const events = svgElement("g", { class: "routing-svg__events" });
    svg.append(base, active, nodes, tokens, events);

    const clientCenter = { x: 130, y: 215 };
    const routeCenter = { x: 540, y: 215 };
    const connectionCenters = Array.from({ length: CONNECTIONS }, (_, index) => ({
      x: 300,
      y: 70 + index * 72,
    }));
    const podCenters = Array.from({ length: PODS }, (_, index) => ({
      x: 720,
      y: 28 + index * 39,
    }));

    connectionCenters.forEach((connection, index) => {
      const color = CONNECTION_COLORS[index];
      appendPath(
        base,
        curvedPath(clientCenter.x, clientCenter.y, 250, connection.y),
        `routing-svg__base-path routing-svg__base-path--${index + 1}`,
        color,
      );
      appendPath(
        base,
        curvedPath(350, connection.y, 480, routeCenter.y),
        `routing-svg__base-path routing-svg__base-path--${index + 1}`,
        color,
      );
      if (scenario === "cluster") {
        const pod = podCenters[CLUSTER_PINS[index]];
        appendPath(
          base,
          curvedPath(routeCenter.x + 60, routeCenter.y, pod.x, pod.y),
          `routing-svg__base-path routing-svg__base-path--${index + 1}`,
          color,
        );
      }
    });

    if (scenario === "proxy") {
      podCenters.forEach((pod) =>
        appendPath(
          base,
          curvedPath(routeCenter.x + 60, routeCenter.y, pod.x, pod.y),
          "routing-svg__base-path",
        ),
      );
    }

    nodes.append(
      svgElement("text", { x: 30, y: 24, class: "routing-svg__eyebrow" }, "CLIENT"),
      svgElement("text", { x: 250, y: 24, class: "routing-svg__eyebrow" }, "CONNECTIONS"),
      svgElement(
        "text",
        { x: 480, y: 24, class: "routing-svg__eyebrow" },
        scenario === "cluster" ? "VIRTUAL SERVICE IP" : "HTTP PROXY",
      ),
      svgElement("text", { x: 720, y: 24, class: "routing-svg__eyebrow" }, "PODS"),
    );

    appendNode(nodes, 30, 186, 100, 58, "Client", "pool size 5");
    connectionCenters.forEach((connection, index) =>
      appendNode(nodes, 250, connection.y - 18, 100, 36, `C${index + 1}`),
    );
    const routeNode = appendNode(
      nodes,
      480,
      186,
      120,
      58,
      scenario === "cluster" ? "ClusterIP" : "HTTP proxy",
      scenario === "cluster" ? "selects once" : "selects per request",
    );
    routeNode.querySelector("rect").classList.add("routing-svg__service");

    const podText = [];
    const podRects = [];
    podCenters.forEach((pod, index) => {
      const group = appendNode(nodes, 720, pod.y - 16, 154, 32, `Pod ${index + 1}`);
      const rect = group.querySelector("rect");
      const label = group.querySelector("text");
      label.setAttribute("x", "12");
      label.setAttribute("text-anchor", "start");
      const status = svgElement(
        "text",
        {
          x: 142,
          y: 20,
          "text-anchor": "end",
          class: "routing-svg__secondary",
        },
        "0 done",
      );
      group.appendChild(status);
      podText.push(status);
      podRects.push(rect);
    });

    svg._routing = {
      scenario,
      active,
      tokens,
      events,
      podText,
      podRects,
      clientCenter,
      routeCenter,
      connectionCenters,
      podCenters,
    };
  }

  function renderScenario(svg, runtime, state) {
    const refs = svg._routing;
    refs.active.replaceChildren();
    refs.tokens.replaceChildren();
    refs.events.replaceChildren();

    refs.podText.forEach((text, pod) => {
      const done = runtime.completedByPod[pod];
      const active = runtime.activeByPod[pod];
      text.textContent = `${done} done${active ? ` · ${active} active` : ""}`;
      const used = done > 0 || active > 0 ||
        (refs.scenario === "cluster" && CLUSTER_PINS.includes(pod));
      refs.podRects[pod].classList.toggle("routing-svg__pod-used", used);
      refs.podRects[pod].classList.toggle("routing-svg__pod-idle", !used);
    });

    runtime.active.forEach((requestId) => {
      const request = state.requests[requestId];
      const connection = refs.connectionCenters[request.connection];
      const podIndex =
        refs.scenario === "cluster" ? request.clusterPod : request.proxyPod;
      const pod = refs.podCenters[podIndex];
      const color =
        refs.scenario === "cluster"
          ? CONNECTION_COLORS[request.connection]
          : "var(--accent)";
      const paths = [
        appendPath(
          refs.active,
          curvedPath(refs.clientCenter.x, refs.clientCenter.y, 250, connection.y),
          "routing-svg__active-path",
          color,
        ),
        appendPath(
          refs.active,
          curvedPath(350, connection.y, 480, refs.routeCenter.y),
          "routing-svg__active-path",
          color,
        ),
        appendPath(
          refs.active,
          curvedPath(refs.routeCenter.x + 60, refs.routeCenter.y, pod.x, pod.y),
          "routing-svg__active-path",
          color,
        ),
      ];
      const progress = (state.visualTime - request.start) / request.duration;
      const point = pointAlongPaths(paths, progress);
      const token = svgElement("circle", {
        cx: point.x,
        cy: point.y,
        r: 6,
        class: "routing-svg__request",
      });
      token.appendChild(
        svgElement(
          "title",
          {},
          `Request ${request.id + 1}: C${request.connection + 1} to Pod ${podIndex + 1}`,
        ),
      );
      refs.tokens.appendChild(token);
    });

    (state.lastFrame?.completes || []).forEach((requestId, offset) => {
      const request = state.requests[requestId];
      const podIndex =
        refs.scenario === "cluster" ? request.clusterPod : request.proxyPod;
      const pod = refs.podCenters[podIndex];
      refs.events.appendChild(
        svgElement("circle", {
          cx: pod.x,
          cy: pod.y + ((offset % 3) - 1) * 4,
          r: 9,
          class: "routing-svg__completion",
        }),
      );
    });
  }

  function initializeComparison(root) {
    const workload = buildWorkload();
    const state = {
      ...workload,
      cluster: freshRuntime(),
      proxy: freshRuntime(),
      frameIndex: -1,
      time: 0,
      visualTime: 0,
      lastFrame: null,
      playing: false,
      animationFrame: null,
    };

    const clusterSvg = root.querySelector('[data-scenario="cluster"]');
    const proxySvg = root.querySelector('[data-scenario="proxy"]');
    const status = root.querySelector("[data-status]");
    const progress = root.querySelector("[data-progress]");
    const clusterMetric = root.querySelector("[data-cluster-metric]");
    const proxyMetric = root.querySelector("[data-proxy-metric]");
    const clusterSummary = root.querySelector("[data-cluster-summary]");
    const proxySummary = root.querySelector("[data-proxy-summary]");
    const buttons = {
      step: root.querySelector('[data-action="step"]'),
      play: root.querySelector('[data-action="play"]'),
      result: root.querySelector('[data-action="result"]'),
      reset: root.querySelector('[data-action="reset"]'),
    };
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

    setupScenario(clusterSvg, "cluster");
    setupScenario(proxySvg, "proxy");
    root.classList.add("is-enhanced");

    function applyToRuntime(runtime, ids, starting, podKey) {
      ids.forEach((id) => {
        const pod = state.requests[id][podKey];
        if (starting) {
          runtime.active.add(id);
          runtime.activeByPod[pod] += 1;
        } else if (runtime.active.delete(id)) {
          runtime.activeByPod[pod] -= 1;
          runtime.completedByPod[pod] += 1;
          runtime.completed += 1;
        }
      });
    }

    function isComplete() {
      return state.frameIndex >= state.frames.length - 1;
    }

    function render() {
      renderScenario(clusterSvg, state.cluster, state);
      renderScenario(proxySvg, state.proxy, state);
      clusterMetric.textContent = `${state.cluster.completed} completed`;
      proxyMetric.textContent = `${state.proxy.completed} completed`;
      progress.textContent = `${state.cluster.completed} / ${TOTAL_REQUESTS} requests completed`;

      if (isComplete()) {
        clusterSummary.textContent = "4 / 10 pods used · completed range 0–40.";
        proxySummary.textContent = "10 / 10 pods used · exactly 10 requests each.";
      } else {
        clusterSummary.textContent = `Five pinned connections → four pods · ${state.cluster.active.size} active.`;
        proxySummary.textContent = `Round robin per request · ${state.proxy.active.size} active.`;
      }

      buttons.step.disabled = isComplete();
      buttons.result.disabled = isComplete();
      buttons.play.disabled = isComplete();
    }

    function applyFrame(frame, shouldRender) {
      applyToRuntime(state.cluster, frame.completes, false, "clusterPod");
      applyToRuntime(state.proxy, frame.completes, false, "proxyPod");
      applyToRuntime(state.cluster, frame.starts, true, "clusterPod");
      applyToRuntime(state.proxy, frame.starts, true, "proxyPod");
      state.time = frame.time;
      state.visualTime = frame.time;
      state.lastFrame = frame;

      if (!shouldRender) return;
      if (isComplete()) {
        status.textContent =
          "Complete. ClusterIP used 4 of 10 pods; the HTTP proxy used all 10 evenly.";
      } else {
        status.textContent = `Time ${frame.time}: ${frame.starts.length} started, ${frame.completes.length} completed, ${state.cluster.active.size} active.`;
      }
      render();
    }

    function stop() {
      state.playing = false;
      if (state.animationFrame !== null) {
        cancelAnimationFrame(state.animationFrame);
        state.animationFrame = null;
      }
      buttons.play.textContent = "Play";
      buttons.play.setAttribute("aria-pressed", "false");
    }

    function step() {
      stop();
      if (isComplete()) return;
      state.frameIndex += 1;
      applyFrame(state.frames[state.frameIndex], true);
    }

    function animateNextFrame() {
      if (!state.playing) return;
      if (isComplete()) {
        stop();
        return;
      }

      if (state.frameIndex < 0) {
        state.frameIndex = 0;
        applyFrame(state.frames[0], true);
        window.setTimeout(animateNextFrame, reducedMotion.matches ? 120 : 260);
        return;
      }

      const next = state.frames[state.frameIndex + 1];
      const from = state.time;
      const animationDuration = reducedMotion.matches ? 0 : 420;
      const startedAt = performance.now();

      function tick(now) {
        if (!state.playing) return;
        const amount = animationDuration === 0
          ? 1
          : Math.min(1, (now - startedAt) / animationDuration);
        state.visualTime = from + (next.time - from) * amount;
        renderScenario(clusterSvg, state.cluster, state);
        renderScenario(proxySvg, state.proxy, state);
        if (amount < 1) {
          state.animationFrame = requestAnimationFrame(tick);
          return;
        }
        state.animationFrame = null;
        state.frameIndex += 1;
        applyFrame(next, true);
        if (isComplete()) stop();
        else window.setTimeout(animateNextFrame, reducedMotion.matches ? 90 : 120);
      }

      state.animationFrame = requestAnimationFrame(tick);
    }

    function togglePlay() {
      if (state.playing) {
        stop();
        status.textContent = `Paused at time ${state.time} with ${state.cluster.active.size} active requests.`;
        return;
      }
      if (isComplete()) return;
      state.playing = true;
      buttons.play.textContent = "Pause";
      buttons.play.setAttribute("aria-pressed", "true");
      status.textContent = "Playing the seeded workload.";
      animateNextFrame();
    }

    function showResult() {
      stop();
      while (!isComplete()) {
        state.frameIndex += 1;
        applyFrame(state.frames[state.frameIndex], false);
      }
      state.lastFrame = state.frames[state.frameIndex];
      state.visualTime = state.time;
      status.textContent =
        "Complete. ClusterIP used 4 of 10 pods; the HTTP proxy used all 10 evenly.";
      render();
    }

    function reset() {
      stop();
      state.cluster = freshRuntime();
      state.proxy = freshRuntime();
      state.frameIndex = -1;
      state.time = 0;
      state.visualTime = 0;
      state.lastFrame = null;
      status.textContent = "Connections are established. Step or play to dispatch requests.";
      render();
    }

    buttons.step.addEventListener("click", step);
    buttons.play.addEventListener("click", togglePlay);
    buttons.result.addEventListener("click", showResult);
    buttons.reset.addEventListener("click", reset);
    render();
  }

  document.querySelectorAll("[data-routing-comparison]").forEach(initializeComparison);
})();
