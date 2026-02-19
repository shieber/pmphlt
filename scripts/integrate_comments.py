#!/usr/bin/env python3
"""
WordPress Comments Integration Script

This script automatically integrates extracted WordPress comments
into Jekyll post front matter, eliminating manual copy/paste.
"""

import yaml
import re
import sys
from pathlib import Path
import argparse
from datetime import datetime

class CommentIntegrator:
    def __init__(self, posts_dir="_posts", comments_dir="_comment_data", dry_run=False):
        self.posts_dir = Path(posts_dir)
        self.comments_dir = Path(comments_dir)
        self.dry_run = dry_run
        
    def find_matching_post(self, comment_file_slug):
        """Find the Jekyll post file that matches a comment file slug."""
        # Try different patterns for matching
        patterns = [
            f"*{comment_file_slug}.html",
            f"*{comment_file_slug}.md",
            f"*-{comment_file_slug}.html", 
            f"*-{comment_file_slug}.md"
        ]
        
        for pattern in patterns:
            matches = list(self.posts_dir.glob(pattern))
            if matches:
                return matches[0]  # Return first match
        
        # Try fuzzy matching on slug parts
        slug_parts = comment_file_slug.split('-')
        if len(slug_parts) > 2:
            # Try without first part (might be date prefix)
            shorter_slug = '-'.join(slug_parts[1:])
            for pattern in [f"*{shorter_slug}.html", f"*{shorter_slug}.md"]:
                matches = list(self.posts_dir.glob(pattern))
                if matches:
                    return matches[0]
        
        return None
    
    def parse_front_matter(self, content):
        """Parse Jekyll front matter from post content."""
        if not content.startswith('---\n'):
            return None, content
        
        # Find the end of front matter
        end_marker = content.find('\n---\n', 4)
        if end_marker == -1:
            return None, content
        
        front_matter_text = content[4:end_marker]  # Skip first '---\n'
        post_content = content[end_marker + 5:]    # Skip '\n---\n'
        
        try:
            front_matter = yaml.safe_load(front_matter_text)
            return front_matter, post_content
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
            return None, content
    
    def format_front_matter(self, front_matter):
        """Format front matter as YAML string."""
        return yaml.dump(front_matter, default_flow_style=False, allow_unicode=True)
    
    def integrate_comments_into_post(self, post_file, comments_data):
        """Integrate comments into a specific post file."""
        # Read the post file
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse front matter
        front_matter, post_content = self.parse_front_matter(content)
        
        if front_matter is None:
            print(f"❌ Could not parse front matter in {post_file}")
            return False
        
        # Add comments to front matter
        front_matter['wordpress_comments'] = comments_data['wordpress_comments']
        
        # Reconstruct the file
        new_content = "---\n" + self.format_front_matter(front_matter) + "---\n" + post_content
        
        if self.dry_run:
            print(f"   📝 Would update: {post_file}")
            print(f"      Added {len(comments_data['wordpress_comments'])} comments")
        else:
            # Write the updated file
            with open(post_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Updated: {post_file} ({len(comments_data['wordpress_comments'])} comments)")
        
        return True
    
    def process_all_comments(self):
        """Process all comment files and integrate them into posts."""
        if not self.comments_dir.exists():
            print(f"❌ Comments directory {self.comments_dir} does not exist")
            print("   Run extract_wordpress_comments.py first")
            return
        
        comment_files = list(self.comments_dir.glob("*.yml"))
        if not comment_files:
            print(f"❌ No comment files found in {self.comments_dir}")
            return
        
        if self.dry_run:
            print(f"🔍 DRY RUN MODE - No files will be modified")
            print("=" * 60)
        
        processed = 0
        matched = 0
        
        for comment_file in comment_files:
            processed += 1
            
            # Load comment data
            with open(comment_file, 'r', encoding='utf-8') as f:
                comments_data = yaml.safe_load(f)
            
            # Extract slug from filename
            comment_slug = comment_file.stem  # filename without extension
            
            # Find matching post
            post_file = self.find_matching_post(comment_slug)
            
            if post_file:
                matched += 1
                self.integrate_comments_into_post(post_file, comments_data)
            else:
                print(f"❌ No matching post found for: {comment_file}")
                print(f"   Looked for slug: {comment_slug}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Comment files processed: {processed}")
        print(f"   Posts matched and updated: {matched}")
        print(f"   Unmatched comment files: {processed - matched}")
        
        if self.dry_run:
            print(f"\n💡 To actually update files, run without --dry-run")

def main():
    parser = argparse.ArgumentParser(description='Integrate WordPress comments into Jekyll posts')
    parser.add_argument('--posts-dir', default='_posts', 
                       help='Directory containing Jekyll posts (default: _posts)')
    parser.add_argument('--comments-dir', default='_comment_data',
                       help='Directory containing comment YAML files (default: _comment_data)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be updated without making changes')
    
    args = parser.parse_args()
    
    integrator = CommentIntegrator(
        posts_dir=args.posts_dir,
        comments_dir=args.comments_dir, 
        dry_run=args.dry_run
    )
    
    integrator.process_all_comments()

if __name__ == "__main__":
    main() 