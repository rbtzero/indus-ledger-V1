#!/usr/bin/env python3
"""SIGN SURVIVAL ANALYZER - Step 5.1"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse

def analyze_sign_survival(corpus_file, sites_file, out_png, out_csv):
    print("📈 SIGN SURVIVAL ANALYSIS")
    
    # Load data
    corpus_df = pd.read_csv(corpus_file, sep='\t')
    sites_df = pd.read_csv(sites_file)
    
    print(f"   📊 Loaded {len(corpus_df)} inscriptions, {len(sites_df)} sites")
    
    # Extract sign frequencies
    all_signs = []
    for _, row in corpus_df.iterrows():
        signs = str(row['signs']).split()
        all_signs.extend(signs)
    
    # Count frequencies
    sign_freq = pd.Series(all_signs).value_counts()
    
    # Calculate survival curves
    thresholds = range(1, min(15, int(sign_freq.max()) + 1))
    survival_data = []
    
    for threshold in thresholds:
        surviving = len(sign_freq[sign_freq >= threshold])
        survival_rate = (surviving / len(sign_freq)) * 100
        survival_data.append({
            'threshold': threshold,
            'surviving_signs': surviving,
            'survival_rate': survival_rate
        })
    
    survival_df = pd.DataFrame(survival_data)
    
    # Innovation metrics
    total_signs = len(sign_freq)
    rare_signs = len(sign_freq[sign_freq == 1])
    common_signs = len(sign_freq[sign_freq >= 3])
    
    innovation_rate = (rare_signs / total_signs) * 100
    standardization = (common_signs / total_signs) * 100
    
    print(f"   📝 Total signs: {total_signs}")
    print(f"   🔍 Rare (freq=1): {rare_signs} ({innovation_rate:.1f}%)")
    print(f"   📚 Common (freq≥3): {common_signs} ({standardization:.1f}%)")
    
    # Save data
    survival_df.to_csv(out_csv, index=False)
    
    # Create visualization
    plt.figure(figsize=(10, 6))
    plt.plot(survival_df['threshold'], survival_df['survival_rate'], 'b-o', linewidth=2)
    plt.title('Sign Survival Curve')
    plt.xlabel('Frequency Threshold')
    plt.ylabel('% Signs Surviving')
    plt.grid(True, alpha=0.3)
    plt.savefig(out_png)
    plt.close()
    
    print(f"✅ Complete: {out_csv}, {out_png}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus', required=True)
    parser.add_argument('--sites', required=True)
    parser.add_argument('--out_png', required=True)
    parser.add_argument('--out_csv', required=True)
    
    args = parser.parse_args()
    analyze_sign_survival(args.corpus, args.sites, args.out_png, args.out_csv)

if __name__ == "__main__":
    main() 