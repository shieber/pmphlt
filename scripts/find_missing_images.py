#!/usr/bin/env python3
"""
Script to find missing images by scanning all HTML files and checking
which referenced images don't exist locally or return 404 errors.
"""

import os
import re
import glob
import requests
from pathlib import Path
from urllib.parse import urlparse

def find_image_references():
    """Find all image references in HTML files."""
    image_patterns = [
        r'src=["\']([^"\']*\.(?:jpg|jpeg|png|gif|svg))["\']',
        r'!\[[^\]]*\]\(([^)]*\.(?:jpg|jpeg|png|gif|svg))\)',
        r'<img[^>]*src=["\']([^"\']*\.(?:jpg|jpeg|png|gif|svg))["\'][^>]*>'
    ]
    
    image_refs = set()
    
    # Scan all HTML files
    for html_file in glob.glob('**/*.html', recursive=True):
        if html_file.startswith('_site/'):  # Skip built site
            continue
            
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern in image_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Handle Jekyll template variables
                    if '{{site.baseurl}}' in match:
                        # Extract the path after {{site.baseurl}}
                        path_match = re.search(r'\{\{site\.baseurl\}\}(.+)', match)
                        if path_match:
                            match = path_match.group(1)
                        else:
                            continue
                    elif '{{page.baseurl}}' in match:
                        # Extract the path after {{page.baseurl}}
                        path_match = re.search(r'\{\{page\.baseurl\}\}(.+)', match)
                        if path_match:
                            match = path_match.group(1)
                        else:
                            continue
                    elif any(template_var in match for template_var in ['{{', '}}', '{%', '%}']):
                        # Skip other template variables we can't handle
                        continue
                    
                    # Clean up the path
                    if match.startswith('/'):
                        match = match[1:]
                    if match.startswith('assets/'):
                        image_refs.add(match)
                    elif not match.startswith(('http://', 'https://', '//')):
                        # Assume relative to assets if not absolute
                        if not match.startswith('assets/'):
                            match = f'assets/{match}'
                        image_refs.add(match)
                    else:
                        # External URL
                        image_refs.add(match)
        except Exception as e:
            print(f"Error reading {html_file}: {e}")
    
    return image_refs

def check_url_status(url):
    """Check if a URL returns a 404 error."""
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code != 404
    except Exception as e:
        print(f"Error checking {url}: {e}")
        return False

def check_missing_images(image_refs):
    """Check which referenced images are missing."""
    missing = []
    
    for image_path in sorted(image_refs):
        if image_path.startswith(('http://', 'https://', '//')):
            # External URL - check if it returns 404
            if not check_url_status(image_path):
                missing.append(image_path)
                print(f"MISSING (404): {image_path}")
            else:
                print(f"EXISTS (200): {image_path}")
        else:
            # Local file
            if not os.path.exists(image_path):
                missing.append(image_path)
                print(f"MISSING (local): {image_path}")
            else:
                print(f"EXISTS (local): {image_path}")
    
    return missing

def main():
    print("Scanning for image references...")
    image_refs = find_image_references()
    
    print(f"\nFound {len(image_refs)} image references")
    print("\nChecking which images exist...")
    
    missing = check_missing_images(image_refs)
    
    print(f"\nMissing images: {len(missing)}")
    
    # Write missing images to file
    with open('missing_images.txt', 'w') as f:
        for image_path in missing:
            f.write(f"{image_path}\n")
    
    print(f"\nMissing images written to missing_images.txt")
    
    if missing:
        print("\nMissing images:")
        for image_path in missing:
            print(f"  {image_path}")
    else:
        print("\nNo missing images found!")

if __name__ == "__main__":
    main() 