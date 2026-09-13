# Standalone tool theme

All five tools use the site's warm surfaces, serif headings, teal controls, and
light/dark palette. Their shared theme is embedded in each HTML file, so copying
or downloading a tool does not require the rest of this repository.

Edit `assets/css/standalone-tools.css` and `assets/js/standalone-tools.js`, then run:

```sh
python3 scripts/sync-tool-theme.py
python3 scripts/sync-tool-theme.py --check
```

Keep tool-specific layouts in each HTML file, outside the generated theme markers.
Use the `--tool-*` variables for surfaces, text, borders, and semantic colors.
The theme selector shares the site's `theme` preference and supports system mode;
it also works when browser storage is unavailable.

The map tools still need their public Leaflet/Chart.js dependencies and map tiles.
The routing simulator, packet visualizer, and TOGG comparison work offline.
