#!/usr/bin/env python3
"""
resource_pair_entropy.py
Analyzes mutual information between resource pairs to identify ritual linkages
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import argparse
import json
from itertools import combinations
import matplotlib.pyplot as plt
import seaborn as sns

class ResourcePairEntropyAnalyzer:
    """Analyzes mutual information between resource pairs"""
    
    def __init__(self):
        self.resources = []
        self.resource_cooccurrence = defaultdict(lambda: defaultdict(int))
        
    def load_ledger(self, ledger_path, resource_list):
        """Load ledger and set resource list"""
        try:
            self.ledger = pd.read_csv(ledger_path, sep='\t')
            self.resources = resource_list
            print(f"✓ Loaded {len(self.ledger)} ledger entries")
            print(f"✓ Analyzing {len(self.resources)} resources: {', '.join(self.resources)}")
            return True
        except Exception as e:
            print(f"❌ Error loading ledger: {e}")
            return False
    
    def extract_resource_cooccurrences(self):
        """Extract resource co-occurrence patterns from translations"""
        print(f"\n🔍 EXTRACTING RESOURCE CO-OCCURRENCES")
        print("=" * 35)
        
        # Load translations
        try:
            translations = pd.read_csv('output/corrected_translations.tsv', sep='\t')
            print(f"✓ Using {len(translations)} translations")
            
            sequence_resources = []
            
            for _, row in translations.iterrows():
                translation = row['english_translation'].lower()
                original = row['original_indus']
                
                # Find all resources in this translation
                found_resources = [res for res in self.resources if res in translation]
                
                if found_resources:
                    sequence_resources.append({
                        'original': original,
                        'translation': translation,
                        'resources': found_resources,
                        'resource_count': len(found_resources)
                    })
                    
                    # Record co-occurrences
                    for res1, res2 in combinations(found_resources, 2):
                        self.resource_cooccurrence[res1][res2] += 1
                        self.resource_cooccurrence[res2][res1] += 1  # Symmetric
        
        except Exception as e:
            print(f"❌ Error loading translations: {e}")
            return [], {}
        
        print(f"📊 CO-OCCURRENCE ANALYSIS RESULTS:")
        print(f"   • Sequences with resources: {len(sequence_resources)}")
        print(f"   • Total co-occurrence pairs: {sum(len(pairs) for pairs in self.resource_cooccurrence.values()) // 2}")
        
        # Show top co-occurrences
        all_pairs = []
        for res1, pairs in self.resource_cooccurrence.items():
            for res2, count in pairs.items():
                if res1 < res2:  # Avoid duplicates
                    all_pairs.append((res1, res2, count))
        
        all_pairs.sort(key=lambda x: x[2], reverse=True)
        
        print(f"\n🔗 TOP RESOURCE CO-OCCURRENCES:")
        for i, (res1, res2, count) in enumerate(all_pairs[:5]):
            print(f"   {i+1}. {res1} ⇄ {res2}: {count} instances")
        
        return sequence_resources, dict(self.resource_cooccurrence)
    
    def calculate_mutual_information(self, sequence_resources):
        """Calculate mutual information matrix between resources"""
        print(f"\n📊 CALCULATING MUTUAL INFORMATION MATRIX")
        print("=" * 38)
        
        # Count individual resource frequencies
        resource_counts = Counter()
        total_sequences = len(sequence_resources)
        
        for seq in sequence_resources:
            for resource in seq['resources']:
                resource_counts[resource] += 1
        
        # Calculate mutual information for each pair
        mi_matrix = {}
        for resource in self.resources:
            mi_matrix[resource] = {}
        
        for res1 in self.resources:
            for res2 in self.resources:
                if res1 == res2:
                    mi_matrix[res1][res2] = 1.0  # Perfect correlation with self
                    continue
                
                # Count joint occurrences
                joint_count = self.resource_cooccurrence[res1][res2]
                
                # Calculate probabilities
                p_res1 = resource_counts[res1] / total_sequences if total_sequences > 0 else 0
                p_res2 = resource_counts[res2] / total_sequences if total_sequences > 0 else 0
                p_joint = joint_count / total_sequences if total_sequences > 0 else 0
                
                # Calculate mutual information
                if p_joint > 0 and p_res1 > 0 and p_res2 > 0:
                    mi = p_joint * np.log2(p_joint / (p_res1 * p_res2))
                    # Normalize by min entropy for easier interpretation
                    h_res1 = -p_res1 * np.log2(p_res1) if p_res1 > 0 else 0
                    h_res2 = -p_res2 * np.log2(p_res2) if p_res2 > 0 else 0
                    norm_mi = mi / min(h_res1, h_res2) if min(h_res1, h_res2) > 0 else 0
                else:
                    norm_mi = 0
                
                mi_matrix[res1][res2] = norm_mi
        
        print(f"🎯 MUTUAL INFORMATION RESULTS:")
        for res1 in self.resources:
            print(f"   {res1.upper()}:")
            for res2 in self.resources:
                if res1 != res2:
                    mi_val = mi_matrix[res1][res2]
                    print(f"      ⇄ {res2}: {mi_val:.3f}")
        
        return mi_matrix
    
    def analyze_ritual_linkages(self, mi_matrix, cooccurrence_data):
        """Analyze which commodities are ritually linked"""
        print(f"\n⛩️ RITUAL LINKAGE ANALYSIS")
        print("=" * 26)
        
        # Find strong linkages (high mutual information)
        strong_linkages = []
        moderate_linkages = []
        weak_linkages = []
        
        for res1 in self.resources:
            for res2 in self.resources:
                if res1 < res2:  # Avoid duplicates
                    mi_val = mi_matrix[res1][res2]
                    cooccur_count = cooccurrence_data.get(res1, {}).get(res2, 0)
                    
                    linkage_data = {
                        'resource1': res1,
                        'resource2': res2,
                        'mutual_information': mi_val,
                        'cooccurrence_count': cooccur_count,
                        'linkage_type': 'ritual'
                    }
                    
                    if mi_val >= 0.5:
                        strong_linkages.append(linkage_data)
                    elif mi_val >= 0.2:
                        moderate_linkages.append(linkage_data)
                    else:
                        weak_linkages.append(linkage_data)
        
        # Sort linkages by strength
        strong_linkages.sort(key=lambda x: x['mutual_information'], reverse=True)
        moderate_linkages.sort(key=lambda x: x['mutual_information'], reverse=True)
        
        print(f"🔥 STRONG RITUAL LINKAGES (MI ≥ 0.5):")
        for link in strong_linkages:
            print(f"   {link['resource1']} ⇄ {link['resource2']}")
            print(f"     MI: {link['mutual_information']:.3f}, Co-occur: {link['cooccurrence_count']}")
        
        print(f"\n🔸 MODERATE RITUAL LINKAGES (0.2 ≤ MI < 0.5):")
        for link in moderate_linkages[:5]:  # Top 5
            print(f"   {link['resource1']} ⇄ {link['resource2']}")
            print(f"     MI: {link['mutual_information']:.3f}, Co-occur: {link['cooccurrence_count']}")
        
        print(f"\n📊 LINKAGE SUMMARY:")
        print(f"   • Strong linkages: {len(strong_linkages)}")
        print(f"   • Moderate linkages: {len(moderate_linkages)}")
        print(f"   • Weak linkages: {len(weak_linkages)}")
        
        return strong_linkages, moderate_linkages, weak_linkages
    
    def create_ritual_network_model(self, strong_linkages, moderate_linkages):
        """Create a model of the ritual resource network"""
        print(f"\n🕸️ RITUAL RESOURCE NETWORK MODEL")
        print("=" * 32)
        
        # Analyze network structure
        network_nodes = set()
        for link in strong_linkages + moderate_linkages:
            network_nodes.add(link['resource1'])
            network_nodes.add(link['resource2'])
        
        # Identify central resources (highest connectivity)
        connectivity = defaultdict(int)
        for link in strong_linkages + moderate_linkages:
            connectivity[link['resource1']] += 1
            connectivity[link['resource2']] += 1
        
        # Rank by connectivity
        central_resources = sorted(connectivity.items(), key=lambda x: x[1], reverse=True)
        
        print(f"🌟 CENTRAL RITUAL RESOURCES:")
        for i, (resource, connections) in enumerate(central_resources):
            print(f"   {i+1}. {resource.upper()}: {connections} ritual connections")
        
        # Determine network type
        if len(strong_linkages) >= 3:
            network_type = "HIGHLY_INTEGRATED"
        elif len(strong_linkages) >= 1:
            network_type = "MODERATELY_INTEGRATED"
        else:
            network_type = "LOOSELY_CONNECTED"
        
        print(f"\n🏛️ NETWORK INTERPRETATION:")
        print(f"   Network Type: {network_type}")
        
        if network_type == "HIGHLY_INTEGRATED":
            print(f"   → Multiple strong ritual connections between commodities")
            print(f"   → Complex sacred-economy integration")
            print(f"   → Commodities have deep spiritual interdependence")
        elif network_type == "MODERATELY_INTEGRATED":
            print(f"   → Some ritual connections exist")
            print(f"   → Partial sacred-economy integration")
            print(f"   → Selected commodities are spiritually linked")
        else:
            print(f"   → Few ritual connections")
            print(f"   → Limited sacred-economy integration")
            print(f"   → Commodities mostly independent")
        
        return {
            'network_type': network_type,
            'central_resources': central_resources,
            'strong_linkages': strong_linkages,
            'moderate_linkages': moderate_linkages
        }
    
    def save_results(self, mi_matrix, linkage_analysis, output_path):
        """Save mutual information and linkage results"""
        print(f"\n💾 SAVING RESULTS TO {output_path}")
        
        results = {
            'mutual_information_matrix': mi_matrix,
            'strong_linkages': linkage_analysis['strong_linkages'],
            'moderate_linkages': linkage_analysis['moderate_linkages'],
            'network_type': linkage_analysis['network_type'],
            'central_resources': linkage_analysis['central_resources']
        }
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ Saved mutual information analysis to {output_path}")
        return True

def main():
    parser = argparse.ArgumentParser(description='Analyze mutual information between resource pairs')
    parser.add_argument('--ledger', required=True, help='Path to ledger file')
    parser.add_argument('--resources', required=True, help='Comma-separated resource list')
    parser.add_argument('--out_json', required=True, help='Output JSON path')
    
    args = parser.parse_args()
    
    print("🔗 RESOURCE PAIR ENTROPY ANALYSIS")
    print("=" * 34)
    print(f"Research Question: Which commodities are ritually linked?")
    
    # Parse resources
    resources = [r.strip() for r in args.resources.split(',')]
    
    analyzer = ResourcePairEntropyAnalyzer()
    
    # Load data
    if not analyzer.load_ledger(args.ledger, resources):
        return 1
    
    # Extract co-occurrences
    sequence_resources, cooccurrence_data = analyzer.extract_resource_cooccurrences()
    
    if not sequence_resources:
        print("❌ No resource co-occurrences found!")
        return 1
    
    # Calculate mutual information
    mi_matrix = analyzer.calculate_mutual_information(sequence_resources)
    
    # Analyze ritual linkages
    strong_linkages, moderate_linkages, weak_linkages = analyzer.analyze_ritual_linkages(mi_matrix, cooccurrence_data)
    
    # Create network model
    linkage_analysis = analyzer.create_ritual_network_model(strong_linkages, moderate_linkages)
    
    # Save results
    analyzer.save_results(mi_matrix, linkage_analysis, args.out_json)
    
    print(f"\n🎉 ENTROPY ANALYSIS COMPLETE!")
    print(f"📊 Ritual resource network model generated")
    
    return 0

if __name__ == "__main__":
    exit(main()) 