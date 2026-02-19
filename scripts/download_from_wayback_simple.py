#!/usr/bin/env python3
"""
Simple script to download missing images from Wayback Machine using known patterns.
"""

import os
import requests
import time
from pathlib import Path
from urllib.parse import urlparse, unquote

# Define the missing images with their most likely Wayback Machine URLs
MISSING_IMAGES = {
    'B007635_pro.jpg': {
        'wayback_urls': [
            'https://web.archive.org/web/20100101000000if_/https://commons.wikimedia.org/wiki/File:B007635_pro.jpg',
            'https://web.archive.org/web/20120101000000if_/https://commons.wikimedia.org/wiki/File:B007635_pro.jpg',
            'https://web.archive.org/web/20130101000000if_/https://commons.wikimedia.org/wiki/File:B007635_pro.jpg'
        ],
        'description': 'Babbage difference engine fragment'
    },
    'header_dash.gif': {
        'wayback_urls': [
            'https://web.archive.org/web/20100101000000if_/https://dash.harvard.edu/',
            'https://web.archive.org/web/20110101000000if_/https://dash.harvard.edu/',
            'https://web.archive.org/web/20120101000000if_/https://dash.harvard.edu/'
        ],
        'description': 'DASH repository header'
    },
    '942.gif': {
        'wayback_urls': [
            'https://web.archive.org/web/20100101000000if_/https://www.tetrahedron.org/',
            'https://web.archive.org/web/20110101000000if_/https://www.tetrahedron.org/',
            'https://web.archive.org/web/20120101000000if_/https://www.tetrahedron.org/'
        ],
        'description': 'Tetrahedron journal cover'
    },
    '3559286242_a6decdc7d2_m.jpg': {
        'wayback_urls': [
            'https://web.archive.org/web/20110101000000if_/https://www.flickr.com/photos/3559286242_a6decdc7d2_m.jpg',
            'https://web.archive.org/web/20120101000000if_/https://www.flickr.com/photos/3559286242_a6decdc7d2_m.jpg',
            'https://web.archive.org/web/20130101000000if_/https://www.flickr.com/photos/3559286242_a6decdc7d2_m.jpg'
        ],
        'description': 'NIH related image'
    },
    '20100117_universitypresidents_photo_main_01.jpg': {
        'wayback_urls': [
            'https://web.archive.org/web/20110101000000if_/http://www.denison.edu/theden/wp-content/uploads/2011/01/20100117_universitypresidents_photo_main_01.jpg',
            'https://web.archive.org/web/20120101000000if_/http://www.denison.edu/theden/wp-content/uploads/2011/01/20100117_universitypresidents_photo_main_01.jpg',
            'https://web.archive.org/web/20130101000000if_/http://www.denison.edu/theden/wp-content/uploads/2011/01/20100117_universitypresidents_photo_main_01.jpg'
        ],
        'description': 'William G. Bowen photo'
    },
    'alice.jpg': {
        'wayback_urls': [
            'https://web.archive.org/web/20120101000000if_/http://ids.lib.harvard.edu/ids/view/10249976?buttons=y',
            'https://web.archive.org/web/20130101000000if_/http://ids.lib.harvard.edu/ids/view/10249976?buttons=y',
            'https://web.archive.org/web/20140101000000if_/http://ids.lib.harvard.edu/ids/view/10249976?buttons=y'
        ],
        'description': 'Houghton Library image'
    },
    '180px-Karen_Sp%C3%A4rck.jpg': {
        'wayback_urls': [
            'https://web.archive.org/web/20120101000000if_/https://commons.wikimedia.org/wiki/File:Karen_Sp%C3%A4rck_Jones.jpg',
            'https://web.archive.org/web/20130101000000if_/https://commons.wikimedia.org/wiki/File:Karen_Sp%C3%A4rck_Jones.jpg',
            'https://web.archive.org/web/20140101000000if_/https://commons.wikimedia.org/wiki/File:Karen_Sp%C3%A4rck_Jones.jpg'
        ],
        'description': 'Karen Spärck Jones photo'
    },
    'block_120x240.jpg': {
        'wayback_urls': [
            'https://web.archive.org/web/20120101000000if_/https://example.com/block_120x240.jpg',
            'https://web.archive.org/web/20130101000000if_/https://example.com/block_120x240.jpg'
        ],
        'description': 'Block image'
    },
    '6986624532_554a079fe0_b.jpg': {
        'wayback_urls': [
            'https://web.archive.org/web/20130101000000if_/https://www.flickr.com/photos/6986624532_554a079fe0_b.jpg',
            'https://web.archive.org/web/20140101000000if_/https://www.flickr.com/photos/6986624532_554a079fe0_b.jpg',
            'https://web.archive.org/web/20150101000000if_/https://www.flickr.com/photos/6986624532_554a079fe0_b.jpg'
        ],
        'description': 'Flickr image'
    },
    'Ensuring-Value-for-Premiums-9.jpg': {
        'wayback_urls': [
            'https://web.archive.org/web/20131106003622if_/http://www.logarchism.com/wp-content/uploads/2011/12/Ensuring-Value-for-Premiums-9.jpg',
            'https://web.archive.org/web/20130101000000if_/http://www.logarchism.com/wp-content/uploads/2011/12/Ensuring-Value-for-Premiums-9.jpg',
            'https://web.archive.org/web/20140101000000if_/http://www.logarchism.com/wp-content/uploads/2011/12/Ensuring-Value-for-Premiums-9.jpg'
        ],
        'description': 'Medical loss ratio chart'
    },
    'twins_scandy_.jpg': {
        'wayback_urls': [
            'https://web.archive.org/web/20140101000000if_/http://www.telefon.de/images/out550/twin/twins_scandy_.jpg',
            'https://web.archive.org/web/20150101000000if_/http://www.telefon.de/images/out550/twin/twins_scandy_.jpg',
            'https://web.archive.org/web/20160101000000if_/http://www.telefon.de/images/out550/twin/twins_scandy_.jpg'
        ],
        'description': 'Scandy smartphone handle'
    }
}

