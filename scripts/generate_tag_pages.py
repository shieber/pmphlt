#!/usr/bin/env python3

import os
import re
import glob
from pathlib import Path
import yaml

def extract_front_matter(content):
    """Extract YAML front matter from a Jekyll post."""
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            return content[3:end].strip()
    return None

def main():
    # Create _tags directory if it doesn't exist
    tags_dir = Path('_tags')
    tags_dir.mkdir(exist_ok=True)
    
    # Get all posts and extract tags from _posts and _unlisted directories
    posts_dirs = [Path('_posts'), Path('_unlisted')]
    posts = []
    for posts_dir in posts_dirs:
        if posts_dir.exists():
            posts.extend(list(posts_dir.glob('*.md')) + list(posts_dir.glob('*.html')))
    
    all_tags = set()
    for post_file in posts:
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()
        front_matter = extract_front_matter(content)
        if front_matter:
            try:
                data = yaml.safe_load(front_matter)
                tags = data.get('tags', [])
                if isinstance(tags, str):
                    # Handle comma-separated string
                    tags = [t.strip() for t in tags.split(',')]
                elif not isinstance(tags, list):
                    tags = []
                all_tags.update([t for t in tags if t])
            except Exception as e:
                print(f"Warning: Could not parse YAML in {post_file}: {e}")
    all_tags = sorted(all_tags)
    
    # Generate tag pages in _tags/
    for tag in all_tags:
        tag_slug = re.sub(r'[^a-z0-9]+', '-', tag.lower()).strip('-')
        tag_file = tags_dir / f"{tag_slug}.md"
        tag_content = f"""---
layout: tag
tag: {tag}
title: "Posts tagged with '{tag}'"
permalink: /tags/{tag_slug}/
---"""
        with open(tag_file, 'w', encoding='utf-8') as f:
            f.write(tag_content)
        print(f"Generated tag page: {tag_file}")
    print(f"Generated {len(all_tags)} tag pages")

if __name__ == '__main__':
    main() 