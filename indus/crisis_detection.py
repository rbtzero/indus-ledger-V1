#!/usr/bin/env python3
"""
CRISIS DETECTION SYSTEM
=======================
Component 4: Price shock and crisis detection
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
from scipy import stats
from collections import defaultdict

def detect_price_anomalies(weights_df, threshold=2.0):
    """Detect price anomalies using statistical methods"""
    print("🚨 CRISIS DETECTION ANALYSIS")
    print("=" * 27)
    
    anomalies = []
    
    # Group by sign for price analysis
    sign_groups = weights_df.groupby('sign')
    
    print(f"   📊 Analyzing {len(sign_groups)} sign groups")
    
    for sign, group in sign_groups:
        if len(group) < 5:  # Need minimum samples
            continue
            
        weights = group['weight'].values
        
        # Calculate z-scores
        z_scores = np.abs(stats.zscore(weights))
        
        # Detect outliers
        outlier_mask = z_scores > threshold
        outliers = group[outlier_mask]
        
        if len(outliers) > 0:
            for _, outlier in outliers.iterrows():
                anomalies.append({
                    'sign': sign,
                    'weight': outlier['weight'],
                    'z_score': z_scores[outlier.name - group.index[0]],
                    'type': 'high' if outlier['weight'] > weights.mean() else 'low',
                    'severity': 'critical' if z_scores[outlier.name - group.index[0]] > 3.0 else 'moderate'
                })
    
    anomalies_df = pd.DataFrame(anomalies)
    print(f"   🚨 Found {len(anomalies)} price anomalies")
    
    return anomalies_df

def analyze_crisis_periods(anomalies_df, weights_df):
    """Identify systemic crisis periods"""
    print(f"\n📈 CRISIS PERIOD ANALYSIS")
    print("=" * 26)
    
    # Count anomalies by sign to identify widespread crises
    crisis_signs = anomalies_df['sign'].value_counts()
    
    print("   SIGNS WITH MOST PRICE SHOCKS:")
    for i, (sign, count) in enumerate(crisis_signs.head(8).items()):
        severity_counts = anomalies_df[anomalies_df['sign'] == sign]['severity'].value_counts()
        critical = severity_counts.get('critical', 0)
        moderate = severity_counts.get('moderate', 0)
        print(f"      {i+1:2d}. Sign {sign:3d}: {count:2d} shocks ({critical}C/{moderate}M)")
    
    # Analyze by anomaly type
    type_analysis = anomalies_df.groupby(['type', 'severity']).size().unstack(fill_value=0)
    print(f"\n   ANOMALY TYPE BREAKDOWN:")
    for atype in ['high', 'low']:
        if atype in type_analysis.index:
            critical = type_analysis.loc[atype, 'critical'] if 'critical' in type_analysis.columns else 0
            moderate = type_analysis.loc[atype, 'moderate'] if 'moderate' in type_analysis.columns else 0
            print(f"      {atype.upper():4s} price shocks: {critical:2d} critical, {moderate:2d} moderate")
    
    return crisis_signs, type_analysis

def create_crisis_visualization(anomalies_df, weights_df, output_png):
    """Create crisis visualization plots"""
    print(f"\n📊 CREATING CRISIS VISUALIZATIONS")
    print("=" * 34)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Plot 1: Anomaly distribution by sign
    if len(anomalies_df) > 0:
        crisis_counts = anomalies_df['sign'].value_counts().head(15)
        ax1.bar(range(len(crisis_counts)), crisis_counts.values, color='red', alpha=0.7)
        ax1.set_title('Price Anomalies by Sign', fontweight='bold')
        ax1.set_xlabel('Sign (Top 15)')
        ax1.set_ylabel('Number of Anomalies')
        ax1.set_xticks(range(len(crisis_counts)))
        ax1.set_xticklabels([f"{sign}" for sign in crisis_counts.index], rotation=45)
    
    # Plot 2: Severity distribution
    if len(anomalies_df) > 0:
        severity_counts = anomalies_df['severity'].value_counts()
        colors = ['orange', 'red']
        ax2.pie(severity_counts.values, labels=severity_counts.index, autopct='%1.1f%%', colors=colors)
        ax2.set_title('Crisis Severity Distribution', fontweight='bold')
    
    # Plot 3: Weight distribution with anomalies highlighted
    all_weights = weights_df['weight'].values
    anomaly_weights = anomalies_df['weight'].values if len(anomalies_df) > 0 else []
    
    ax3.hist(all_weights, bins=30, alpha=0.7, color='blue', label='Normal weights')
    if len(anomaly_weights) > 0:
        ax3.hist(anomaly_weights, bins=15, alpha=0.8, color='red', label='Anomalous weights')
    ax3.set_title('Weight Distribution: Normal vs Anomalous', fontweight='bold')
    ax3.set_xlabel('Weight')
    ax3.set_ylabel('Frequency')
    ax3.legend()
    
    # Plot 4: Z-score distribution
    if len(anomalies_df) > 0:
        z_scores = anomalies_df['z_score'].values
        ax4.hist(z_scores, bins=20, color='purple', alpha=0.7)
        ax4.axvline(x=2.0, color='orange', linestyle='--', label='Moderate threshold')
        ax4.axvline(x=3.0, color='red', linestyle='--', label='Critical threshold')
        ax4.set_title('Z-Score Distribution of Anomalies', fontweight='bold')
        ax4.set_xlabel('Z-Score')
        ax4.set_ylabel('Frequency')
        ax4.legend()
    
    plt.tight_layout()
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Crisis plots saved: {output_png}")

def calculate_economic_stability(weights_df, anomalies_df):
    """Calculate overall economic stability metrics"""
    print(f"\n📊 ECONOMIC STABILITY METRICS")
    print("=" * 30)
    
    total_weights = len(weights_df)
    total_anomalies = len(anomalies_df)
    anomaly_rate = (total_anomalies / total_weights) * 100 if total_weights > 0 else 0
    
    critical_anomalies = len(anomalies_df[anomalies_df['severity'] == 'critical']) if len(anomalies_df) > 0 else 0
    critical_rate = (critical_anomalies / total_weights) * 100 if total_weights > 0 else 0
    
    # Calculate coefficient of variation by sign
    sign_cv = weights_df.groupby('sign')['weight'].apply(lambda x: x.std() / x.mean() if x.mean() != 0 else 0)
    avg_volatility = sign_cv.mean()
    
    # Stability score (inverse of volatility and anomaly rate)
    stability_score = max(0, 100 - (anomaly_rate * 2) - (critical_rate * 5) - (avg_volatility * 10))
    
    print(f"   📊 Total weights analyzed: {total_weights:,}")
    print(f"   🚨 Total anomalies found: {total_anomalies:,}")
    print(f"   📈 Anomaly rate: {anomaly_rate:.2f}%")
    print(f"   💥 Critical anomaly rate: {critical_rate:.2f}%")
    print(f"   📊 Average price volatility: {avg_volatility:.3f}")
    print(f"   🎯 Economic stability score: {stability_score:.1f}/100")
    
    return {
        'total_weights': total_weights,
        'total_anomalies': total_anomalies,
        'anomaly_rate': anomaly_rate,
        'critical_rate': critical_rate,
        'avg_volatility': avg_volatility,
        'stability_score': stability_score
    }

def main():
    parser = argparse.ArgumentParser(description='Detect price shocks and economic crises')
    parser.add_argument('--weights', required=True, help='Path to processed weights CSV')
    parser.add_argument('--out_csv', required=True, help='Output anomalies CSV')
    parser.add_argument('--out_png', required=True, help='Output crisis plots PNG')
    parser.add_argument('--threshold', type=float, default=2.0, help='Z-score threshold for anomalies')
    
    args = parser.parse_args()
    
    print("🚨 ECONOMIC CRISIS DETECTION SYSTEM")
    print("=" * 37)
    
    # Load weights data
    weights_df = pd.read_csv(args.weights)
    print(f"   📊 Loaded {len(weights_df)} weight records")
    
    # Detect anomalies
    anomalies_df = detect_price_anomalies(weights_df, threshold=args.threshold)
    
    # Analyze crisis periods
    if len(anomalies_df) > 0:
        crisis_signs, type_analysis = analyze_crisis_periods(anomalies_df, weights_df)
        
        # Create visualizations
        create_crisis_visualization(anomalies_df, weights_df, args.out_png)
        
        # Save anomalies
        anomalies_df.to_csv(args.out_csv, index=False)
    else:
        print("   ✅ No significant anomalies detected - stable economy")
        # Create empty files
        pd.DataFrame().to_csv(args.out_csv, index=False)
        plt.figure()
        plt.text(0.5, 0.5, 'No Anomalies Detected\nStable Economic System', 
                ha='center', va='center', fontsize=16, transform=plt.gca().transAxes)
        plt.savefig(args.out_png)
        plt.close()
    
    # Calculate stability metrics
    stability_metrics = calculate_economic_stability(weights_df, anomalies_df)
    
    print(f"\n🚨 CRISIS DETECTION COMPLETE")
    print("=" * 29)
    print(f"   📋 Anomalies saved: {args.out_csv}")
    print(f"   📊 Crisis plots saved: {args.out_png}")
    print(f"   🎯 Stability score: {stability_metrics['stability_score']:.1f}/100")
    
    return 0

if __name__ == "__main__":
    exit(main()) 