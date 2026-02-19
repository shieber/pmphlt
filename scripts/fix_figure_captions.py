#!/usr/bin/env python3
"""
Script to fix figure captions by extracting attribution information from commented-out table captions.
"""

import os
import re
import glob
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
import html

def extract_attribution_from_comment(comment_text):
    """Extract attribution information from a commented-out table caption."""
    # Look for span elements with attribution links
    attribution_pattern = r'<span[^>]*>.*?<a[^>]*>.*?</a>.*?</span>'
    matches = re.findall(attribution_pattern, comment_text, re.DOTALL)
    
    if matches:
        # Take the last span (usually the attribution one)
        attribution_span = matches[-1]
        
        # Clean up the span - remove color and font-size styling but keep links
        # Remove style attributes
        attribution_span = re.sub(r'style="[^"]*"', '', attribution_span)
        # Remove existing classes and add our semantic class
        attribution_span = re.sub(r'class="[^"]*"', 'class="caption-source"', attribution_span)
        
        # If no class attribute was found, add one
        if 'class=' not in attribution_span:
            attribution_span = attribution_span.replace('<span', '<span class="caption-source"')
        
        return attribution_span
    
    return None

def find_commented_table_before_figure(html_content, figure_index):
    """Find the commented-out table that precedes a figure."""
    # Split content into lines to find the figure
    lines = html_content.split('\n')
    
    # Find the figure line
    figure_line = None
    for i, line in enumerate(lines):
        if '<figure' in line and figure_index == 0:
            figure_line = i
            break
        elif '<figure' in line:
            figure_index -= 1
    
    if figure_line is None:
        return None
    
    # Look backwards for the commented table
    for i in range(figure_line - 1, max(0, figure_line - 20), -1):
        line = lines[i].strip()
        if line.startswith('<!--') and '<table' in line:
            # Found the start of a commented table
            comment_start = i
            comment_end = None
            
            # Find the end of the comment
            for j in range(comment_start, min(len(lines), comment_start + 20)):
                if '-->' in lines[j]:
                    comment_end = j
                    break
            
            if comment_end:
                # Extract the full comment
                comment_lines = lines[comment_start:comment_end + 1]
                comment_text = '\n'.join(comment_lines)
                return comment_text
    
    return None

def fix_figure_captions_in_file(file_path, dry_run=False):
    """Fix figure captions in a single HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        modified = False
        would_modify = False
        caption_fixes = 0
        
        # Find all figure elements
        soup = BeautifulSoup(content, 'html.parser')
        figures = soup.find_all('figure')
        
        # Fix existing figure captions
        for i, figure in enumerate(figures):
            figcaption = figure.find('figcaption')
            if figcaption:
                # Look for commented table before this figure
                comment_text = find_commented_table_before_figure(original_content, i)
                
                if comment_text:
                    attribution = extract_attribution_from_comment(comment_text)
                    
                    if attribution:
                        # Check if figcaption already has attribution
                        if not figcaption.find('a'):
                            # Add attribution to figcaption
                            figcaption_text = figcaption.get_text().strip()
                            
                            if dry_run:
                                # Show what would be changed
                                print(f"  Would fix caption in {file_path}")
                                print(f"    Current: {figcaption}")
                                print(f"    Would add: {attribution}")
                                
                                # Create the new figcaption for preview
                                new_figcaption = soup.new_tag('figcaption')
                                
                                # Create caption text span
                                caption_span = soup.new_tag('span', attrs={'class': 'caption-text'})
                                caption_span.append(figcaption_text)
                                new_figcaption.append(caption_span)
                                new_figcaption.append(' ')
                                
                                # Parse the attribution HTML and add it
                                attribution_soup = BeautifulSoup(attribution, 'html.parser')
                                new_figcaption.append(attribution_soup)
                                
                                print(f"    Revised: {new_figcaption}")
                                print()
                                would_modify = True
                                caption_fixes += 1
                            else:
                                # Create new figcaption with attribution
                                new_figcaption = soup.new_tag('figcaption')
                                
                                # Create caption text span
                                caption_span = soup.new_tag('span', attrs={'class': 'caption-text'})
                                caption_span.append(figcaption_text)
                                new_figcaption.append(caption_span)
                                new_figcaption.append(' ')
                                
                                # Parse the attribution HTML and add it
                                attribution_soup = BeautifulSoup(attribution, 'html.parser')
                                new_figcaption.append(attribution_soup)
                                
                                # Replace the old figcaption
                                figcaption.replace_with(new_figcaption)
                                modified = True
                                caption_fixes += 1
                                
                                print(f"  Fixed caption in {file_path}")
                                print(f"    Original: {figcaption_text}")
                                print(f"    Added: {attribution}")
        
        if modified and not dry_run:
            # Write the modified content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            return True, caption_fixes
        
        if would_modify and dry_run:
            return True, caption_fixes
        
        return False, 0
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, 0

def main():
    parser = argparse.ArgumentParser(description='Fix figure captions by restoring attribution information')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what changes would be made without modifying files')
    args = parser.parse_args()
    
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified")
        print("=" * 60)
    else:
        print("Fixing figure captions by restoring attribution information")
        print("=" * 60)
    
    # Find all HTML files in _posts directory
    post_files = glob.glob('_posts/*.html')
    
    fixed_count = 0
    total_caption_fixes = 0
    total_files = len(post_files)
    
    for file_path in post_files:
        print(f"\nProcessing: {file_path}")
        
        result = fix_figure_captions_in_file(file_path, dry_run=args.dry_run)
        if isinstance(result, tuple):
            file_modified, caption_fixes = result
            if file_modified:
                fixed_count += 1
                total_caption_fixes += caption_fixes
        else:
            # Backward compatibility
            if result:
                fixed_count += 1
    
    print("\n" + "=" * 60)
    if args.dry_run:
        print(f"Dry run complete: {fixed_count} files would be modified out of {total_files} total")
        print(f"  - {total_caption_fixes} caption attributions would be restored")
        print("Run without --dry-run to apply the changes")
    else:
        print(f"Processing complete: {fixed_count} files modified out of {total_files} total")
        print(f"  - {total_caption_fixes} caption attributions restored")
        print("\nPlease review the changes before committing.")

if __name__ == "__main__":
    main() 