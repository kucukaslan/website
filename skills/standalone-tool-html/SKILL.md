---
name: standalone-tool-html
description: Create polished, portable single-file HTML tools, calculators, simulators, and visualizers that match kucukaslan.com.tr and can later be copied into its tools catalog. Use for downloadable standalone HTML, not multi-file apps, Hugo templates, or publishing a website.
---

# Standalone tool HTML

Produce a complete, working `.html` artifact for the user's immediate task. The
user may later copy that same file into `static/tools/` on kucukaslan.com.tr.
Creation requires no access to the website repository. Do not add the page to the
website or publish it unless asked.

## Start from the bundled theme

Read [assets/starter.html](assets/starter.html) and adapt it. If these instructions
arrive as a single chat attachment, the same starter is included at the end.
Keep the complete `standalone-theme:start` through `standalone-theme:end` block
unchanged. It contains the shared CSS and the theme controller. Add all
tool-specific CSS and JavaScript outside that block.

Replace the starter's title, description, topic, main content, and behavior with
the requested tool. Use the user's language for visible copy and the HTML `lang`
attribute; translate the navigation and theme option labels while preserving
their IDs and option values. The layout is a starting point, not a requirement
to present every tool as a form or dashboard.

The visual identity is warm paper, charcoal text, and teal controls with restrained
serif headings. Use the supplied `--tool-*` tokens and local font stacks. Useful
classes include `tool-header`, `tool-kicker`, `tool-description`, `tool-panel`,
`tool-button`, and `tool-help`. Keep the main interaction easy to reach. Let maps,
diagrams, tables, and results carry the page; do not add decorative metrics or
sales copy. Use `--tool-blue`, `--tool-orange`, `--tool-violet`, and `--tool-red`
with their `-soft` surfaces when different data states need distinct colors.

## Portability and catalog contract

- Return one UTF-8 HTML document with a doctype, language, early charset
  declaration, viewport meta tag, one meaningful `h1`, and a useful document title.
- Include exactly `<meta name="description" content="...">`, with `name` before
  `content` and no intervening attributes. The catalog parses this shape. HTML
  escape attribute values; encode embedded apostrophes as `&#39;` and double
  quotes as `&quot;` because the current catalog parser rejects raw quote characters.
- Use a descriptive lowercase filename, such as `connection-pool-calculator.html`.
  The catalog derives the tool name and summary from the HTML metadata; it needs
  no Markdown wrapper, frontmatter, registration file, or Hugo shortcode.
- Embed application CSS, JavaScript, and required data. Avoid relative or
  origin-relative asset paths, sibling files, local fetches, package imports,
  service workers, build commands, and runtime dependencies on ChatGPT's preview.
  The saved document should open directly from disk and from a static host.
- Prefer native browser APIs and inline SVG or canvas. A public HTTPS CDN library
  or live map service is acceptable when it materially helps the tool; pin library
  versions where practical and state the internet requirement. An offline request
  means no external runtime resources at all. Navigation links alone do not make
  a tool internet-dependent.
- Preserve the absolute site links, `tool-theme` selector, `tool-content` target,
  and `tool-page` body class. The theme controller supports system/light/dark,
  shares the site's `theme` preference, and tolerates unavailable browser storage.
  Additional persistence must be optional and use a tool-specific key.
- If a chart or canvas caches colors, listen for `tool-theme-change` and redraw
  using the resolved theme tokens. Do not reset the user's inputs on a theme change.

## Implement the actual tool

Use realistic initial values and make the primary action immediately understandable.
Validate relevant ranges and inputs, explain errors beside the affected control,
and preserve input after errors. For simulations, state assumptions and keep
illustrative behavior distinguishable from measured results. Do not invent data
to make a chart appear convincing.

Keep labels programmatically associated with inputs, visible keyboard focus,
meaningful button names, and readable light/dark states. At phone widths, contain
wide tables and diagrams in labelled, keyboard-accessible scrolling regions rather
than widening the whole document. Wrap long logs and hex data, and present long
numbers without splitting their digits. Respect reduced motion in both CSS and
JavaScript-driven animation. Treat pasted logs, JSON, and labels as data; use
`textContent` or escape text instead of inserting user input as HTML.

## Check and deliver

If execution is available, run `python3 scripts/check_html.py OUTPUT.html` relative
to this skill folder. This checks static portability and catalog compatibility;
it does not prove runtime behavior or detect every dependency created in JavaScript.
Without execution, review the same contract directly.

If browser tools are available, exercise the main interaction, an invalid or empty
input, theme switching, and a narrow viewport. Check direct-file loading when the
environment permits it. State any material verification limits; do not claim a
browser or offline test you could not run. A preview restriction is not a reason
to turn the deliverable into a hosted or multi-file application.

Deliver a downloadable HTML file when possible. Otherwise return the entire
document in one HTML code block, without omitted sections or separate CSS/JS files.
Briefly name the file, explain its use, and mention any online dependency.

The user can later copy the file into `static/tools/`. A page made from this
starter matches the bundled theme snapshot. If the website's theme has changed
since this skill was exported, `python3 scripts/sync-tool-theme.py` in the website
refreshes the embedded theme before its consistency check and build.
