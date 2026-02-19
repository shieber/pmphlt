#!/usr/bin/env python3
"""
WordPress to Jekyll Migration Script

This script converts WordPress XML export files to Jekyll blog posts.
It preserves metadata, content, and handles image attachments.
"""

import xml.etree.ElementTree as ET
import re
import os
import sys
from datetime import datetime
from pathlib import Path
import html
from urllib.parse import urlparse, unquote

class WordPressToJekyll:
    def __init__(self, xml_file, output_dir="_groundtruth", dry_run=False):
        self.xml_file = xml_file
        self.output_dir = Path(output_dir)
        self.dry_run = dry_run
        self.namespaces = {
            'content': 'http://purl.org/rss/1.0/modules/content/',
            'excerpt': 'http://wordpress.org/export/1.2/excerpt/',
            'wp': 'http://wordpress.org/export/1.2/',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }
        
        # Create output directory if it doesn't exist
        if not self.dry_run:
            self.output_dir.mkdir(exist_ok=True)
    
    def parse_xml(self):
        """Parse the WordPress XML export file."""
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
            return root
        except ET.ParseError as e:
            print(f"Error parsing XML file: {e}")
            return None
    
    def extract_posts(self, root):
        """Extract all posts from the XML."""
        posts = []
        
        # Find all item elements
        for item in root.findall('.//item'):
            post_type = item.find('wp:post_type', self.namespaces)
            
            # Only process actual posts, not attachments or pages
            if post_type is not None and post_type.text == 'post':
                post = self.parse_post(item)
                if post:
                    posts.append(post)
        
        return posts
    
    def parse_post(self, item):
        """Parse a single post item."""
        try:
            # Extract basic metadata
            title = item.find('title')
            title_text = title.text if title is not None else "Untitled"
            
            # Extract date
            post_date = item.find('wp:post_date', self.namespaces)
            if post_date is None or not post_date.text:
                return None
            
            # Parse date
            try:
                date_obj = datetime.strptime(post_date.text, '%Y-%m-%d %H:%M:%S')
                date_str = date_obj.strftime('%Y-%m-%d %H:%M:%S.000000000 -04:00')
            except ValueError:
                print(f"Warning: Could not parse date for post '{title_text}'")
                return None
            
            # Extract content
            content_elem = item.find('content:encoded', self.namespaces)
            content = content_elem.text if content_elem is not None else ""
            
            # Extract categories and tags (convert categories to tags)
            tags = []
            
            for category in item.findall('category'):
                domain = category.get('domain', '')
                if domain == 'category':
                    cat_name = category.text
                    if cat_name and cat_name != 'Uncategorized':
                        tags.append(cat_name)
                elif domain == 'post_tag':
                    tag_name = category.text
                    if tag_name:
                        tags.append(tag_name)
            
            # Add the "groundtruth" tag to all posts
            tags.append('groundtruth')
            
            # Extract author
            creator = item.find('dc:creator', self.namespaces)
            author = creator.text if creator is not None else "shieber"
            
            # Extract post name for filename
            post_name = item.find('wp:post_name', self.namespaces)
            slug = post_name.text if post_name is not None else self.slugify(title_text)
            
            # Extract status
            status = item.find('wp:status', self.namespaces)
            post_status = status.text if status is not None else "publish"
            
            # Skip drafts and private posts
            if post_status not in ['publish', 'inherit']:
                return None
            
            return {
                'title': title_text,
                'date': date_str,
                'content': content,
                'tags': tags,
                'author': author,
                'slug': slug,
                'status': post_status
            }
            
        except Exception as e:
            print(f"Error parsing post: {e}")
            return None
    
    def slugify(self, text):
        """Convert title to URL-friendly slug."""
        # Remove special characters and convert to lowercase
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        # Replace spaces and hyphens with single hyphens
        slug = re.sub(r'[-\s]+', '-', slug)
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        return slug
    
    def clean_content(self, content):
        """Clean and format the post content."""
        if not content:
            return ""
        
        # Decode HTML entities
        content = html.unescape(content)
        
        # Convert WordPress shortcodes and formatting
        content = self.convert_wordpress_formatting(content)
        
        return content
    
    def convert_wordpress_formatting(self, content):
        """Convert WordPress-specific formatting to standard HTML."""
        # Convert WordPress gallery shortcodes (basic handling)
        content = re.sub(r'\[gallery.*?\]', '', content)
        
        # Convert WordPress embed shortcodes
        content = re.sub(r'\[embed\](.*?)\[/embed\]', r'\1', content)
        
        # Convert WordPress caption shortcodes
        content = re.sub(r'\[caption.*?\](.*?)\[/caption\]', r'\1', content)
        
        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        return content
    
    def generate_front_matter(self, post):
        """Generate Jekyll front matter for a post."""
        front_matter = f"""---
layout: post
title: {post['title']}
date: {post['date']}
type: post
parent_id: '0'
published: true
password: ''
status: publish
comments: false
"""
        
        # Add tags if any
        if post['tags']:
            front_matter += f"tags:\n"
            for tag in post['tags']:
                front_matter += f"- {tag}\n"
        

        
        # Add author information
        front_matter += f"""meta:
  _edit_last: '2110'
author:
  login: {post['author']}
  email: shieber@seas.harvard.edu
  display_name: Stuart Shieber
  first_name: Stuart
  last_name: Shieber
---
"""
        return front_matter
    
    def generate_filename(self, post):
        """Generate filename for the post."""
        date_obj = datetime.strptime(post['date'], '%Y-%m-%d %H:%M:%S.000000000 -04:00')
        date_prefix = date_obj.strftime('%Y-%m-%d')
        
        # Use slug if available, otherwise slugify title
        slug = post['slug'] if post['slug'] else self.slugify(post['title'])
        
        return f"{date_prefix}-{slug}.html"
    
    def write_post(self, post):
        """Write a post to file."""
        filename = self.generate_filename(post)
        filepath = self.output_dir / filename
        
        # Check if file already exists
        if filepath.exists() and not self.dry_run:
            print(f"Warning: File {filename} already exists, skipping...")
            return False
        
        # Generate content
        front_matter = self.generate_front_matter(post)
        content = self.clean_content(post['content'])
        
        full_content = front_matter + content
        
        if self.dry_run:
            print(f"Would create: {filename}")
            print(f"Title: {post['title']}")
            print(f"Date: {post['date']}")
            print(f"Tags: {post['tags']}")
            print("\nFront matter:")
            print(front_matter)
            print("Content preview:")
            # Show first 200 characters of content, truncated at word boundary
            content_preview = content[:200]
            if len(content) > 200:
                last_space = content_preview.rfind(' ')
                if last_space > 150:  # Only truncate if we can find a reasonable break point
                    content_preview = content_preview[:last_space] + "..."
                else:
                    content_preview += "..."
            print(content_preview)
            print("-" * 50)
            return True
        else:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(full_content)
                print(f"Created: {filename}")
                return True
            except Exception as e:
                print(f"Error writing {filename}: {e}")
                return False
    
    def migrate(self):
        """Main migration function."""
        print(f"Starting WordPress to Jekyll migration...")
        print(f"Input file: {self.xml_file}")
        print(f"Output directory: {self.output_dir}")
        print(f"Dry run: {self.dry_run}")
        print("-" * 50)
        
        # Parse XML
        root = self.parse_xml()
        if root is None:
            print("Failed to parse XML file")
            return False
        
        # Extract posts
        posts = self.extract_posts(root)
        print(f"Found {len(posts)} posts to migrate")
        
        if not posts:
            print("No posts found to migrate")
            return False
        
        # Process each post
        successful = 0
        for post in posts:
            if self.write_post(post):
                successful += 1
        
        print("-" * 50)
        print(f"Migration complete: {successful}/{len(posts)} posts processed successfully")
        
        return successful > 0

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate WordPress XML export to Jekyll posts')
    parser.add_argument('xml_file', help='WordPress XML export file')
    parser.add_argument('--output-dir', default='_groundtruth', help='Output directory for posts (default: _groundtruth)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be created without writing files')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.xml_file):
        print(f"Error: Input file '{args.xml_file}' not found")
        sys.exit(1)
    
    # Create migrator and run
    migrator = WordPressToJekyll(args.xml_file, args.output_dir, args.dry_run)
    success = migrator.migrate()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 