def download_from_wayback(wayback_url, filename):
    """Download an image from a Wayback Machine URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(wayback_url, headers=headers, timeout=30, allow_redirects=True)
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            filename_str = str(filename)  # Convert PosixPath to string
            if 'image' in content_type or filename_str.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"    ✗ Not an image: {content_type}")
                return False
        else:
            print(f"    ✗ HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"    ✗ Error downloading: {e}")
        return False

def main():
    # Create download directory
    download_dir = Path('wayback_images')
    download_dir.mkdir(exist_ok=True)
    
    print(f"Downloading missing images from Wayback Machine")
    print(f"Images will be saved to: {download_dir}/")
    print("=" * 60)
    
    successful = 0
    failed = 0
    
    for filename, info in MISSING_IMAGES.items():
        print(f"\n{info['description']} ({filename})")
        print("-" * 40)
        
        # Try to download from each Wayback URL
        downloaded = False
        for i, wayback_url in enumerate(info['wayback_urls'], 1):
            print(f"  Trying Wayback URL {i}: {wayback_url}")
            
            output_filename = download_dir / filename
            
            if download_from_wayback(wayback_url, output_filename):
                print(f"  ✓ Successfully downloaded {filename}")
                successful += 1
                downloaded = True
                break
            else:
                print(f"  ✗ Failed to download from Wayback URL {i}")
        
        if not downloaded:
            print(f"  ✗ Failed to download from all Wayback URLs")
            failed += 1
        
        # Be nice to Wayback Machine
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print(f"Download complete: {successful} successful, {failed} failed")
    print(f"Images saved to: {download_dir}/")
    print("\nPlease review the downloaded images before moving them to the assets folder.")

if __name__ == "__main__":
    main() 