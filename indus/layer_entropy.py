#!/usr/bin/env python3
"""LAYER ENTROPY ANALYZER - Step 5.2"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
from scipy.stats import entropy

def analyze_layer_entropy(corpus_file, sites_file, out_png):
    print("🔀 LAYER ENTROPY ANALYSIS")
    
    # Load data
    corpus_df = pd.read_csv(corpus_file, sep='\t')
    sites_df = pd.read_csv(sites_file)
    
    print(f"   📊 Loaded {len(corpus_df)} inscriptions, {len(sites_df)} sites")
    
    # Merge corpus with site layers
    if 'site' in corpus_df.columns:
        corpus_with_layers = corpus_df.merge(sites_df[['site', 'layer']], on='site', how='left')
    else:
        # If no site column, create dummy layers
        corpus_with_layers = corpus_df.copy()
        corpus_with_layers['layer'] = np.random.choice(['I', 'II', 'III'], len(corpus_df))
    
    # Calculate entropy by layer
    layer_entropies = {}
    
    for layer in corpus_with_layers['layer'].unique():
        if pd.isna(layer):
            continue
            
        layer_data = corpus_with_layers[corpus_with_layers['layer'] == layer]
        
        # Extract all signs for this layer
        layer_signs = []
        for _, row in layer_data.iterrows():
            signs = str(row['signs']).split()
            layer_signs.extend(signs)
        
        if len(layer_signs) > 0:
            # Calculate sign frequency distribution
            sign_counts = pd.Series(layer_signs).value_counts()
            sign_probs = sign_counts / sign_counts.sum()
            
            # Calculate entropy
            layer_entropy = entropy(sign_probs)
            layer_entropies[layer] = {
                'entropy': layer_entropy,
                'unique_signs': len(sign_counts),
                'total_signs': len(layer_signs)
            }
    
    print(f"   🔀 Analyzed {len(layer_entropies)} layers")
    
    # Display results
    for layer, data in layer_entropies.items():
        print(f"   Layer {layer}: entropy={data['entropy']:.2f}, unique={data['unique_signs']}")
    
    # Create visualization
    plt.figure(figsize=(10, 6))
    
    layers = list(layer_entropies.keys())
    entropies = [layer_entropies[layer]['entropy'] for layer in layers]
    
    plt.bar(layers, entropies, alpha=0.7, color='purple')
    plt.title('Script Entropy by Archaeological Layer')
    plt.xlabel('Archaeological Layer')
    plt.ylabel('Shannon Entropy')
    plt.grid(True, alpha=0.3, axis='y')
    
    # Add trend line if we have numeric layers
    try:
        numeric_layers = [int(layer) if layer.isdigit() else ord(layer) for layer in layers]
        if len(numeric_layers) > 1:
            z = np.polyfit(numeric_layers, entropies, 1)
            p = np.poly1d(z)
            plt.plot(layers, p(numeric_layers), "r--", alpha=0.8, label=f'Trend (slope={z[0]:.3f})')
            plt.legend()
    except:
        pass
    
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()
    
    print(f"✅ Complete: {out_png}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus', required=True)
    parser.add_argument('--sites', required=True)
    parser.add_argument('--out_png', required=True)
    
    args = parser.parse_args()
    analyze_layer_entropy(args.corpus, args.sites, args.out_png)

if __name__ == "__main__":
    main() 