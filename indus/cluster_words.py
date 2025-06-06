#!/usr/bin/env python3
import argparse
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from collections import defaultdict
import pandas as pd

def load_embeddings(filepath):
    """Load word embeddings from standard format"""
    print(f"📊 LOADING EMBEDDINGS:")
    
    embeddings = {}
    words = []
    vectors = []
    
    with open(filepath, 'r') as f:
        # Read header
        header = f.readline().strip().split()
        vocab_size, vector_size = int(header[0]), int(header[1])
        print(f"✓ Vocabulary size: {vocab_size}")
        print(f"✓ Vector dimension: {vector_size}")
        
        # Read embeddings
        for line in f:
            parts = line.strip().split()
            word = parts[0]
            vector = np.array([float(x) for x in parts[1:]])
            
            embeddings[word] = vector
            words.append(word)
            vectors.append(vector)
    
    vectors = np.array(vectors)
    print(f"✓ Loaded {len(embeddings)} word vectors")
    
    return embeddings, words, vectors

def find_optimal_k(vectors, max_k=50):
    """Find optimal number of clusters using silhouette score"""
    print(f"\n🔍 FINDING OPTIMAL CLUSTER COUNT:")
    
    max_k = min(max_k, len(vectors) // 2)  # Can't have more clusters than half the data
    
    if max_k < 2:
        print("❌ Too few vectors for clustering")
        return 2
    
    silhouette_scores = []
    k_range = range(2, min(max_k + 1, 21))  # Limit to reasonable range
    
    best_k = 2
    best_score = -1
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(vectors)
        score = silhouette_score(vectors, cluster_labels)
        silhouette_scores.append(score)
        
        print(f"  k={k}: silhouette={score:.3f}")
        
        if score > best_score:
            best_score = score
            best_k = k
    
    print(f"✓ Optimal k: {best_k} (silhouette: {best_score:.3f})")
    return best_k

def perform_clustering(vectors, words, k):
    """Perform K-means clustering"""
    print(f"\n🎯 CLUSTERING WITH k={k}:")
    
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(vectors)
    
    # Group words by cluster
    clusters = defaultdict(list)
    for word, label in zip(words, cluster_labels):
        clusters[label].append(word)
    
    # Calculate cluster statistics
    silhouette = silhouette_score(vectors, cluster_labels)
    print(f"✓ Silhouette score: {silhouette:.3f}")
    print(f"✓ Created {len(clusters)} clusters")
    
    # Show cluster size distribution
    sizes = [len(cluster) for cluster in clusters.values()]
    print(f"✓ Cluster sizes: min={min(sizes)}, max={max(sizes)}, avg={np.mean(sizes):.1f}")
    
    return clusters, cluster_labels, silhouette

def analyze_clusters(clusters, embeddings):
    """Analyze and interpret clusters"""
    print(f"\n📋 CLUSTER ANALYSIS:")
    
    # Sort clusters by size (largest first)
    sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)
    
    cluster_analysis = []
    
    for cluster_id, words in sorted_clusters[:20]:  # Show top 20 clusters
        print(f"\n  Cluster {cluster_id} ({len(words)} words):")
        
        # Show all words in cluster
        words_str = ", ".join(sorted(words))
        print(f"    Words: {words_str}")
        
        # Try to identify semantic pattern
        semantic_hints = identify_semantic_pattern(words)
        if semantic_hints:
            print(f"    🎯 Semantic pattern: {semantic_hints}")
        
        # Calculate intra-cluster similarity
        if len(words) > 1:
            similarities = []
            for i, word1 in enumerate(words):
                for word2 in words[i+1:]:
                    sim = np.dot(embeddings[word1], embeddings[word2]) / (
                        np.linalg.norm(embeddings[word1]) * np.linalg.norm(embeddings[word2])
                    )
                    similarities.append(sim)
            
            avg_sim = np.mean(similarities)
            print(f"    📊 Avg similarity: {avg_sim:.3f}")
        
        cluster_analysis.append({
            'cluster_id': cluster_id,
            'size': len(words),
            'words': words,
            'semantic_pattern': semantic_hints
        })
    
    return cluster_analysis

