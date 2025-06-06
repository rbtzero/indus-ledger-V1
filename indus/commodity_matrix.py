#!/usr/bin/env python3
"""
COMMODITY FLOW HEAT-MAP
=======================
Component 2.2: Commodity matrix and heat-map visualization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from collections import defaultdict

def create_commodity_matrix(edges_file, out_csv, out_png):
    print("📊 COMMODITY FLOW HEAT-MAP GENERATOR")
    print("=" * 37)
    
    # Load trade edges
    edges_df = pd.read_csv(edges_file, sep='\t')
    print(f"   🔗 Loaded {len(edges_df)} trade edges")
    
    # Extract all commodities and sites
    all_commodities = set()
    all_sites = set()
    
    for _, row in edges_df.iterrows():
        commodities = str(row['commodities']).split(';')
        all_commodities.update([c.strip() for c in commodities if c.strip()])
        all_sites.update([row['source'], row['target']])
    
    print(f"   📦 Found {len(all_commodities)} commodities")
    print(f"   🏛️ Found {len(all_sites)} sites")
    
    # Build commodity-site matrix
    matrix_data = {}
    
    for site in all_sites:
        matrix_data[site] = {}
        for commodity in all_commodities:
            matrix_data[site][commodity] = 0.0
    
    # Fill matrix with trade flows
    for _, row in edges_df.iterrows():
        source = row['source']
        target = row['target'] 
        weight = row['weight']
        commodities = str(row['commodities']).split(';')
        
        for commodity in commodities:
            commodity = commodity.strip()
            if commodity:
                # Split flow between source (export) and target (import)
                matrix_data[source][commodity] += weight * 0.5
                matrix_data[target][commodity] += weight * 0.5
    
    # Convert to DataFrame
    matrix_df = pd.DataFrame(matrix_data).T
    matrix_df = matrix_df.fillna(0)
    
    print(f"   📊 Matrix shape: {matrix_df.shape}")
    
    # Calculate flow statistics
    total_flow = matrix_df.sum().sum()
    top_commodities = matrix_df.sum(axis=0).nlargest(5)
    top_sites = matrix_df.sum(axis=1).nlargest(5)
    
    print(f"\n📈 COMMODITY FLOW ANALYSIS")
    print("=" * 28)
    print(f"   💰 Total flow volume: {total_flow:.1f}")
    print(f"   📦 Top commodities:")
    for i, (commodity, flow) in enumerate(top_commodities.items()):
        print(f"      {i+1}. {commodity:15s}: {flow:6.1f}")
    
    print(f"   🏛️ Top trading sites:")
    for i, (site, flow) in enumerate(top_sites.items()):
        print(f"      {i+1}. {site:15s}: {flow:6.1f}")
    
    # Save matrix
    matrix_df.to_csv(out_csv)
    
    # Create heat-map visualization
    plt.figure(figsize=(12, 8))
    
    # Use top sites and commodities for cleaner visualization
    plot_commodities = list(top_commodities.head(8).index)
    plot_sites = list(top_sites.head(6).index)
    
    plot_matrix = matrix_df.loc[plot_sites, plot_commodities]
    
    sns.heatmap(plot_matrix, 
                annot=True, 
                fmt='.1f',
                cmap='YlOrRd',
                cbar_kws={'label': 'Trade Flow Volume'},
                square=True)
    
    plt.title('Indus Valley Commodity Flow Matrix\nTrade Volume by Site and Commodity', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Commodities', fontweight='bold')
    plt.ylabel('Trading Sites', fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Analysis complete: {out_csv}, {out_png}")
    
    return matrix_df

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--edges', required=True)
    parser.add_argument('--out_csv', required=True)
    parser.add_argument('--out_png', required=True)
    
    args = parser.parse_args()
    create_commodity_matrix(args.edges, args.out_csv, args.out_png)

if __name__ == "__main__":
    main() 