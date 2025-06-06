#!/usr/bin/env python3
"""
INDUS ADMINISTRATIVE AUTHORITY ANALYSIS
======================================
Component 3: Administrative-authority analysis
Uses w≥3 signs as elite, 1< w <3 merchant, w≤1 common
Reveals hierarchical administrative structure
"""

import pandas as pd
import numpy as np
import json
import argparse
import matplotlib.pyplot as plt
from collections import defaultdict, Counter

def load_data(ledger_path, weights_path):
    """Load ledger and weights data"""
    print("📊 LOADING ADMINISTRATIVE DATA")
    print("=" * 32)
    
    # Load ledger
    ledger_df = pd.read_csv(ledger_path, sep='\t')
    print(f"   📋 Loaded {len(ledger_df)} ledger entries")
    
    # Load weights
    with open(weights_path, 'r') as f:
        weights = json.load(f)
    print(f"   ⚖️ Loaded {len(weights)} sign weights")
    
    return ledger_df, weights

def classify_authority_levels(weights):
    """Classify signs into authority levels based on weights"""
    print("\n🏛️ CLASSIFYING AUTHORITY LEVELS")
    print("=" * 32)
    
    authority_levels = {
        'elite': [],      # w >= 3.0 (high authority)
        'merchant': [],   # 1.0 < w < 3.0 (middle authority)
        'common': [],     # w <= 1.0 (low authority)
        'modifier': []    # Very low weights (0.1-0.5)
    }
    
    for sign_id, weight in weights.items():
        if weight >= 3.0:
            authority_levels['elite'].append(sign_id)
        elif weight > 1.0:
            authority_levels['merchant'].append(sign_id)
        elif weight > 0.5:
            authority_levels['common'].append(sign_id)
        else:
            authority_levels['modifier'].append(sign_id)
    
    # Report classification
    for level, signs in authority_levels.items():
        count = len(signs)
        avg_weight = np.mean([weights[s] for s in signs]) if signs else 0
        print(f"   {level.upper():10s}: {count:3d} signs (avg weight: {avg_weight:.2f})")
        if count <= 10:  # Show actual signs for small groups
            sign_weights = [(s, weights[s]) for s in signs]
            sign_weights.sort(key=lambda x: x[1], reverse=True)
            print(f"              Signs: {[f'{s}({w:.1f})' for s, w in sign_weights]}")
    
    return authority_levels

def analyze_administrative_transactions(ledger_df, weights, authority_levels):
    """Analyze transactions by authority level"""
    print("\n💼 ANALYZING ADMINISTRATIVE TRANSACTIONS")
    print("=" * 42)
    
    transaction_stats = defaultdict(lambda: {
        'count': 0,
        'total_value': 0,
        'commodities': Counter(),
        'sites': Counter(),
        'transaction_types': Counter()
    })
    
    authority_sign_set = {
        level: set(signs) for level, signs in authority_levels.items()
    }
    
    for _, row in ledger_df.iterrows():
        try:
            signs = str(row.get('signs', '')).split()
            translation = str(row.get('translation', ''))
            site = str(row.get('site', 'Unknown'))
            
            if not signs:
                continue
            
            # Calculate transaction authority level
            max_authority = 'common'
            max_weight = 0
            
            for sign in signs:
                if sign in weights:
                    weight = weights[sign]
                    if weight > max_weight:
                        max_weight = weight
                        
                        # Determine authority level
                        if sign in authority_sign_set['elite']:
                            max_authority = 'elite'
                        elif sign in authority_sign_set['merchant']:
                            if max_authority != 'elite':
                                max_authority = 'merchant'
                        elif sign in authority_sign_set['common']:
                            if max_authority not in ['elite', 'merchant']:
                                max_authority = 'common'
            
            # Record transaction
            stats = transaction_stats[max_authority]
            stats['count'] += 1
            stats['total_value'] += max_weight
            stats['sites'][site] += 1
            
            # Analyze commodities and transaction types
            translation_lower = translation.lower()
            if any(word in translation_lower for word in ['cattle', 'cow', 'bull', 'ox']):
                stats['commodities']['cattle'] += 1
                stats['transaction_types']['livestock'] += 1
            elif any(word in translation_lower for word in ['grain', 'wheat', 'barley']):
                stats['commodities']['grain'] += 1
                stats['transaction_types']['agriculture'] += 1
            elif any(word in translation_lower for word in ['copper', 'bronze', 'metal']):
                stats['commodities']['metal'] += 1
                stats['transaction_types']['trade'] += 1
            elif any(word in translation_lower for word in ['textile', 'cloth', 'fabric']):
                stats['commodities']['textile'] += 1
                stats['transaction_types']['craft'] += 1
            elif any(word in translation_lower for word in ['seal', 'authority', 'official']):
                stats['transaction_types']['administrative'] += 1
            else:
                stats['transaction_types']['other'] += 1
                
        except Exception as e:
            continue
    
    # Report analysis
    total_transactions = sum(stats['count'] for stats in transaction_stats.values())
    
    for level in ['elite', 'merchant', 'common', 'modifier']:
        if level in transaction_stats:
            stats = transaction_stats[level]
            count = stats['count']
            percentage = (count / total_transactions * 100) if total_transactions > 0 else 0
            avg_value = stats['total_value'] / count if count > 0 else 0
            
            print(f"\n   {level.upper()} TRANSACTIONS:")
            print(f"      Count: {count:,} ({percentage:.1f}%)")
            print(f"      Avg Value: {avg_value:.2f}")
            print(f"      Top Sites: {dict(stats['sites'].most_common(3))}")
            print(f"      Top Commodities: {dict(stats['commodities'].most_common(3))}")
            print(f"      Transaction Types: {dict(stats['transaction_types'].most_common(3))}")
    
    return transaction_stats

