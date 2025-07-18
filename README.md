# The Occasional Pamphlet

A Jekyll-based blog about scholarly communication and other topics, maintained by Stuart Shieber.

## About

This is the source code for [The Occasional Pamphlet](https://occasionalpamphlet.com), a blog focused on scholarly communication, open access, academic publishing, and related topics. The blog is built using Jekyll and is based on the Lanyon theme.

### Blog Integration

This site integrates content from two blogs:
- **The Occasional Pamphlet** - The main blog (2009-present)
- **The Ground Truth** - A previous WordPress blog (2004-2015) that has been migrated and integrated

Posts from The Ground Truth are tagged with "groundtruth" and styled distinctively to distinguish them from the main blog posts while maintaining a unified reading experience.

## Site Structure

- **`_posts/`** - Blog posts (dating back to 2009)
- **`_pages/`** - Static pages (About, License, Policies)
- **`_layouts/`** - Jekyll layout templates
- **`_includes/`** - Reusable HTML components
- **`_attachments/`** - WordPress attachment pages (legacy)
- **`assets/`** - Images and other static assets organized by year
- **`scripts/`** - Python utilities for site maintenance and analysis
- **`public/`** - Compiled CSS, JS, and other static files

## Development Setup

### Prerequisites

- Ruby (with Bundler)
- Jekyll

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/shieber/pmphlt.git
   cd pmphlt
   ```

2. Install dependencies:
   ```bash
   bundle install
   ```

3. Start the development server:
   ```bash
   bundle exec jekyll serve
   ```

4. Visit `http://localhost:4000` to view the site

## Scripts

The `scripts/` directory contains various Python utilities for site maintenance:

### Content Analysis
- **`word_frequency.py`** - Analyze word frequency across blog posts
- **`topic_analysis.py`** - Perform topic clustering on blog content
- **`semantic_clustering.py`** - Advanced semantic analysis of posts

### Image Management
- **`find_missing_images.py`** - Scan for missing images in posts
- **`download_from_wayback_simple.py`** - Download missing images from Wayback Machine

### Content Maintenance
- **`fix_figure_captions.py`** - Restore figure captions and attribution
- **`fix_redundant_captions.py`** - Remove duplicate caption text
- **`generate_tag_pages.py`** - Generate tag index pages
- **`unwrap_posts.py`** - Clean up post formatting
- **`fix_paragraph_breaks.py`** - Add paragraph tags to posts missing proper formatting
- **`migrate_wordpress_posts.py`** - Migration script for WordPress posts (reference only)

### Build
- **`build.sh`** - Build script for deployment

## Customization

### Theme
The site uses a customized version of the Lanyon Jekyll theme with:
- Hidden sidebar navigation
- Custom typography and spacing
- Semantic figure styling with captions
- Responsive design

### CSS Customizations
- Custom figure layouts with `wrapped-image` class
- Semantic caption styling (`.caption-text`, `.caption-source`)
- Custom link colors and typography
- Responsive image handling
- Ground Truth post styling (pale yellow background for posts tagged "groundtruth")

## Content Management

### Adding Posts
1. Create a new file in `_posts/` with the format `YYYY-MM-DD-title.md`
2. Include front matter with title, date, tags, etc.
3. Use markdown for content formatting
4. Images should be placed in `assets/YYYY/MM/` directory

### Tags
- Tags are automatically generated from post front matter
- Tag pages are created using `scripts/generate_tag_pages.py`
- Tag index is available at `/tags.html`
- Posts from The Ground Truth are tagged with "groundtruth" for identification

### Images
- Store images in `assets/` organized by year/month
- Use semantic `<figure>` elements with `<figcaption>` for captions
- Support for attribution and source links in captions

## Deployment

The site is configured for GitHub Pages deployment. The build process:
1. Generates tag pages
2. Compiles Jekyll site
3. Outputs to `_site/` directory

## License

See [LICENSE.md](LICENSE.md) for licensing information.

## Author

**Stuart Shieber**
- Blog: [The Occasional Pamphlet](https://occasionalpamphlet.com)
- Website: [stuartshieber.com](https://stuartshieber.com)
- GitHub: [@shieber](https://github.com/shieber)
