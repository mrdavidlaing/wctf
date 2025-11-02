# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal website built with Hugo static site generator using the Hugo Theme Console. The site is configured as a profile-style homepage featuring a personal introduction, resume/CV, and professional links.

## Prerequisites

- Hugo (static site generator)
- Go 1.20+ (required by Hugo modules)

## Development Commands

### Local Development
```bash
make serve
# OR
hugo server -D --bind 0.0.0.0
```
Starts development server with drafts enabled on all interfaces, typically on http://localhost:1313

### Building for Production
```bash
make build
# OR
hugo --minify
```
Generates minified static files in the `public/` directory

### Cleaning Build Artifacts
```bash
make clean
```
Removes the `public/` directory

### Creating New Content
```bash
hugo new content/posts/new-post.md
```
Creates new content using the archetype template

## Site Architecture

### Configuration Structure
The site uses Hugo's modular configuration approach with files in `config/_default/`:

- **config.toml**: Base site configuration including baseURL, outputs, module imports, and SEO metadata
- **params.toml**: Hugo Theme Console parameters including navigation links and styling options
- **module.toml**: Hugo module imports for the console theme

### Theme Details
- Uses `github.com/mrmierzejewski/hugo-theme-console` theme (not Congo as mentioned in old docs)
- Profile-style layout with fade-up animations
- Console/terminal aesthetic
- Navigation includes resume/cv, GitHub, and LinkedIn links

### Content Architecture
- **content/_index.md**: Homepage with centered profile layout, bitmoji image, and social links
- **content/resume/index.md**: Resume page that displays JSON Resume format and links to external HTML version
- **static/resume.json**: JSON Resume schema-compliant resume data
- **archetypes/default.md**: Template for new content with TOML frontmatter

### Custom Components
- **layouts/shortcodes/readfile.html**: Custom shortcode that reads and syntax-highlights files (used to display resume.json)
- **layouts/index.json**: JSON output format for the homepage

### Static Assets
- **static/images/**: Profile images and media files
- **static/resume.json**: Resume data in JSON Resume format
- **static/_headers**: Netlify headers configuration