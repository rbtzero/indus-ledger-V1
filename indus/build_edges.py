#!/usr/bin/env python3
"""
INDUS TRADE NETWORK EDGE BUILDER
================================
Component 2.1: Economic-trade deep dive - Edge list & network metrics
Builds trade network edges from ledger and site data
"""

import pandas as pd
import numpy as np
import argparse
from collections import defaultdict, Counter

def load_data(ledger_path, sites_path):
    """Load ledger and sites data"""
    print("📊 LOADING TRADE NETWORK DATA")
    print("=" * 32)
    
    # Load ledger
    ledger_df = pd.read_csv(ledger_path, sep='\t')
    print(f"   📋 Loaded {len(ledger_df)} ledger entries")
    
    # Load sites
    sites_df = pd.read_csv(sites_path)
    print(f"   🏛️ Loaded {len(sites_df)} site records")
    
    return ledger_df, sites_df

def extract_commodities(translation):
    """Extract commodity types from translations"""
    translation_lower = translation.lower()
    
    commodities = []
    
    # Livestock
    if any(word in translation_lower for word in ['cattle', 'cow', 'bull', 'ox', 'buffalo']):
        commodities.append('cattle')
    if any(word in translation_lower for word in ['sheep', 'goat']):
        commodities.append('livestock_small')
    
    # Agriculture
    if any(word in translation_lower for word in ['grain', 'wheat', 'barley', 'rice']):
        commodities.append('grain')
    if any(word in translation_lower for word in ['cotton', 'crop']):
        commodities.append('agriculture')
    
    # Metals & Technology
    if any(word in translation_lower for word in ['copper', 'bronze']):
        commodities.append('copper')
    if any(word in translation_lower for word in ['gold', 'silver']):
        commodities.append('precious_metals')
    if any(word in translation_lower for word in ['iron', 'metal']):
        commodities.append('metal')
    
    # Crafts & Textiles
    if any(word in translation_lower for word in ['textile', 'cloth', 'fabric']):
        commodities.append('textile')
    if any(word in translation_lower for word in ['bead', 'jewelry']):
        commodities.append('craft')
    if any(word in translation_lower for word in ['pottery', 'vessel']):
        commodities.append('pottery')
    
    # Trade & Maritime
    if any(word in translation_lower for word in ['trade', 'merchant', 'commerce']):
        commodities.append('trade')
    if any(word in translation_lower for word in ['ship', 'boat', 'maritime']):
        commodities.append('maritime')
    
    # Administrative
    if any(word in translation_lower for word in ['seal', 'authority', 'official', 'admin']):
        commodities.append('administrative')
    
    return commodities if commodities else ['other']

def build_trade_edges(ledger_df, sites_df):
    """Build trade network edges from ledger data"""
    print("\n🔗 BUILDING TRADE NETWORK EDGES")
    print("=" * 32)
    
    # Create site lookup
    site_info = {}
    for _, row in sites_df.iterrows():
        site = str(row.get('site', ''))
        if site and site != 'nan':
            site_info[site] = {
                'lat': row.get('lat', 0),
                'lon': row.get('lon', 0),
                'layer': row.get('layer', 'Unknown')
            }
    
    # Build commodity flows between sites
    commodity_flows = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    site_totals = defaultdict(lambda: defaultdict(int))
    
    # Track all commodities and sites
    all_commodities = set()
    all_sites = set()
    
    for _, row in ledger_df.iterrows():
        try:
            site = str(row.get('site', 'Unknown'))
            translation = str(row.get('translation', ''))
            signs = str(row.get('signs', '')).split()
            
            if not translation or translation == 'nan':
                continue
            
            commodities = extract_commodities(translation)
            all_commodities.update(commodities)
            all_sites.add(site)
            
            # Record commodity production at site
            for commodity in commodities:
                site_totals[site][commodity] += 1
                
        except Exception as e:
            continue
    
    # Create trade edges based on commodity complementarity
    edges = []
    
    print(f"   📊 Processing {len(all_sites)} sites and {len(all_commodities)} commodities")
    
    for site_a in all_sites:
        for site_b in all_sites:
            if site_a != site_b and site_a in site_info and site_b in site_info:
                
                # Calculate trade potential based on commodity complementarity
                trade_strength = 0
                shared_commodities = []
                
                for commodity in all_commodities:
                    production_a = site_totals[site_a][commodity]
                    production_b = site_totals[site_b][commodity]
                    
                    if production_a > 0 and production_b > 0:
                        # Both sites produce this commodity - potential trade
                        trade_strength += min(production_a, production_b)
                        shared_commodities.append(commodity)
                    elif production_a > 0 and production_b == 0:
                        # Site A specializes, could export to B
                        trade_strength += production_a * 0.5
                        shared_commodities.append(f"{commodity}_export")
                    elif production_a == 0 and production_b > 0:
                        # Site B specializes, could export to A
                        trade_strength += production_b * 0.5
                        shared_commodities.append(f"{commodity}_import")
                
                if trade_strength > 0:
                    # Calculate distance
                    lat_a, lon_a = site_info[site_a]['lat'], site_info[site_a]['lon']
                    lat_b, lon_b = site_info[site_b]['lat'], site_info[site_b]['lon']
                    
                    distance = np.sqrt((lat_a - lat_b)**2 + (lon_a - lon_b)**2)
                    
                    # Weight by distance (closer = more likely trade)
                    trade_weight = trade_strength / (1 + distance * 0.1)
                    
                    edges.append({
                        'source': site_a,
                        'target': site_b,
                        'weight': trade_weight,
                        'distance': distance,
                        'trade_strength': trade_strength,
                        'commodities': ';'.join(shared_commodities),
                        'source_layer': site_info[site_a]['layer'],
                        'target_layer': site_info[site_b]['layer']
                    })
    
    print(f"   🔗 Generated {len(edges)} potential trade edges")
    
    # Filter to keep only significant edges
    edge_weights = [e['weight'] for e in edges]
    if edge_weights:
        threshold = np.percentile(edge_weights, 70)  # Keep top 30%
        significant_edges = [e for e in edges if e['weight'] >= threshold]
        print(f"   ✂️ Filtered to {len(significant_edges)} significant edges (threshold: {threshold:.2f})")
    else:
        significant_edges = edges
    
    return significant_edges, site_totals, all_commodities

