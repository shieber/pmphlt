#!/usr/bin/env python3
"""
Script to fix redundant caption text in figure captions.
This script removes duplicated caption text from caption-source spans.
"""

import os
import re
import glob
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
import html

def fix_redundant_captions_in_file(file_path, dry_run=False):
    """Fix redundant caption text in a single HTML file."""
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
        
        for figure in figures:
            figcaption = figure.find('figcaption')
            if figcaption:
                # Look for caption-text and caption-source spans
                caption_text_span = figcaption.find('span', class_='caption-text')
                caption_source_spans = figcaption.find_all('span', class_='caption-source')
                
                if caption_text_span and caption_source_spans:
                    caption_text = caption_text_span.get_text().strip()
                    
                    # Check if any caption-source span starts with the same text
                    for span in caption_source_spans:
                        source_text = span.get_text().strip()
                        
                        # If the source text starts with the caption text, remove the redundant part
                        if source_text.startswith(caption_text):
                            # Get the HTML content of the source span
                            source_html = str(span)
                            
                            # Remove the redundant text from the beginning
                            # We need to be careful to preserve the HTML structure
                            if dry_run:
                                print(f"  Would fix redundant caption in {file_path}")
                                print(f"    Caption text: '{caption_text}'")
                                print(f"    Would remove redundant span: {span}")
                                print(f"    (This span contains: '{source_text}')")
                                
                                # Create a preview of what the figure would look like after the fix
                                print(f"    Final figure would be:")
                                print(f"      <figure>")
                                print(f"        <img ... />")
                                print(f"        <figcaption>")
                                print(f"          <span class=\"caption-text\">{caption_text}</span>")
                                # Show remaining caption-source spans (excluding the redundant one)
                                remaining_spans = []
                                for remaining_span in caption_source_spans:
                                    if remaining_span.get_text().strip() != source_text:
                                        remaining_spans.append(str(remaining_span))
                                for remaining_span in remaining_spans:
                                    print(f"          {remaining_span}")
                                print(f"        </figcaption>")
                                print(f"      </figure>")
                                print()
                                would_modify = True
                                caption_fixes += 1
                            else:
                                # Remove the entire redundant span
                                # Also remove any leading <br/> tags that might be before it
                                if span.find_previous_sibling() and str(span.find_previous_sibling()).strip() == '<br/>':
                                    span.find_previous_sibling().decompose()
                                
                                # Remove the redundant span entirely
                                span.decompose()
                                
                                modified = True
                                caption_fixes += 1
                                print(f"  Fixed redundant caption in {file_path}")
                                print(f"    Removed entire redundant span containing: '{source_text}'")
        
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
    parser = argparse.ArgumentParser(description='Fix redundant caption text in figure captions')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what changes would be made without modifying files')
    args = parser.parse_args()
    
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified")
        print("=" * 60)
    else:
        print("Fixing redundant caption text in figure captions")
        print("=" * 60)
    
    # Find all HTML files in _posts directory
    post_files = glob.glob('_posts/*.html')
    
    fixed_count = 0
    total_caption_fixes = 0
    total_files = len(post_files)
    
    for file_path in post_files:
        print(f"\nProcessing: {file_path}")
        
        result = fix_redundant_captions_in_file(file_path, dry_run=args.dry_run)
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
        print(f"  - {total_caption_fixes} redundant caption texts would be removed")
        print("Run without --dry-run to apply the changes")
    else:
        print(f"Processing complete: {fixed_count} files modified out of {total_files} total")
        print(f"  - {total_caption_fixes} redundant caption texts removed")
        print("\nPlease review the changes before committing.")

if __name__ == "__main__":
    main() 