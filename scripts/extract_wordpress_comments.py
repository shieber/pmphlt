#!/usr/bin/env python3
"""
WordPress Comment Extraction Script

This script extracts comments from a WordPress XML export and converts them
to YAML format for inclusion in Jekyll post front matter.
"""

import xml.etree.ElementTree as ET
import yaml
import re
import sys
from datetime import datetime
from pathlib import Path
import html

class WordPressCommentExtractor:
    def __init__(self, xml_file, dry_run=False):
        self.xml_file = xml_file
        self.dry_run = dry_run
        self.namespaces = {
            'content': 'http://purl.org/rss/1.0/modules/content/',
            'wp': 'http://wordpress.org/export/1.2/',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }
    
    def parse_xml(self):
        """Parse the WordPress XML export file."""
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
            return root
        except ET.ParseError as e:
            print(f"Error parsing XML file: {e}")
            return None
    
    def extract_comments(self, root):
        """Extract all comments from posts."""
        posts_with_comments = {}
        total_posts = 0
        posts_processed = 0
        
        # Find all item elements (posts)
        for item in root.findall('.//item'):
            post_type = item.find('wp:post_type', self.namespaces)
            
            if post_type is not None:
                total_posts += 1
                if self.dry_run and total_posts <= 5:
                    title_elem = item.find('title')
                    title = title_elem.text if title_elem is not None else 'Untitled'
                    print(f"   Found item: '{title}' (type: {post_type.text})")
            
            # Only process actual posts
            if post_type is not None and post_type.text == 'post':
                posts_processed += 1
                post_data = self.parse_post_comments(item)
                if post_data:
                    if self.dry_run:
                        print(f"   Post '{post_data['title']}' has {len(post_data['comments'])} comments")
                    if post_data['comments']:
                        posts_with_comments[post_data['slug']] = post_data
        
        if self.dry_run:
            print(f"\n📊 DIAGNOSTIC INFO:")
            print(f"   Total items found: {total_posts}")
            print(f"   Posts processed: {posts_processed}")
            print(f"   Posts with comments: {len(posts_with_comments)}")
        
        return posts_with_comments
    
    def parse_post_comments(self, item):
        """Parse comments for a specific post."""
        title_elem = item.find('title')
        title = title_elem.text if title_elem is not None else 'Untitled'
        
        slug_elem = item.find('wp:post_name', self.namespaces)
        slug = slug_elem.text if slug_elem is not None else self.slugify(title)
        
        date_elem = item.find('wp:post_date', self.namespaces)
        post_date = date_elem.text if date_elem is not None else ''
        
        # Extract comments
        comments = []
        comment_elements = item.findall('wp:comment', self.namespaces)
        
        if self.dry_run and comment_elements:
            print(f"     Found {len(comment_elements)} comment elements for '{title}'")
        
        for comment in comment_elements:
            comment_data = self.parse_comment(comment)
            if comment_data:
                comments.append(comment_data)
        
        # Sort comments by date
        comments.sort(key=lambda x: x['date'])
        
        return {
            'title': title,
            'slug': slug,
            'post_date': post_date,
            'comments': comments
        }
    
    def parse_comment(self, comment_elem):
        """Parse individual comment data."""
        # Skip spam or unapproved comments
        approved = comment_elem.find('wp:comment_approved', self.namespaces)
        if approved is not None and approved.text != '1':
            if self.dry_run:
                print(f"     Skipping unapproved comment (status: {approved.text})")
            return None
        
        comment_type = comment_elem.find('wp:comment_type', self.namespaces)
        if comment_type is not None and comment_type.text not in ['', 'comment']:
            if self.dry_run:
                print(f"     Skipping non-comment (type: {comment_type.text})")
            return None  # Skip trackbacks, pingbacks, etc.
        
        # Extract comment data
        author_elem = comment_elem.find('wp:comment_author', self.namespaces)
        author = author_elem.text if author_elem is not None else 'Anonymous'
        
        email_elem = comment_elem.find('wp:comment_author_email', self.namespaces)
        email = email_elem.text if email_elem is not None else ''
        
        url_elem = comment_elem.find('wp:comment_author_url', self.namespaces)
        url = url_elem.text if url_elem is not None else ''
        
        date_elem = comment_elem.find('wp:comment_date', self.namespaces)
        date = date_elem.text if date_elem is not None else ''
        
        content_elem = comment_elem.find('wp:comment_content', self.namespaces)
        content = content_elem.text if content_elem is not None else ''
        
        # Clean up content
        content = html.unescape(content)
        content = self.clean_comment_content(content)
        
        return {
            'author': author,
            'email': email,
            'url': url,
            'date': date,
            'content': content
        }
    
    def clean_comment_content(self, content):
        """Clean up comment content."""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = content.strip()
        
        # Convert basic HTML to markdown
        content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content)
        content = re.sub(r'<b>(.*?)</b>', r'**\1**', content)
        content = re.sub(r'<em>(.*?)</em>', r'*\1*', content)
        content = re.sub(r'<i>(.*?)</i>', r'*\1*', content)
        content = re.sub(r'<code>(.*?)</code>', r'`\1`', content)
        
        # Convert links
        content = re.sub(r'<a href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', content)
        
        # Remove other HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        return content
    
    def slugify(self, text):
        """Convert text to URL-friendly slug."""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')
    
    def generate_jekyll_filename(self, post_data):
        """Generate comment filename that matches Jekyll post naming."""
        # Parse the post date
        try:
            date_obj = datetime.strptime(post_data['post_date'], '%Y-%m-%d %H:%M:%S')
            date_prefix = date_obj.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            print(f"Warning: Could not parse date '{post_data['post_date']}' for {post_data['title']}, using slug only")
            return f"{post_data['slug']}.yml"
        
        # Use the slug from WordPress
        slug = post_data['slug'] if post_data['slug'] else self.slugify(post_data['title'])
        
        # Create filename that matches Jekyll post format (but .yml instead of .html)
        return f"{date_prefix}-{slug}.yml"
    
    def generate_yaml_output(self, posts_with_comments):
        """Generate YAML output for each post."""
        if self.dry_run:
            print("\n🔍 DRY RUN MODE - No files will be created")
            print("=" * 60)
        
        output_dir = Path('_data/comments')
        if not self.dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
        
        summary = []
        
        for slug, post_data in posts_with_comments.items():
            # Create YAML filename that matches Jekyll post naming
            comment_filename = self.generate_jekyll_filename(post_data)
            yaml_file = output_dir / comment_filename
            
            yaml_data = {
                'wordpress_comments': []
            }
            
            for comment in post_data['comments']:
                yaml_data['wordpress_comments'].append({
                    'author': comment['author'],
                    'date': comment['date'],
                    'content': comment['content']
                })
            
            if self.dry_run:
                print(f"\n📄 Would create: {yaml_file}")
                print(f"   Post: {post_data['title']}")
                print(f"   Comments: {len(post_data['comments'])}")
                print(f"   Post Date: {post_data['post_date']}")
                
                # Show first few comments as preview
                for i, comment in enumerate(post_data['comments'][:3]):
                    print(f"   Comment {i+1}: {comment['author']} ({comment['date']})")
                    content_preview = comment['content'][:100].replace('\n', ' ')
                    print(f"     \"{content_preview}{'...' if len(comment['content']) > 100 else ''}\"")
                
                if len(post_data['comments']) > 3:
                    print(f"   ... and {len(post_data['comments']) - 3} more comments")
            else:
                # Write YAML file
                with open(yaml_file, 'w', encoding='utf-8') as f:
                    yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True)
                print(f"Created {yaml_file} with {len(post_data['comments'])} comments")
            
            summary.append({
                'post': post_data['title'],
                'slug': slug,
                'comments': len(post_data['comments']),
                'file': str(yaml_file),
                'post_date': post_data['post_date']
            })
        
        return summary
    
    def generate_front_matter_examples(self, posts_with_comments):
        """Generate example front matter for posts."""
        examples_file = Path('_data/comments') / 'README.txt'
        
        if self.dry_run:
            print(f"\n📝 Would create front matter examples in: {examples_file}")
            return
        
        with open(examples_file, 'w', encoding='utf-8') as f:
            f.write("# Front Matter Examples for Posts with Comments\n\n")
            
            for slug, post_data in posts_with_comments.items():
                f.write(f"## {post_data['title']} ({slug})\n\n")
                f.write("Add to post front matter:\n\n")
                f.write("```yaml\n")
                f.write("wordpress_comments:\n")
                
                for comment in post_data['comments'][:3]:  # Show first 3 as example
                    f.write(f"  - author: \"{comment['author']}\"\n")
                    f.write(f"    date: \"{comment['date']}\"\n")
                    content_preview = comment['content'][:100] + "..." if len(comment['content']) > 100 else comment['content']
                    f.write(f"    content: |\n")
                    for line in content_preview.split('\n'):
                        f.write(f"      {line}\n")
                
                if len(post_data['comments']) > 3:
                    f.write(f"  # ... {len(post_data['comments']) - 3} more comments\n")
                
                f.write("```\n\n")
        
        print(f"Created front matter examples in {examples_file}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract comments from WordPress XML export')
    parser.add_argument('xml_file', help='Path to WordPress XML export file')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be extracted without creating files')
    parser.add_argument('--filter-posts', type=int, default=None,
                       help='Only show first N posts (useful for testing)')
    
    args = parser.parse_args()
    
    if not Path(args.xml_file).exists():
        print(f"Error: File {args.xml_file} not found")
        sys.exit(1)
    
    extractor = WordPressCommentExtractor(args.xml_file, dry_run=args.dry_run)
    root = extractor.parse_xml()
    
    if root is None:
        sys.exit(1)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - Analyzing WordPress export file...")
    else:
        print("Extracting comments from WordPress export...")
    
    posts_with_comments = extractor.extract_comments(root)
    
    if not posts_with_comments:
        print("No posts with comments found in the export.")
        return
    
    # Filter posts if requested
    if args.filter_posts:
        items = list(posts_with_comments.items())[:args.filter_posts]
        posts_with_comments = dict(items)
        print(f"🔍 Filtering to first {args.filter_posts} posts for preview")
    
    if args.dry_run:
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"Found {len(posts_with_comments)} posts with comments in export")
    else:
        print(f"\nFound {len(posts_with_comments)} posts with comments:")
    
    # Generate YAML files (or show preview in dry-run)
    summary = extractor.generate_yaml_output(posts_with_comments)
    
    # Generate front matter examples
    extractor.generate_front_matter_examples(posts_with_comments)
    
    if args.dry_run:
        print(f"\n📊 SUMMARY:")
        total_comments = sum(item['comments'] for item in summary)
        print(f"Total posts with comments: {len(summary)}")
        print(f"Total comments to extract: {total_comments}")
        print(f"\n💡 To actually extract comments, run without --dry-run flag")
        print(f"💡 Use --filter-posts N to limit output during testing")
    else:
        print(f"\n✅ EXTRACTION COMPLETE:")
        total_comments = sum(item['comments'] for item in summary)
        print(f"Total posts with comments: {len(summary)}")
        print(f"Total comments extracted: {total_comments}")
        print(f"\nFiles created in _data/comments/ directory")
        print(f"Comments will be automatically loaded by Jekyll via site.data.comments")
        print(f"See _data/comments/README.txt for details")

if __name__ == "__main__":
    main() 