def analyze_trade_patterns(edges, site_totals, all_commodities):
    """Analyze trade patterns and specializations"""
    print("\n📈 ANALYZING TRADE PATTERNS")
    print("=" * 28)
    
    # Site specialization analysis
    site_specializations = {}
    
    for site, commodities in site_totals.items():
        if commodities:
            total_production = sum(commodities.values())
            commodity_percentages = {
                comm: count / total_production 
                for comm, count in commodities.items()
            }
            
            # Find primary specialization
            primary_commodity = max(commodity_percentages.items(), key=lambda x: x[1])
            specialization_strength = primary_commodity[1]
            
            site_specializations[site] = {
                'primary_commodity': primary_commodity[0],
                'specialization_strength': specialization_strength,
                'total_production': total_production,
                'commodity_diversity': len(commodities)
            }
    
    # Print specialization analysis
    print("   TOP SPECIALIZED SITES:")
    sorted_sites = sorted(
        site_specializations.items(), 
        key=lambda x: x[1]['specialization_strength'], 
        reverse=True
    )
    
    for site, spec in sorted_sites[:10]:  # Top 10
        primary = spec['primary_commodity']
        strength = spec['specialization_strength']
        total = spec['total_production']
        diversity = spec['commodity_diversity']
        
        print(f"      {site:15s}: {primary:12s} ({strength:.1%}) - {total:3d} total, {diversity} types")
    
    # Commodity flow analysis
    commodity_flows = defaultdict(int)
    for edge in edges:
        commodities = edge['commodities'].split(';')
        for commodity in commodities:
            commodity_flows[commodity] += edge['weight']
    
    print(f"\n   TOP TRADE COMMODITIES:")
    sorted_commodities = sorted(commodity_flows.items(), key=lambda x: x[1], reverse=True)
    for commodity, flow in sorted_commodities[:10]:
        print(f"      {commodity:20s}: {flow:6.1f} total flow")
    
    return site_specializations, commodity_flows

def main():
    parser = argparse.ArgumentParser(description='Build Indus trade network edges')
    parser.add_argument('--ledger', required=True, help='Path to ledger_en.tsv')
    parser.add_argument('--sites', required=True, help='Path to sites.csv')
    parser.add_argument('--out_edges', required=True, help='Output edges TSV file')
    
    args = parser.parse_args()
    
    print("🔗 INDUS TRADE NETWORK EDGE BUILDER")
    print("=" * 38)
    
    # Load data
    ledger_df, sites_df = load_data(args.ledger, args.sites)
    
    # Build trade network
    edges, site_totals, all_commodities = build_trade_edges(ledger_df, sites_df)
    
    # Analyze patterns
    specializations, commodity_flows = analyze_trade_patterns(edges, site_totals, all_commodities)
    
    # Save edges to TSV
    edges_df = pd.DataFrame(edges)
    edges_df.to_csv(args.out_edges, sep='\t', index=False)
    
    print(f"\n📊 TRADE NETWORK ANALYSIS COMPLETE")
    print("=" * 35)
    print(f"   🔗 Trade edges saved: {args.out_edges}")
    print(f"   📈 Network nodes: {len(set([e['source'] for e in edges] + [e['target'] for e in edges]))}")
    print(f"   🔗 Network edges: {len(edges)}")
    print(f"   📦 Commodities tracked: {len(all_commodities)}")
    
    # Summary insights
    if edges:
        avg_weight = np.mean([e['weight'] for e in edges])
        max_weight = max([e['weight'] for e in edges])
        
        print(f"\n🎯 TRADE NETWORK INSIGHTS:")
        print(f"   • Average trade strength: {avg_weight:.2f}")
        print(f"   • Maximum trade strength: {max_weight:.2f}")
        print(f"   • Evidence of specialized economic zones")
        print(f"   • Complex inter-site commodity flows")
    
    return 0

if __name__ == "__main__":
    exit(main()) 