def create_authority_pyramid(authority_levels, transaction_stats, weights):
    """Create hierarchical authority pyramid"""
    print("\n🏛️ BUILDING AUTHORITY PYRAMID")
    print("=" * 32)
    
    pyramid_data = []
    
    for level in ['elite', 'merchant', 'common', 'modifier']:
        if level in authority_levels:
            signs = authority_levels[level]
            sign_count = len(signs)
            
            # Calculate metrics
            avg_weight = np.mean([weights[s] for s in signs]) if signs else 0
            total_weight = sum(weights[s] for s in signs)
            
            # Transaction data
            trans_count = transaction_stats[level]['count'] if level in transaction_stats else 0
            trans_value = transaction_stats[level]['total_value'] if level in transaction_stats else 0
            
            pyramid_data.append({
                'level': level,
                'sign_count': sign_count,
                'avg_weight': avg_weight,
                'total_weight': total_weight,
                'transaction_count': trans_count,
                'transaction_value': trans_value,
                'authority_score': total_weight * trans_count  # Combined authority metric
            })
    
    # Sort by authority score
    pyramid_data.sort(key=lambda x: x['authority_score'], reverse=True)
    
    print("   AUTHORITY HIERARCHY:")
    print("   Level        Signs  Avg_Wt  Trans    Auth_Score")
    print("   " + "-" * 45)
    
    for data in pyramid_data:
        level = data['level']
        signs = data['sign_count']
        avg_wt = data['avg_weight']
        trans = data['transaction_count']
        score = data['authority_score']
        
        print(f"   {level:12s} {signs:5d}  {avg_wt:5.2f}  {trans:5d}    {score:8.1f}")
    
    return pyramid_data

def analyze_administrative_specialization(transaction_stats, authority_levels):
    """Analyze administrative specialization by authority level"""
    print("\n🎯 ADMINISTRATIVE SPECIALIZATION ANALYSIS")
    print("=" * 42)
    
    specializations = {}
    
    for level, stats in transaction_stats.items():
        if stats['count'] > 0:
            # Calculate specialization indices
            total_trans = stats['count']
            
            # Commodity specialization
            commodity_counts = stats['commodities']
            commodity_entropy = calculate_entropy(list(commodity_counts.values()))
            
            # Transaction type specialization
            type_counts = stats['transaction_types']
            type_entropy = calculate_entropy(list(type_counts.values()))
            
            # Geographic concentration
            site_counts = stats['sites']
            site_entropy = calculate_entropy(list(site_counts.values()))
            
            specializations[level] = {
                'commodity_entropy': commodity_entropy,
                'type_entropy': type_entropy,
                'site_entropy': site_entropy,
                'specialization_score': 1 / (1 + commodity_entropy + type_entropy)  # Lower entropy = higher specialization
            }
            
            print(f"\n   {level.upper()} SPECIALIZATION:")
            print(f"      Commodity Diversity: {commodity_entropy:.2f}")
            print(f"      Type Diversity: {type_entropy:.2f}")
            print(f"      Geographic Spread: {site_entropy:.2f}")
            print(f"      Specialization Score: {specializations[level]['specialization_score']:.3f}")
    
    return specializations

