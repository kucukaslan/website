# Static Website Generator

This is a static website built with [Hugo](https://gohugo.io/), a fast and flexible static site generator written in Go.

## Overview

The website uses the **lugo** theme and generates static HTML files in the `docs/` directory, which can be served directly by a web server or deployed to static hosting services like GitHub Pages.

## Project Structure

```
website/
├── archetypes/          # Content templates for new pages
├── assets/              # CSS and JS assets (processed by Hugo)
├── content/             # Markdown content files (posts, pages)
├── docs/                # Generated static website (output directory)
├── layouts/             # Custom layout overrides for the theme
├── static/              # Static files copied directly to output (CSS, images, etc.)
├── themes/lugo/         # Hugo theme used for the site
└── config.toml          # Hugo configuration file
```

## Prerequisites

- [Hugo](https://gohugo.io/installation/) (extended version recommended)
- Git (for version control)

## How the Site is Generated

### 1. Content Files

All content is written in Markdown format and placed in the `content/` directory:
- Each `.md` file becomes a page or post
- Front matter (YAML/TOML) at the top defines metadata (title, date, tags, etc.)
- Hugo processes these Markdown files and converts them to HTML

### 2. Theme and Layouts

The site uses the **lugo** theme located in `themes/lugo/`. Custom layout overrides can be placed in the `layouts/` directory, which take precedence over theme layouts.

### 3. Static Files

Files in the `static/` directory (CSS, images, JavaScript, PDFs, etc.) are copied directly to the root of the output directory during generation.

### 4. Configuration

The `config.toml` file contains:
- Site metadata (title, base URL, language)
- Theme configuration
- Build settings (output directory set to `docs/`)
- Markup renderer settings

### 5. Generation Process

To generate the static website:

```bash
# Build the site (outputs to docs/ directory)
hugo

# Preview the site locally at http://localhost:1313
hugo server

# Build with drafts included
hugo --buildDrafts

# Build for production (excludes drafts and future-dated posts)
hugo --minify
```

The generated static files are output to the `docs/` directory (as configured in `config.toml` with `publishDir="docs"`).

## Development Workflow

1. **Create new content:**
   ```bash
   hugo new posts/my-new-post.md
   ```

2. **Edit content:**
   - Edit Markdown files in `content/`
   - Modify styles in `static/style.css`
   - Customize layouts in `layouts/`

3. **Preview changes:**
   ```bash
   hugo server
   ```
   Visit `http://localhost:1313` to see your changes live.

4. **Build for production:**
   ```bash
   hugo
   ```
   This generates the static site in the `docs/` directory.

5. **Deploy:**
   - Commit and push the `docs/` directory to your repository
   - If using GitHub Pages, ensure it's configured to serve from the `docs/` folder

## Key Features

- **Markdown-based content:** Easy to write and maintain
- **Fast generation:** Hugo is extremely fast at building static sites
- **Theme customization:** Override theme layouts without modifying the theme itself
- **Asset pipeline:** CSS and JS in `assets/` are processed and optimized
- **RSS feed:** Automatically generated at `/index.xml`
- **Tag system:** Posts can be tagged and related posts are linked
- **Dark mode:** Theme switcher for light/dark mode

## Customization

### Styles

The main stylesheet is located at `static/style.css`. This file is copied directly to the output directory and overrides the theme's default styles.

### Layouts

Custom layouts should be placed in the `layouts/` directory, mirroring the structure of the theme:
- `layouts/_default/` - Default page templates
- `layouts/page/` - Page-specific templates
- `layouts/partials/` - Reusable partial templates
- `layouts/shortcodes/` - Custom shortcodes

### Configuration

Edit `config.toml` to change:
- Site title and metadata
- Theme settings
- Output directory
- Build options

## Deployment

The generated static files in the `docs/` directory can be deployed to any static hosting service:

- **GitHub Pages:** Push `docs/` directory, configure Pages to serve from `/docs`
- **Netlify:** Connect repository, build command: `hugo`, publish directory: `docs`
- **Vercel:** Similar setup with `hugo` as build command
- **Any web server:** Simply upload the contents of `docs/` to your web server

## Resources

- [Hugo Documentation](https://gohugo.io/documentation/)
- [Hugo Themes](https://themes.gohugo.io/)
- [Markdown Guide](https://www.markdownguide.org/)


