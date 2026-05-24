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
│   ├── posts/           # Blog posts
│   ├── pages/           # Standalone pages (About, etc.)
│   ├── songs/           # Kurdish song collections
│   └── tcp/             # TCP/HTTP series
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

## Content

- **Posts** go in `content/posts/` — use the `url` frontmatter field to preserve existing URLs when moving files.
- **Pages** go in `content/pages/` (e.g. About at `/about/`).
- **Songs** go in `content/songs/` with `layout: stran` for YouTube embed support.
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
