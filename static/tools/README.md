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

## Create tools in ChatGPT

The reusable instructions live in `skills/standalone-tool-html/SKILL.md` at the
repository root. Its starter carries the complete theme, so generating a tool
does not require repository access. `skill-artifacts/standalone-tool-html.md`
is a single attachment for a normal ChatGPT conversation; the ZIP beside it
contains the conventional skill folder, starter, and optional HTML checker.
Attaching the guide gives that conversation the instructions; it does not
install an account-wide skill.

After changing the shared theme or skill sources, refresh the exports:

```sh
python3 scripts/package-tool-skill.py
python3 scripts/package-tool-skill.py --check
```

Generated pages retain the shared theme markers and catalog metadata. Copy a
finished `.html` into this directory when it is useful enough to keep. If it
carries an older theme snapshot, run the theme sync command above before building.
