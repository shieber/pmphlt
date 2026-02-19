#!/usr/bin/env python3
"""
Semantic clustering analysis for blog posts.
Uses word co-occurrence and semantic similarity to identify topic clusters.
"""

import os
import re
import string
import json
from collections import Counter, defaultdict
from pathlib import Path
from itertools import combinations

# Extended stop words for academic content
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
    'you', 'your', 'yours', 'yourself', 'yourselves',
    # Academic-specific stop words
    'also', 'however', 'therefore', 'thus', 'furthermore', 'moreover', 'additionally',
    'according', 'based', 'accordingly', 'consequently', 'hence', 'meanwhile',
    'nevertheless', 'nonetheless', 'otherwise', 'similarly', 'subsequently',
    'thereby', 'thereafter', 'therein', 'thereof', 'thereto', 'thereupon',
    'whereas', 'whereby', 'wherein', 'whereof', 'whereupon', 'wherever'
}

# Topic keywords for semantic clustering
TOPIC_KEYWORDS = {
    'scholarly_publishing': [
        'journal', 'journals', 'publisher', 'publishers', 'publishing', 'article', 'articles',
        'publication', 'editorial', 'peer', 'review', 'manuscript', 'submission'
    ],
    'open_access': [
        'open', 'access', 'openaccess', 'oa', 'green', 'gold', 'hybrid', 'repository',
        'archive', 'deposit', 'self', 'archiving'
    ],
    'economics': [
        'fee', 'fees', 'cost', 'costs', 'price', 'pricing', 'revenue', 'subscription',
        'business', 'model', 'economic', 'financial', 'budget', 'funding'
    ],
    'policy': [
        'policy', 'policies', 'mandate', 'mandates', 'rights', 'license', 'licensing',
        'copyright', 'legal', 'regulation', 'compliance'
    ],
    'academic_institutions': [
        'university', 'universities', 'institution', 'institutions', 'faculty', 'library',
        'libraries', 'librarian', 'researcher', 'researchers', 'academic'
    ],
    'technology': [
        'technology', 'digital', 'online', 'web', 'internet', 'software', 'platform',
        'system', 'database', 'metadata', 'api'
    ],
    'research': [
        'research', 'study', 'studies', 'data', 'analysis', 'method', 'methodology',
        'finding', 'findings', 'result', 'results'
    ]
}

