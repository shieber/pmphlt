# Site Management Instructions

Practical reference for managing *The Occasional Pamphlet* Jekyll site.

---

## Table of Contents

1. [Local Development](#local-development)
2. [Adding a Post](#adding-a-post)
3. [Editing a Post](#editing-a-post)
4. [Deleting a Post](#deleting-a-post)
5. [Tags](#tags)
6. [Images](#images)
7. [Comments](#comments)
8. [Deploying to GitHub Pages](#deploying-to-github-pages)
9. [Special Post Types](#special-post-types)
10. [Maintenance Scripts](#maintenance-scripts)

---

## Local Development

Start the local server to preview changes before pushing:

```bash
bundle exec jekyll serve
```

Then visit `http://localhost:4000`. The server watches for file changes and rebuilds automatically (except for changes to `_config.yml`, which require a restart).

To do a one-time build without serving:

```bash
bundle exec jekyll build
```

---

## Adding a Post

### 1. Create the file

Create a new Markdown file in `_posts/` using the naming convention:

```
YYYY-MM-DD-slug-title.md
```

The slug portion becomes the URL path. For example, `2025-07-18-my-new-post.md` will be published at `https://occasionalpamphlet.com/2025/07/18/my-new-post/`.

### 2. Write the front matter

Every post must begin with a YAML front matter block:

```yaml
---
layout: post
title: "Your Post Title"
date: 2025-07-18 09:00:00 -04:00
tags: [scholarly-communication, open-access]
---
```

**Front matter fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `layout` | Yes | Always `post` |
| `title` | Yes | Display title (can include punctuation) |
| `date` | Yes | Publication date and time with timezone offset |
| `tags` | No | List of tags (see [Tags](#tags) below) |
| `comments` | No | Set to `false` to disable comments entirely for this post |
| `comments_always_open` | No | Set to `true` to keep comments open regardless of post age |

### 3. Write the content

After the closing `---` of the front matter, write your post in Markdown. To control what appears in the post excerpt/preview on the home page, insert the `<!--more-->` separator at the desired cut-off point:

```markdown
Opening paragraph that will appear in the preview.

<!--more-->

The rest of the post, which appears only on the full post page.
```

If no `<!--more-->` is present, an automatic 50-word excerpt is used.

### 4. Generate tag pages (if using new tags)

If your post uses any tags that don't already have a page in `_tags/`, run:

```bash
python scripts/generate_tag_pages.py
```

See [Tags](#tags) for details.

---

## Staging an Unlisted Post

To put up a post that is reachable by URL but hidden from all listings (home page, feed, tag pages), place it in `_unlisted/` instead of `_posts/`.

Use the same filename format and front matter as a normal post:

```
_unlisted/2025-07-18-my-draft-post.md
```

```yaml
---
layout: post
title: "My Draft Post"
date: 2025-07-18 09:00:00 -04:00
tags: [scholarly-communication]
---
```

The post will be built and accessible at its normal URL (e.g., `/2025/07/18/my-draft-post/`) but will not appear on the home page, in the RSS feed, or on any tag page.

When you are ready to publish it, simply move the file from `_unlisted/` to `_posts/` and push.

## Editing a Post

Open the relevant file in `_posts/` and edit directly. The filename determines the URL, so **do not rename the file** unless you intend to change the URL (which would break any Giscus comment threads attached to that URL).

If you must change a URL, add a redirect in `_redirects` to preserve incoming links.

---

## Deleting a Post

Simply delete the file from `_posts/`. If the post had Giscus comments, the associated GitHub Discussion in the `shieber/pmphlt` repository will remain but will no longer be linked from the site. You may optionally delete or close it manually in the GitHub Discussions interface.

---

## Tags

### Using existing tags

Add tag names to the `tags` list in a post's front matter. Use the human-readable tag name (not the slug):

```yaml
tags: [scholarly communication, open access, language]
```

Note that tag names with spaces are fine in the front matter — they are automatically slugified for URLs.

**Current tags:**

- alan-turing
- arxiv
- code
- computational-linguistics
- computer-science
- editing
- groundtruth *(reserved — see [Special Post Types](#special-post-types))*
- guest-post
- harry-lewis
- language
- lewis-carroll
- libraries
- meta
- moderation
- open-access
- other
- policy
- politics
- scholarly-communication
- syntax
- typesetting
- writing

### Adding a new tag

1. Add the new tag name to the post's front matter `tags` list.
2. Run the tag page generator:
   ```bash
   python scripts/generate_tag_pages.py
   ```
   This creates a new file in `_tags/` for the tag, which produces the tag index page at `/tags/your-new-tag/`.
3. Commit both the post and the new file in `_tags/`.

You can also create a tag page manually by adding a file to `_tags/`. For example, `_tags/my-new-tag.md`:

```yaml
---
layout: tag
tag: my new tag
title: "Posts tagged with 'my new tag'"
permalink: /tags/my-new-tag/
---
```

---

## Images

Store images in `assets/` organized by year and month:

```
assets/2025/07/my-image.png
```

Reference them in posts using a root-relative path:

```markdown
![Alt text](/assets/2025/07/my-image.png)
```

For images with captions and attribution, use the semantic HTML figure format:

```html
<figure>
  <img src="/assets/2025/07/my-image.png" alt="Alt text">
  <figcaption>
    <span class="caption-text">Caption describing the image.</span>
    <span class="caption-source">Source: <a href="https://example.com">Author Name</a></span>
  </figcaption>
</figure>
```

To wrap text around an image, add the `wrapped-image` class:

```html
<figure class="wrapped-image">
  ...
</figure>
```

---

## Comments

The site has two layers of comments:

### Archived WordPress comments

Posts that had comments on the original WordPress site display them in a styled "Archived Comments" block. These are stored as YAML files in `_data/comments/`, named by post slug (e.g., `_data/comments/2015-09-28-whence-function-notation.yml`).

These files are loaded automatically by `_layouts/post.html` — no post front matter changes are needed.

**To add or edit an archived comment**, edit the relevant YAML file in `_data/comments/`. The format is:

```yaml
wordpress_comments:
- author: Author Name
  date: '2015-09-29 14:59:09'
  content: |
    Comment text here. Markdown is supported.
- author: Another Author
  date: '2015-09-30 08:00:00'
  content: Another comment.
```

### New comments (Giscus)

New comments use [Giscus](https://giscus.app), which stores comments as GitHub Discussions in the `shieber/pmphlt` repository. Commenters must have a GitHub account to post.

**Moderating comments:**
- Go to the [Discussions tab](https://github.com/shieber/pmphlt/discussions) of the repository.
- Each post's comment thread is a separate Discussion. You can edit, delete, hide, or lock individual comments there.

**Deleting a comment:**
- Open the GitHub Discussion linked to the post.
- Click the `...` menu on the comment and select Delete.

**Closing comments on a post:**
Add `comments: false` to the post's front matter. Archived WordPress comments will still be displayed; only the Giscus widget will be hidden.

```yaml
---
layout: post
title: "My Post"
date: 2022-07-25 08:00:00 -04:00
tags: [scholarly-communication]
comments: false
---
```

**Keeping comments permanently open:**
By default, comments will eventually be closed for old posts (when the age limit in `_layouts/post.html` is restored). To keep a specific post's comments open indefinitely regardless of age:

```yaml
comments_always_open: true
```

---

## Deploying to GitHub Pages

The site is hosted on GitHub Pages at `https://occasionalpamphlet.com`.

### Typical workflow

1. Make and test your changes locally (`bundle exec jekyll serve`).
2. Commit the changes:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```
3. Push to GitHub:
   ```bash
   git push
   ```
   GitHub Pages will rebuild and publish the site automatically within a minute or two.

### What to commit

Always commit:
- New or edited post files (`_posts/`)
- Any new tag pages (`_tags/`)
- New or edited comment data files (`_data/comments/`)
- Any layout, include, or CSS changes
- New images (`assets/`)

Do **not** commit:
- The `_site/` directory (it is in `.gitignore` and is rebuilt by GitHub Pages)

---

## Special Post Types

### Ground Truth posts

Posts migrated from the predecessor blog *The Ground Truth* are tagged `groundtruth`:

```yaml
tags: [groundtruth, language]
```

This tag causes the post to render with a pale yellow background to distinguish it visually from main blog posts.

### Guest posts

Tag guest posts with `guest-post`. There is no special visual treatment beyond the tag appearing in the tag list.

---

## Maintenance Scripts

All scripts are in the `scripts/` directory and require Python 3.

### Tag management

```bash
python scripts/generate_tag_pages.py
```
Scans all posts and generates any missing tag pages in `_tags/`. Safe to run at any time; it does not overwrite existing tag files.

### WordPress comment extraction

```bash
# Dry run (no files written):
python scripts/extract_wordpress_comments.py --dry-run

# Actually extract (writes YAML files to _data/comments/):
python scripts/extract_wordpress_comments.py
```

Reads from the WordPress XML export file and creates one YAML file per post that has comments. Run the dry run first to verify what will be created.

### Image maintenance

```bash
# Find posts referencing images that don't exist locally:
python scripts/find_missing_images.py

# Attempt to retrieve missing images from the Wayback Machine:
python scripts/download_from_wayback_simple.py
```

### Content analysis (informational only, no file changes)

```bash
python scripts/word_frequency.py
python scripts/topic_analysis.py
python scripts/semantic_clustering.py
```
