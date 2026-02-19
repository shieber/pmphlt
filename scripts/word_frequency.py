#!/usr/bin/env python3
"""
Script to analyze word frequency in blog posts.
Finds the 50 most common words across all posts, excluding stop words.
"""

import os
import re
import string
from collections import Counter
from pathlib import Path

# Common English stop words
STOP_WORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
    'could', 'did', 'do', 'does', 'doing', 'down', 'during',
    'each', 'few', 'for', 'from', 'further',
    'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how',
    'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself',
    'just',
    'me', 'more', 'most', 'my', 'myself',
    'no', 'nor', 'not', 'now',
    'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own',
    'same', 'she', 'should', 'so', 'some', 'such',
    'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too',
    'under', 'until', 'up',
    'very',
    'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'would',
    'you', 'your', 'yours', 'yourself', 'yourselves'
}

def clean_text(text):
    """Clean text by removing HTML tags, punctuation, and converting to lowercase."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove punctuation and convert to lowercase
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Split into words and filter out empty strings
    words = [word.strip() for word in text.split() if word.strip()]
    
    return words

def analyze_blog_posts():
    """Analyze all blog posts and return word frequency."""
    posts_dir = Path('_posts')
    word_counter = Counter()
    
    if not posts_dir.exists():
        print(f"Error: {posts_dir} directory not found!")
        return None
    
    # Process each HTML file in the _posts directory
    for post_file in posts_dir.glob('*.html'):
        try:
            with open(post_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract content between the front matter and end of file
            # Look for the end of front matter (---)
            parts = content.split('---', 2)
            if len(parts) >= 3:
                post_content = parts[2]
            else:
                post_content = content
            
            # Clean and process the text
            words = clean_text(post_content)
            
            # Filter out stop words and short words
            filtered_words = [
                word for word in words 
                if word not in STOP_WORDS 
                and len(word) > 2  # Exclude very short words
                and not word.isdigit()  # Exclude pure numbers
            ]
            
            word_counter.update(filtered_words)
            
        except Exception as e:
            print(f"Error processing {post_file}: {e}")
    
    return word_counter

def main():
    """Main function to run the word frequency analysis."""
    print("Analyzing blog posts for word frequency...")
    
    word_counter = analyze_blog_posts()
    
    if word_counter is None:
        return
    
    # Get the 50 most common words
    most_common = word_counter.most_common(50)
    
    print(f"\nFound {len(word_counter)} unique words across all posts.")
    print(f"\nTop 50 most common words (excluding stop words):")
    print("-" * 50)
    
    for i, (word, count) in enumerate(most_common, 1):
        print(f"{i:2d}. {word:15s} - {count:3d} occurrences")
    
    # Save results to a file
    output_file = 'word_frequency_results.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Blog Word Frequency Analysis\n")
        f.write("=" * 30 + "\n\n")
        f.write(f"Total unique words: {len(word_counter)}\n")
        f.write(f"Total word occurrences: {sum(word_counter.values())}\n\n")
        f.write("Top 50 most common words:\n")
        f.write("-" * 30 + "\n")
        
        for i, (word, count) in enumerate(most_common, 1):
            f.write(f"{i:2d}. {word:15s} - {count:3d} occurrences\n")
    
    print(f"\nResults saved to {output_file}")
    
    # Print some statistics
    total_words = sum(word_counter.values())
    print(f"\nStatistics:")
    print(f"Total word occurrences: {total_words}")
    print(f"Unique words: {len(word_counter)}")
    print(f"Average frequency: {total_words / len(word_counter):.1f}")

if __name__ == "__main__":
    main() 