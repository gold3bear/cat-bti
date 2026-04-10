# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CAT-BTI is a single-page web application - a cat personality test/quiz. The project is a mirror of a Bilibili creator's original work.

## Architecture

- **Single HTML file**: `index.html` - contains all HTML, CSS, and JavaScript inline
- **Static assets**: `image/` directory contains cat-related images used in the quiz
- **No build system**: This is a vanilla HTML/CSS/JS project that runs directly in a browser

## Development

No build commands needed - open `index.html` directly in a browser, or serve with any static file server:

```bash
# Python simple server
python -m http.server 8000

# Node http-server
npx http-server .
```

## Testing

No test framework is configured for this project.

## Adding New Cat Images

Place new images in the `image/` directory and reference them in `index.html` by their filename (e.g., `image/NEW-CAT.png`).
