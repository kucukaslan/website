# kucukaslan.com.tr

Personal website of Muhammed Can Küçükaslan, built with [Hugo](https://gohugo.io/).

## Overview

A static site with custom layouts — no theme dependency. Content lives in Markdown under `content/`, and the built site outputs to `public/` (deployed via GitHub Actions to GitHub Pages).

## Project Structure

```
website/
├── archetypes/          # Content templates for new pages
├── assets/              # CSS/JS processed by Hugo's asset pipeline
├── content/
│   ├── _index.md        # Homepage
│   ├── about.md         # Standalone About page
│   ├── languages/       # Static language-filtered writing views
│   └── posts/           # Published writing, drafts, and series members
├── layouts/             # Templates, partials, shortcodes
├── static/              # Static assets (CSS, images, JS)
├── public/              # Build output (gitignored)
└── config.toml          # Hugo configuration
```

## Prerequisites

- [Hugo Extended](https://gohugo.io/installation/) (recommended)
- Git

## Development

```bash
# Build the site
hugo --minify

# Preview locally
hugo server --buildDrafts

# Include drafts in build
hugo --buildDrafts
```

Visit `http://localhost:1313` when running the dev server.

Internal navigation and local assets use origin-relative URLs, so the same
server can also be exposed through a forwarded hostname. Keep the production
`baseURL` in `config.toml`; do not override it with a localhost URL when
starting a forwarded preview.

## Content

- **Writing** goes in `content/posts/` — use the `url` frontmatter field to preserve existing URLs when moving files.
- Add `language` (`en`, `tr`, or `ku`) and `content_type` (`technical`, `opinion`, `culture`, or `site-note`) to published writing.
- Use optional `series` metadata for related articles; series pages appear when they contain published writing.
- Standalone pages use `layout: page` and are excluded from writing lists and article metadata.
- **Drafts** are excluded from production builds unless `--buildDrafts` is passed.

## Deployment

Pushes to `main` trigger `.github/workflows/deploy.yml`, which builds with Hugo Extended and deploys to GitHub Pages via `actions/deploy-pages`.

To deploy manually:

1. Enable GitHub Pages with source set to **GitHub Actions** in repository settings.
2. Merge to `main` — the workflow handles the rest.

## Customization

| What | Where |
|------|-------|
| Styles | `static/style.css` |
| Layouts | `layouts/` |
| Navigation | `config.toml` → `[menu.main]` |
| Site metadata | `config.toml` → `[params]` |
| Open Graph / Twitter Cards | `layouts/partials/opengraph.html` |

## Features

- Editorial typography (CMU Serif, Cormorant Garamond, DM Sans, JetBrains Mono)
- Light/dark mode with `localStorage` persistence and `prefers-color-scheme` fallback
- RSS feed at `/index.xml`
- `robots.txt` at `/robots.txt` (origin file in `static/`; Cloudflare may prepend its managed AI-crawler policy)
- `llms.txt` at `/llms.txt` (AI crawler context; served from `static/llms.txt`)
- Open Graph and Twitter Card meta tags (X: [@kucukaslancomtr](https://x.com/kucukaslancomtr))
- Tag pages at `/tags/`
- Mermaid diagram support
- Lazy-loaded YouTube embeds on song pages
- Chroma syntax highlighting
