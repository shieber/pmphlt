#!/usr/bin/env python3

import os
import glob
import shutil
from datetime import datetime

def main():
    # Directory containing the posts
    posts_dir = '_posts'
    backup_dir = 'backups/posts_unwrap_' + datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    print(f"Created backup directory: {backup_dir}")
    
    # Find all HTML files in the posts directory
    post_files = glob.glob(os.path.join(posts_dir, '*.html'))
    print(f"Found {len(post_files)} post files")
    
    processed_count = 0
    skipped_count = 0
    
    for file_path in post_files:
        filename = os.path.basename(file_path)
        backup_path = os.path.join(backup_dir, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if this post has WordPress HTML wrapper with the actual structure
            if ('<!DOCTYPE html PUBLIC' in content and 
                '<html><body></p>' in content and 
                '</body></html></p>' in content):
                
                print(f"Processing: {filename}")
                
                # Create backup before modifying
                shutil.copy2(file_path, backup_path)
                print(f"  📋 Backed up to: {backup_path}")
                
                # Find the content before the WordPress wrapper (front matter)
                doctype_start = content.find('<p><!DOCTYPE html PUBLIC')
                if doctype_start == -1:
                    print(f"  ⚠ Could not find DOCTYPE start in {filename}")
                    skipped_count += 1
                    continue
                
                pre_wrapper = content[:doctype_start]
                
                # Find the actual content between the wrapper tags
                content_start_marker = '<html><body></p>'
                content_end_marker = '</body></html></p>'
                
                content_start = content.find(content_start_marker)
                content_end = content.find(content_end_marker)
                
                if content_start == -1 or content_end == -1:
                    print(f"  ⚠ Could not find content markers in {filename}")
                    skipped_count += 1
                    continue
                
                # Extract the actual post content
                actual_content_start = content_start + len(content_start_marker)
                post_content = content[actual_content_start:content_end]
                
                # Look for any content after the closing wrapper
                post_wrapper_start = content_end + len(content_end_marker)
                post_wrapper = content[post_wrapper_start:].strip()
                
                # Reconstruct the clean post
                clean_content = pre_wrapper.rstrip() + '\n' + post_content.strip()
                if post_wrapper:
                    clean_content += '\n' + post_wrapper
                
                # Write back to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(clean_content)
                
                processed_count += 1
                print(f"  ✓ Cleaned WordPress wrapper")
                
            else:
                # Create backup anyway for completeness
                shutil.copy2(file_path, backup_path)
                skipped_count += 1
                
        except Exception as e:
            print(f"  ❌ Error processing {filename}: {e}")
            skipped_count += 1
    
    print(f"\nSummary:")
    print(f"- Processed (cleaned): {processed_count} files")
    print(f"- Skipped (already clean): {skipped_count} files") 
    print(f"- Total: {len(post_files)} files")
    print(f"- All files backed up to: {backup_dir}")

if __name__ == '__main__':
    main() 