#!/usr/bin/env python3
"""
Fix Paragraph Breaks Script

This script adds <p> tags around paragraphs in Jekyll posts that are missing them.
It looks for blank lines in the content and wraps the text between them in <p> tags.
"""

import os
import re
from pathlib import Path

def fix_paragraph_breaks(content):
    """Add <p> tags around paragraphs in the content."""
    if not content:
        return content
    
    # Split content into lines
    lines = content.split('\n')
    
    # Find the end of front matter (second ---)
    front_matter_end = -1
    dash_count = 0
    for i, line in enumerate(lines):
        if line.strip() == '---':
            dash_count += 1
            if dash_count == 2:
                front_matter_end = i
                break
    
    if front_matter_end == -1:
        print("Warning: No front matter found")
        return content
    
    # Separate front matter and content
    front_matter = lines[:front_matter_end + 1]
    content_lines = lines[front_matter_end + 1:]
    
    # Process content lines
    result_lines = []
    current_paragraph = []
    
    for line in content_lines:
        line = line.rstrip()  # Remove trailing whitespace
        
        if line.strip() == '':
            # Empty line - end current paragraph
            if current_paragraph:
                # Add paragraph tags around accumulated lines
                result_lines.append('<p>')
                result_lines.extend(current_paragraph)
                result_lines.append('</p>')
                result_lines.append('')  # Add blank line after paragraph
                current_paragraph = []
        else:
            # Non-empty line - add to current paragraph
            current_paragraph.append(line)
    
    # Handle any remaining content (last paragraph)
    if current_paragraph:
        result_lines.append('<p>')
        result_lines.extend(current_paragraph)
        result_lines.append('</p>')
    
    # Combine front matter and processed content
    return '\n'.join(front_matter + result_lines)

def process_file(filepath, dry_run=False):
    """Process a single file to fix paragraph breaks."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if this is a groundtruth post
        if 'groundtruth' not in content:
            print(f"Skipping {filepath.name} - not a groundtruth post")
            return False
        
        # Check if content already has <p> tags
        if '<p>' in content:
            print(f"Skipping {filepath.name} - already has <p> tags")
            return False
        
        # Fix paragraph breaks
        fixed_content = fix_paragraph_breaks(content)
        
        if fixed_content == content:
            print(f"No changes needed for {filepath.name}")
            return False
        
        if dry_run:
            print(f"Would fix {filepath.name}")
            print("Preview of changes:")
            print("-" * 50)
            
            # Show before/after comparison
            original_lines = content.split('\n')
            fixed_lines = fixed_content.split('\n')
            
            # Find content start (after front matter)
            front_matter_end = 0
            dash_count = 0
            for i, line in enumerate(original_lines):
                if line.strip() == '---':
                    dash_count += 1
                    if dash_count == 2:
                        front_matter_end = i
                        break
            
            content_start = front_matter_end + 1
            
            # Show original content (first 15 lines)
            print("ORIGINAL CONTENT:")
            original_content = original_lines[content_start:content_start + 15]
            print('\n'.join(original_content))
            print()
            
            # Show fixed content (first 15 lines)
            print("FIXED CONTENT:")
            fixed_content_preview = fixed_lines[content_start:content_start + 15]
            print('\n'.join(fixed_content_preview))
            print("-" * 50)
            return True
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"Fixed {filepath.name}")
            return True
            
    except Exception as e:
        print(f"Error processing {filepath.name}: {e}")
        return False

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix paragraph breaks in Jekyll posts')
    parser.add_argument('--posts-dir', default='_posts', help='Posts directory (default: _posts)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    
    args = parser.parse_args()
    
    posts_dir = Path(args.posts_dir)
    if not posts_dir.exists():
        print(f"Error: Posts directory '{posts_dir}' not found")
        return
    
    # Find all HTML and MD files
    post_files = list(posts_dir.glob('*.html')) + list(posts_dir.glob('*.md'))
    
    if not post_files:
        print(f"No post files found in {posts_dir}")
        return
    
    print(f"Found {len(post_files)} post files")
    print(f"Dry run: {args.dry_run}")
    print("-" * 50)
    
    fixed_count = 0
    for post_file in post_files:
        if process_file(post_file, args.dry_run):
            fixed_count += 1
    
    print("-" * 50)
    if args.dry_run:
        print(f"Would fix {fixed_count} files")
    else:
        print(f"Fixed {fixed_count} files")

if __name__ == "__main__":
    main() 