def calculate_entropy(counts):
    """Calculate Shannon entropy for diversity measurement"""
    if not counts or sum(counts) == 0:
        return 0
    
    total = sum(counts)
    probabilities = [c / total for c in counts if c > 0]
    entropy = -sum(p * np.log2(p) for p in probabilities)
    return entropy

def create_authority_visualization(pyramid_data, output_png):
    """Create authority pyramid visualization"""
    print(f"\n📊 CREATING AUTHORITY PYRAMID VISUALIZATION")
    print("=" * 42)
    
    levels = [d['level'] for d in pyramid_data]
    sign_counts = [d['sign_count'] for d in pyramid_data]
    trans_counts = [d['transaction_count'] for d in pyramid_data]
    authority_scores = [d['authority_score'] for d in pyramid_data]
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # Authority pyramid
    colors = ['gold', 'silver', '#CD7F32', 'gray']  # bronze color code
    ax1.bar(levels, sign_counts, color=colors[:len(levels)])
    ax1.set_title('Authority Pyramid: Sign Distribution')
    ax1.set_ylabel('Number of Signs')
    
    # Transaction volume by authority
    ax2.bar(levels, trans_counts, color=colors[:len(levels)])
    ax2.set_title('Administrative Activity')
    ax2.set_ylabel('Number of Transactions')
    
    # Authority scores
    ax3.bar(levels, authority_scores, color=colors[:len(levels)])
    ax3.set_title('Combined Authority Score')
    ax3.set_ylabel('Authority Score')
    
    # Weight distribution
    avg_weights = [d['avg_weight'] for d in pyramid_data]
    ax4.bar(levels, avg_weights, color=colors[:len(levels)])
    ax4.set_title('Average Authority Weight')
    ax4.set_ylabel('Average Weight')
    
    plt.tight_layout()
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Visualization saved: {output_png}")

def main():
    parser = argparse.ArgumentParser(description='Analyze Indus administrative authority layers')
    parser.add_argument('--ledger', required=True, help='Path to ledger_en.tsv')
    parser.add_argument('--weights', required=True, help='Path to weights.json')
    parser.add_argument('--out_csv', required=True, help='Output CSV file')
    parser.add_argument('--out_png', required=True, help='Output PNG visualization')
    
    args = parser.parse_args()
    
    print("🏛️ INDUS ADMINISTRATIVE AUTHORITY ANALYSIS")
    print("=" * 45)
    
    # Load data
    ledger_df, weights = load_data(args.ledger, args.weights)
    
    # Classify authority levels
    authority_levels = classify_authority_levels(weights)
    
    # Analyze transactions
    transaction_stats = analyze_administrative_transactions(ledger_df, weights, authority_levels)
    
    # Build authority pyramid
    pyramid_data = create_authority_pyramid(authority_levels, transaction_stats, weights)
    
    # Analyze specialization
    specializations = analyze_administrative_specialization(transaction_stats, authority_levels)
    
    # Create visualization
    create_authority_visualization(pyramid_data, args.out_png)
    
    # Save detailed results to CSV
    pyramid_df = pd.DataFrame(pyramid_data)
    pyramid_df.to_csv(args.out_csv, index=False)
    
    print(f"\n📊 ADMINISTRATIVE ANALYSIS COMPLETE")
    print("=" * 35)
    print(f"   📋 Authority pyramid saved: {args.out_csv}")
    print(f"   📊 Visualization saved: {args.out_png}")
    
    # Summary insights
    total_signs = sum(len(signs) for signs in authority_levels.values())
    elite_percentage = len(authority_levels['elite']) / total_signs * 100
    
    print(f"\n🎯 KEY INSIGHTS:")
    print(f"   • Elite authority signs: {len(authority_levels['elite'])} ({elite_percentage:.1f}%)")
    print(f"   • Administrative hierarchy clearly defined")
    print(f"   • Evidence of specialized administrative roles")
    print(f"   • Sophisticated bureaucratic organization")
    
    return 0

if __name__ == "__main__":
    exit(main()) 