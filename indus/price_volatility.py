#!/usr/bin/env python3
"""PRICE VOLATILITY ANALYZER - Step 4"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse

def analyze_price_volatility(ledger_file, layers_file, commodity, out_png, out_csv):
    print(f"💰 PRICE VOLATILITY: {commodity}")
    
    # Load data
    ledger_df = pd.read_csv(ledger_file, sep='\t')
    layers_df = pd.read_csv(layers_file)
    
    print(f"   📊 Loaded {len(ledger_df)} transactions, {len(layers_df)} sites")
    
    # Filter for commodity
    commodity_data = ledger_df[ledger_df['commodity_type'] == commodity]
    
    if len(commodity_data) == 0:
        print(f"   ⚠️ No {commodity} transactions found")
        # Create empty outputs
        pd.DataFrame({'layer': [], 'mean': [], 'std': []}).to_csv(out_csv, index=False)
        plt.figure()
        plt.text(0.5, 0.5, f'No {commodity} data', ha='center', va='center')
        plt.savefig(out_png)
        plt.close()
        return
    
    # Merge with layers
    commodity_data = commodity_data.merge(layers_df[['site', 'layer']], on='site', how='left')
    
    # Statistics by layer
    layer_stats = commodity_data.groupby('layer')['value'].agg(['mean', 'std', 'count']).reset_index()
    
    # Price spike detection (±3σ)
    overall_mean = commodity_data['value'].mean()
    overall_std = commodity_data['value'].std()
    spikes = commodity_data[abs(commodity_data['value'] - overall_mean) > 3 * overall_std]
    
    print(f"   💰 Mean: {overall_mean:.2f}, Std: {overall_std:.2f}")
    print(f"   🚨 Price spikes: {len(spikes)}")
    
    # Save statistics
    layer_stats.to_csv(out_csv, index=False)
    
    # Create visualization
    plt.figure(figsize=(10, 6))
    plt.bar(layer_stats['layer'], layer_stats['mean'], alpha=0.7)
    plt.title(f'{commodity.title()} Price by Layer')
    plt.xlabel('Layer')
    plt.ylabel('Mean Price')
    plt.savefig(out_png)
    plt.close()
    
    print(f"✅ Complete: {out_csv}, {out_png}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ledger', required=True)
    parser.add_argument('--layers', required=True)
    parser.add_argument('--commodity', required=True)
    parser.add_argument('--out_png', required=True)
    parser.add_argument('--out_csv', required=True)
    
    args = parser.parse_args()
    analyze_price_volatility(args.ledger, args.layers, args.commodity, args.out_png, args.out_csv)

if __name__ == "__main__":
    main() 