def clean_text(text):
    """Clean text by removing HTML tags, punctuation, and converting to lowercase."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove LaTeX math expressions
    text = re.sub(r'\\[\(\[].*?\\[\)\]]', '', text)
    
    # Remove punctuation and convert to lowercase
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Split into words and filter out empty strings
    words = [word.strip() for word in text.split() if word.strip()]
    
    return words

def extract_post_data():
    """Extract post content and metadata."""
    posts_dir = Path('_posts')
    posts_data = []
    
    if not posts_dir.exists():
        print(f"Error: {posts_dir} directory not found!")
        return None
    
    for post_file in posts_dir.glob('*.html'):
        try:
            with open(post_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract front matter
            parts = content.split('---', 2)
            if len(parts) >= 3:
                front_matter = parts[1]
                post_content = parts[2]
            else:
                front_matter = ""
                post_content = content
            
            # Extract title and date from front matter
            title_match = re.search(r'title:\s*(.+)', front_matter)
            date_match = re.search(r'date:\s*(.+)', front_matter)
            tags_match = re.search(r'tags:\s*\[(.*?)\]', front_matter, re.DOTALL)
            
            title = title_match.group(1).strip() if title_match else "Untitled"
            date = date_match.group(1).strip() if date_match else ""
            
            # Extract tags
            tags = []
            if tags_match:
                tags_text = tags_match.group(1)
                tags = [tag.strip() for tag in re.findall(r'([^,\n]+)', tags_text) if tag.strip()]
            
            # Clean content
            words = clean_text(post_content)
            
            posts_data.append({
                'file': post_file.name,
                'title': title,
                'date': date,
                'tags': tags,
                'words': words,
                'raw_content': post_content
            })
            
        except Exception as e:
            print(f"Error processing {post_file}: {e}")
    
    return posts_data

def semantic_clustering(posts_data):
    """Cluster posts based on semantic similarity using keyword matching."""
    print("Performing semantic clustering...")
    
    # Calculate topic scores for each post
    topic_scores = defaultdict(list)
    
    for post in posts_data:
        word_freq = Counter(post['words'])
        post_topics = {}
        
        for topic_name, keywords in TOPIC_KEYWORDS.items():
            score = sum(word_freq.get(keyword, 0) for keyword in keywords)
            post_topics[topic_name] = score
        
        # Find dominant topic
        if any(post_topics.values()):
            dominant_topic = max(post_topics.items(), key=lambda x: x[1])
            topic_scores[dominant_topic[0]].append({
                'post': post,
                'topic_scores': post_topics,
                'dominant_score': dominant_topic[1]
            })
    
    return topic_scores

def word_cooccurrence_analysis(posts_data):
    """Analyze word co-occurrence patterns."""
    print("Analyzing word co-occurrence patterns...")
    
    # Build word co-occurrence matrix
    cooccurrence = defaultdict(int)
    word_frequency = Counter()
    
    for post in posts_data:
        words = [w for w in post['words'] if w not in STOP_WORDS and len(w) > 3]
        word_frequency.update(words)
        
        # Count co-occurrences within a window
        window_size = 5
        for i in range(len(words)):
            for j in range(i + 1, min(i + window_size, len(words))):
                word_pair = tuple(sorted([words[i], words[j]]))
                cooccurrence[word_pair] += 1
    
    # Find strongest word associations
    strong_associations = sorted(cooccurrence.items(), key=lambda x: x[1], reverse=True)[:20]
    
    return {
        'word_frequency': dict(word_frequency.most_common(50)),
        'strong_associations': {f"{word1} + {word2}": count for (word1, word2), count in strong_associations}
    }

def temporal_topic_analysis(posts_data):
    """Analyze how topics evolve over time."""
    print("Analyzing temporal topic trends...")
    
    # Group posts by year
    posts_by_year = defaultdict(list)
    for post in posts_data:
        if post['date']:
            try:
                year = post['date'][:4]
                posts_by_year[year].append(post)
            except:
                continue
    
    # Analyze topic trends by year
    yearly_topics = {}
    for year, posts in posts_by_year.items():
        year_word_freq = Counter()
        for post in posts:
            year_word_freq.update(post['words'])
        
        # Calculate topic scores for the year
        year_topic_scores = {}
        for topic_name, keywords in TOPIC_KEYWORDS.items():
            score = sum(year_word_freq.get(keyword, 0) for keyword in keywords)
            year_topic_scores[topic_name] = score
        
        yearly_topics[year] = {
            'topic_scores': year_topic_scores,
            'top_words': dict(year_word_freq.most_common(20))
        }
    
    return yearly_topics

def generate_topic_summary(topic_scores):
    """Generate a summary of topics and their characteristics."""
    print("Generating topic summary...")
    
    topic_summary = {}
    for topic_name, posts in topic_scores.items():
        if not posts:
            continue
            
        # Calculate topic statistics
        total_posts = len(posts)
        avg_score = sum(p['dominant_score'] for p in posts) / total_posts
        
        # Get representative posts (highest scoring)
        representative_posts = sorted(posts, key=lambda x: x['dominant_score'], reverse=True)[:5]
        
        # Get common words in this topic
        topic_words = Counter()
        for post in posts:
            topic_words.update(post['post']['words'])
        
        # Filter for topic-relevant words
        relevant_words = []
        for word, count in topic_words.most_common(50):
            if word not in STOP_WORDS and len(word) > 3:
                relevant_words.append((word, count))
        
        topic_summary[topic_name] = {
            'post_count': total_posts,
            'average_score': avg_score,
            'representative_posts': [p['post']['title'] for p in representative_posts],
            'top_words': relevant_words[:15]
        }
    
    return topic_summary

def main():
    """Main function to run the semantic clustering analysis."""
    print("Semantic Clustering Analysis for Blog Posts")
    print("=" * 50)
    
    # Extract post data
    posts_data = extract_post_data()
    if not posts_data:
        return
    
    print(f"Analyzing {len(posts_data)} blog posts...")
    
    # Perform semantic clustering
    topic_scores = semantic_clustering(posts_data)
    
    # Analyze word co-occurrence
    cooccurrence_analysis = word_cooccurrence_analysis(posts_data)
    
    # Temporal analysis
    temporal_data = temporal_topic_analysis(posts_data)
    
    # Generate topic summary
    topic_summary = generate_topic_summary(topic_scores)
    
    # Save comprehensive results
    results = {
        'summary': {
            'total_posts': len(posts_data),
            'topics_identified': len(topic_scores),
            'analysis_method': 'semantic_clustering'
        },
        'topic_clusters': topic_summary,
        'word_analysis': cooccurrence_analysis,
        'temporal_analysis': temporal_data
    }
    
    with open('semantic_clustering_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 50)
    print("SEMANTIC CLUSTERING RESULTS")
    print("=" * 50)
    
    print(f"\n📊 Summary:")
    print(f"   Total posts analyzed: {len(posts_data)}")
    print(f"   Topics identified: {len(topic_scores)}")
    
    print(f"\n🏷️  Topic Clusters:")
    for topic_name, summary in topic_summary.items():
        print(f"\n   📌 {topic_name.replace('_', ' ').title()}:")
        print(f"      Posts: {summary['post_count']}")
        print(f"      Avg relevance: {summary['average_score']:.1f}")
        print(f"      Top words: {', '.join([word for word, _ in summary['top_words'][:5]])}")
        print(f"      Representative posts:")
        for title in summary['representative_posts'][:3]:
            print(f"        - {title}")
    
    print(f"\n🔗 Strong Word Associations:")
    for (word1, word2), count in list(cooccurrence_analysis['strong_associations'].items())[:10]:
        print(f"   {word1} ↔ {word2}: {count} co-occurrences")
    
    print(f"\n📅 Temporal Trends:")
    for year in sorted(temporal_data.keys()):
        topic_scores = temporal_data[year]['topic_scores']
        dominant_topic = max(topic_scores.items(), key=lambda x: x[1])
        print(f"   {year}: {dominant_topic[0].replace('_', ' ')} dominant ({dominant_topic[1]} mentions)")
    
    print(f"\n💾 Results saved to:")
    print(f"   - semantic_clustering_results.json (comprehensive data)")

if __name__ == "__main__":
    main() 