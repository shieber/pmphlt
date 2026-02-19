#!/usr/bin/env python3
"""
Enhanced topic analysis for blog posts.
Uses topic modeling, clustering, and semantic analysis to identify themes.
"""

import os
import re
import string
import json
from collections import Counter, defaultdict
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns

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
    
    return ' '.join(words)

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
            cleaned_content = clean_text(post_content)
            
            posts_data.append({
                'file': post_file.name,
                'title': title,
                'date': date,
                'tags': tags,
                'content': cleaned_content,
                'raw_content': post_content
            })
            
        except Exception as e:
            print(f"Error processing {post_file}: {e}")
    
    return posts_data

def topic_modeling_analysis(posts_data):
    """Perform topic modeling using LDA."""
    print("Performing topic modeling analysis...")
    
    # Prepare documents
    documents = [post['content'] for post in posts_data]
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words=STOP_WORDS,
        min_df=2,
        max_df=0.8,
        ngram_range=(1, 2)
    )
    
    # Create document-term matrix
    dtm = vectorizer.fit_transform(documents)
    feature_names = vectorizer.get_feature_names_out()
    
    # Perform LDA topic modeling
    n_topics = 8
    lda = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        max_iter=50
    )
    
    lda_output = lda.fit_transform(dtm)
    
    # Extract topics
    topics = []
    for topic_idx, topic in enumerate(lda.components_):
        top_words_idx = topic.argsort()[-10:][::-1]
        top_words = [feature_names[i] for i in top_words_idx]
        topics.append({
            'topic_id': topic_idx,
            'words': top_words,
            'weights': topic[top_words_idx].tolist()
        })
    
    return topics, lda_output, vectorizer

def cluster_posts(posts_data, lda_output):
    """Cluster posts based on topic distributions."""
    print("Clustering posts by topic similarity...")
    
    # Use K-means clustering on topic distributions
    n_clusters = 5
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(lda_output)
    
    # Group posts by cluster
    clusters = defaultdict(list)
    for i, label in enumerate(cluster_labels):
        clusters[label].append({
            'post': posts_data[i],
            'topic_distribution': lda_output[i].tolist()
        })
    
    return clusters

def generate_word_clouds(posts_data, topics):
    """Generate word clouds for each topic."""
    print("Generating word clouds...")
    
    # Create word clouds for each topic
    for topic in topics:
        # Create word frequency dictionary
        word_freq = dict(zip(topic['words'], topic['weights']))
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            max_words=50
        ).generate_from_frequencies(word_freq)
        
        # Save word cloud
        plt.figure(figsize=(10, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'Topic {topic["topic_id"] + 1} Word Cloud')
        plt.tight_layout()
        plt.savefig(f'topic_{topic["topic_id"] + 1}_wordcloud.png', dpi=300, bbox_inches='tight')
        plt.close()

def analyze_tag_patterns(posts_data):
    """Analyze patterns in post tags."""
    print("Analyzing tag patterns...")
    
    # Collect all tags
    all_tags = []
    tag_frequency = Counter()
    tag_cooccurrence = defaultdict(int)
    
    for post in posts_data:
        tags = post['tags']
        all_tags.extend(tags)
        tag_frequency.update(tags)
        
        # Count tag co-occurrences
        for i, tag1 in enumerate(tags):
            for tag2 in tags[i+1:]:
                tag_cooccurrence[(tag1, tag2)] += 1
    
    # Find most common tag pairs
    top_tag_pairs = sorted(tag_cooccurrence.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        'tag_frequency': dict(tag_frequency.most_common(20)),
        'tag_cooccurrence': dict(top_tag_pairs)
    }

def temporal_analysis(posts_data):
    """Analyze how topics change over time."""
    print("Performing temporal analysis...")
    
    # Group posts by year
    posts_by_year = defaultdict(list)
    for post in posts_data:
        if post['date']:
            try:
                year = post['date'][:4]  # Extract year from date
                posts_by_year[year].append(post)
            except:
                continue
    
    # Analyze word frequency by year
    yearly_word_freq = {}
    for year, posts in posts_by_year.items():
        all_words = []
        for post in posts:
            words = post['content'].split()
            all_words.extend([w for w in words if w not in STOP_WORDS and len(w) > 3])
        
        word_freq = Counter(all_words)
        yearly_word_freq[year] = dict(word_freq.most_common(20))
    
    return yearly_word_freq

def main():
    """Main function to run the enhanced topic analysis."""
    print("Enhanced Topic Analysis for Blog Posts")
    print("=" * 50)
    
    # Extract post data
    posts_data = extract_post_data()
    if not posts_data:
        return
    
    print(f"Analyzing {len(posts_data)} blog posts...")
    
    # Perform topic modeling
    topics, lda_output, vectorizer = topic_modeling_analysis(posts_data)
    
    # Cluster posts
    clusters = cluster_posts(posts_data, lda_output)
    
    # Analyze tags
    tag_analysis = analyze_tag_patterns(posts_data)
    
    # Temporal analysis
    temporal_data = temporal_analysis(posts_data)
    
    # Generate word clouds
    generate_word_clouds(posts_data, topics)
    
    # Save comprehensive results
    results = {
        'summary': {
            'total_posts': len(posts_data),
            'total_topics': len(topics),
            'total_clusters': len(clusters)
        },
        'topics': topics,
        'clusters': {
            str(cluster_id): {
                'size': len(cluster_posts),
                'posts': [post['post']['title'] for post in cluster_posts]
            }
            for cluster_id, cluster_posts in clusters.items()
        },
        'tag_analysis': tag_analysis,
        'temporal_analysis': temporal_data
    }
    
    with open('topic_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 50)
    print("ANALYSIS RESULTS")
    print("=" * 50)
    
    print(f"\n📊 Summary:")
    print(f"   Total posts analyzed: {len(posts_data)}")
    print(f"   Topics identified: {len(topics)}")
    print(f"   Post clusters: {len(clusters)}")
    
    print(f"\n🏷️  Top Tags:")
    for tag, count in list(tag_analysis['tag_frequency'].items())[:10]:
        print(f"   {tag}: {count} posts")
    
    print(f"\n📈 Topics Identified:")
    for topic in topics:
        print(f"   Topic {topic['topic_id'] + 1}: {', '.join(topic['words'][:5])}")
    
    print(f"\n📁 Post Clusters:")
    for cluster_id, cluster_info in results['clusters'].items():
        print(f"   Cluster {cluster_id}: {cluster_info['size']} posts")
        for title in cluster_info['posts'][:3]:  # Show first 3 posts
            print(f"     - {title}")
    
    print(f"\n📅 Temporal Trends:")
    for year in sorted(temporal_data.keys()):
        print(f"   {year}: {len(temporal_data[year])} unique words")
    
    print(f"\n💾 Results saved to:")
    print(f"   - topic_analysis_results.json (comprehensive data)")
    print(f"   - topic_*_wordcloud.png (word clouds for each topic)")

if __name__ == "__main__":
    main() 