def identify_semantic_pattern(words):
    """Try to identify semantic patterns in word clusters"""
    
    # Known semantic categories from our previous analysis
    semantic_categories = {
        'AUTHORITY': ['ra', 'ka', 'pa', 'ma'],  # king, person, father, mother
        'COMMODITY': ['ku', 'na', 'nan'],       # grain, river, water
        'ACTION': ['ta', 'da', 'ja', 'ya'],     # give, do, come, go
        'QUALIFIER': ['la', 'sa', 'cha'],       # small, sacred, sacred
        'LOCATION': ['ha', 'jha'],              # land, place
    }
    
    # Check if cluster matches known categories
    for category, known_words in semantic_categories.items():
        overlap = set(words) & set(known_words)
        if len(overlap) >= 2:  # At least 2 matches
            return f"{category} (matches: {', '.join(overlap)})"
    
    # Look for phonetic patterns
    if len(words) >= 3:
        # Check for common prefixes
        prefixes = defaultdict(int)
        for word in words:
            if len(word) >= 2:
                prefixes[word[:2]] += 1
        
        common_prefix = max(prefixes.items(), key=lambda x: x[1])
        if common_prefix[1] >= 3:
            return f"Common prefix '{common_prefix[0]}'"
        
        # Check for common suffixes
        suffixes = defaultdict(int)
        for word in words:
            if len(word) >= 2:
                suffixes[word[-2:]] += 1
        
        common_suffix = max(suffixes.items(), key=lambda x: x[1])
        if common_suffix[1] >= 3:
            return f"Common suffix '{common_suffix[0]}'"
    
    return None

def save_clusters(clusters, output_path, cluster_analysis):
    """Save clustering results to TSV file"""
    print(f"\n💾 SAVING CLUSTERS:")
    
    rows = []
    for cluster_id, words in clusters.items():
        # Find analysis for this cluster
        analysis = next((a for a in cluster_analysis if a['cluster_id'] == cluster_id), None)
        semantic_pattern = analysis['semantic_pattern'] if analysis else ""
        
        for word in words:
            rows.append({
                'word': word,
                'cluster_id': cluster_id,
                'cluster_size': len(words),
                'semantic_pattern': semantic_pattern
            })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, sep='\t', index=False)
    
    print(f"✓ Saved {len(rows)} word-cluster mappings to {output_path}")
    print(f"✓ Created {len(clusters)} semantic clusters")

def main():
    parser = argparse.ArgumentParser(description="Cluster words using Word2Vec embeddings")
    parser.add_argument('--emb', required=True, help="Input embeddings file")
    parser.add_argument('--k', type=int, default=0, help="Number of clusters (0 = auto-detect)")
    parser.add_argument('--out', required=True, help="Output clusters TSV file")
    
    args = parser.parse_args()
    
    print("🎯 SEMANTIC WORD CLUSTERING")
    print("=" * 28)
    
    # Load embeddings
    embeddings, words, vectors = load_embeddings(args.emb)
    
    if len(words) < 4:
        print("❌ ERROR: Too few words for clustering")
        return
    
    # Determine optimal k
    if args.k <= 0:
        k = find_optimal_k(vectors)
    else:
        k = args.k
        print(f"✓ Using specified k: {k}")
    
    # Perform clustering
    clusters, cluster_labels, silhouette = perform_clustering(vectors, words, k)
    
    # Analyze clusters
    cluster_analysis = analyze_clusters(clusters, embeddings)
    
    # Save results
    save_clusters(clusters, args.out, cluster_analysis)
    
    print(f"\n✅ CLUSTERING COMPLETE!")
    print(f"✓ Silhouette score: {silhouette:.3f}")
    print(f"✓ Total clusters: {len(clusters)}")

if __name__ == "__main__":
    main() 