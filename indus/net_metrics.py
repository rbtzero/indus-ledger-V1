#!/usr/bin/env python3
"""
NETWORK METRICS ANALYZER
=======================
Calculates network topology metrics from trade edges
"""

import pandas as pd
import numpy as np
import networkx as nx
import argparse

def analyze_network_metrics(edges_file, out_csv, out_gexf):
    """Analyze network topology and save metrics"""
    print("📊 NETWORK METRICS ANALYZER")
    print("=" * 29)
    
    # Load edges
    edges_df = pd.read_csv(edges_file, sep='\t')
    print(f"   📊 Loaded {len(edges_df)} trade edges")
    
    # Build NetworkX graph
    G = nx.Graph()
    
    for _, row in edges_df.iterrows():
        source = row['source']
        target = row['target'] 
        weight = row['weight']
        G.add_edge(source, target, weight=weight)
    
    print(f"   🔗 Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # Calculate metrics
    metrics = {}
    
    # Node-level metrics
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    closeness_centrality = nx.closeness_centrality(G)
    
    # Network-level metrics
    if G.number_of_nodes() > 1:
        clustering = nx.average_clustering(G)
        density = nx.density(G)
        
        if nx.is_connected(G):
            diameter = nx.diameter(G)
            avg_path_length = nx.average_shortest_path_length(G)
        else:
            diameter = "Disconnected"
            avg_path_length = "Disconnected"
    else:
        clustering = density = diameter = avg_path_length = 0
    
    # Compile node metrics
    node_metrics = []
    for node in G.nodes():
        node_metrics.append({
            'node': node,
            'degree': G.degree(node),
            'degree_centrality': degree_centrality[node],
            'betweenness_centrality': betweenness_centrality[node],
            'closeness_centrality': closeness_centrality[node]
        })
    
    # Save node metrics
    nodes_df = pd.DataFrame(node_metrics)
    nodes_df.to_csv(out_csv, index=False)
    
    # Network summary
    print(f"\n📈 NETWORK TOPOLOGY ANALYSIS")
    print("=" * 30)
    print(f"   🔗 Density: {density:.3f}")
    print(f"   🕸️ Clustering: {clustering:.3f}")
    print(f"   📏 Diameter: {diameter}")
    print(f"   📐 Avg path length: {avg_path_length}")
    
    # Top nodes by centrality
    if len(nodes_df) > 0:
        print(f"\n   📊 TOP NODES BY CENTRALITY:")
        top_nodes = nodes_df.nlargest(5, 'betweenness_centrality')
        for i, (_, row) in enumerate(top_nodes.iterrows()):
            print(f"      {i+1}. {row['node']:15s}: betweenness={row['betweenness_centrality']:.3f}")
    
    # Save GEXF for Gephi
    nx.write_gexf(G, out_gexf)
    
    print(f"\n✅ NETWORK ANALYSIS COMPLETE")
    print(f"   📋 Node metrics: {out_csv}")
    print(f"   📊 Gephi file: {out_gexf}")
    
    return nodes_df, G

def main():
    parser = argparse.ArgumentParser(description='Analyze trade network metrics')
    parser.add_argument('--edges', required=True, help='Trade edges TSV file')
    parser.add_argument('--out_csv', required=True, help='Output node metrics CSV')
    parser.add_argument('--out_gexf', required=True, help='Output GEXF for Gephi')
    
    args = parser.parse_args()
    
    nodes_df, graph = analyze_network_metrics(args.edges, args.out_csv, args.out_gexf)
    
    return 0

if __name__ == "__main__":
    exit(main()) 