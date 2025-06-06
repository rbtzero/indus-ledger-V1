#!/usr/bin/env python3
"""
INDUS VALLEY RELIGIOUS ICONOGRAPHY ANALYZER
==========================================
Systematic analysis of religious symbols, motifs, and sacred iconography
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from collections import defaultdict

def analyze_religious_symbols(signs_file, out_csv, out_png):
    print("🕉️ RELIGIOUS ICONOGRAPHY ANALYZER")
    print("=" * 35)
    
    # Load sign data
    signs_df = pd.read_csv(signs_file)
    print(f"   📜 Loaded {len(signs_df)} sign records")
    
    # Religious iconographic categories
    religious_categories = {
        'deity_figures': ['proto_shiva', 'mother_goddess', 'horned_deity', 'tree_spirit'],
        'sacred_animals': ['zebu_bull', 'water_buffalo', 'elephant', 'rhinoceros', 'tiger', 'serpent'],
        'ritual_objects': ['offering_stand', 'fire_altar', 'ritual_vessel', 'sacred_tree'],
        'cosmic_symbols': ['swastika', 'cross', 'star', 'wheel', 'spiral'],
        'water_symbols': ['fish', 'crocodile', 'water_vessel', 'lotus'],
        'fertility_symbols': ['phallus', 'yoni', 'pregnancy_figure', 'nursing_mother']
    }
    
    # Analyze iconographic patterns
    iconographic_analysis = {}
    
    for category, symbols in religious_categories.items():
        category_data = []
        category_frequency = 0
        
        for _, sign in signs_df.iterrows():
            sign_id = str(sign.get('id', ''))
            description = str(sign.get('description', '')).lower()
            iconographic = str(sign.get('iconographic', '')).lower()
            
            # Check if sign matches religious symbols
            for symbol in symbols:
                if symbol.lower() in description or symbol.lower() in iconographic:
                    category_data.append({
                        'sign_id': sign_id,
                        'symbol_type': symbol,
                        'frequency': sign.get('frequency', 1),
                        'sites': sign.get('sites', 'unknown'),
                        'interpretation': get_religious_interpretation(symbol)
                    })
                    category_frequency += sign.get('frequency', 1)
        
        iconographic_analysis[category] = {
            'symbols': category_data,
            'total_frequency': category_frequency,
            'symbol_count': len(category_data),
            'religious_significance': get_category_significance(category)
        }
    
    print(f"\n🔍 RELIGIOUS ICONOGRAPHY FINDINGS")
    print("=" * 34)
    
    for category, data in iconographic_analysis.items():
        print(f"   {category.upper().replace('_', ' ')}:")
        print(f"      Symbols found: {data['symbol_count']}")
        print(f"      Total frequency: {data['total_frequency']}")
        print(f"      Significance: {data['religious_significance']}")
        
        # Show top symbols in category
        if data['symbols']:
            sorted_symbols = sorted(data['symbols'], key=lambda x: x['frequency'], reverse=True)
            for i, symbol in enumerate(sorted_symbols[:3]):
                print(f"         {i+1}. {symbol['symbol_type']}: freq={symbol['frequency']} - {symbol['interpretation']}")
        print()
    
    # Sacred animal analysis
    sacred_animals = analyze_sacred_animals(iconographic_analysis)
    
    # Mother goddess cult analysis
    goddess_analysis = analyze_mother_goddess_cult(iconographic_analysis)
    
    # Water cult analysis
    water_cult = analyze_water_cult(iconographic_analysis)
    
    # Create comprehensive religious summary
    religious_summary = compile_religious_summary(iconographic_analysis, sacred_animals, goddess_analysis, water_cult)
    
    # Save analysis
    save_religious_analysis(iconographic_analysis, religious_summary, out_csv)
    
    # Create visualizations
    create_religious_visualizations(iconographic_analysis, religious_summary, out_png)
    
    print(f"✅ Religious iconography analysis complete: {out_csv}, {out_png}")
    return iconographic_analysis

def get_religious_interpretation(symbol):
    """Get religious interpretation of symbols"""
    interpretations = {
        'proto_shiva': 'Lord of Animals, meditation deity, fertility god',
        'mother_goddess': 'Great Mother, fertility goddess, earth deity',
        'horned_deity': 'Divine power, strength, cosmic authority',
        'zebu_bull': 'Sacred animal, virility, divine vehicle',
        'water_buffalo': 'Power, death/rebirth, aquatic divinity',
        'elephant': 'Wisdom, memory, rain-bringer',
        'tiger': 'Royal power, fierce protection',
        'serpent': 'Kundalini energy, earth wisdom, rebirth',
        'fish': 'Fertility, abundance, water life',
        'swastika': 'Solar symbol, cosmic order, good fortune',
        'tree_spirit': 'Tree of life, divine manifestation',
        'offering_stand': 'Ritual worship, divine offering',
        'fire_altar': 'Sacred fire, cosmic sacrifice',
        'lotus': 'Purity, divine birth, spiritual awakening'
    }
    return interpretations.get(symbol, 'Sacred symbol, divine significance')

def get_category_significance(category):
    """Get religious significance of categories"""
    significance = {
        'deity_figures': 'Central pantheon of Indus religious system',
        'sacred_animals': 'Divine vehicles and totemic worship',
        'ritual_objects': 'Active religious practice and ceremony',
        'cosmic_symbols': 'Universal order and divine geometry',
        'water_symbols': 'Water cult and purification rituals',
        'fertility_symbols': 'Life force and reproductive sacredness'
    }
    return significance.get(category, 'Important religious significance')

def analyze_sacred_animals(iconographic_analysis):
    """Detailed analysis of sacred animal worship"""
    print(f"🐘 SACRED ANIMAL CULT ANALYSIS")
    print("=" * 30)
    
    sacred_animals = iconographic_analysis.get('sacred_animals', {})
    animal_symbols = sacred_animals.get('symbols', [])
    
    # Animal hierarchy by frequency
    animal_freq = defaultdict(int)
    for animal in animal_symbols:
        animal_freq[animal['symbol_type']] += animal['frequency']
    
    # Sort by frequency
    sorted_animals = sorted(animal_freq.items(), key=lambda x: x[1], reverse=True)
    
    print(f"   📊 Animal worship hierarchy:")
    for i, (animal, freq) in enumerate(sorted_animals):
        print(f"      {i+1}. {animal.title()}: {freq} occurrences")
        interpretation = get_religious_interpretation(animal)
        print(f"         Religious role: {interpretation}")
    
    # Totemic analysis
    totemic_significance = {
        'zebu_bull': 'Primary divine vehicle, symbol of Shiva',
        'elephant': 'Wisdom deity, rain and fertility god',
        'tiger': 'Royal protector, fierce divine power',
        'water_buffalo': 'Death and rebirth deity, Yama association'
    }
    
    return {
        'hierarchy': sorted_animals,
        'totemic_roles': totemic_significance,
        'total_frequency': sum(animal_freq.values()),
        'diversity': len(animal_freq)
    }

def analyze_mother_goddess_cult(iconographic_analysis):
    """Analysis of Mother Goddess worship patterns"""
    print(f"👸 MOTHER GODDESS CULT ANALYSIS")
    print("=" * 32)
    
    fertility_symbols = iconographic_analysis.get('fertility_symbols', {})
    deity_figures = iconographic_analysis.get('deity_figures', {})
    
    goddess_indicators = []
    
    # Collect goddess-related symbols
    for symbol_data in fertility_symbols.get('symbols', []):
        if 'goddess' in symbol_data['symbol_type'] or 'mother' in symbol_data['symbol_type']:
            goddess_indicators.append(symbol_data)
    
    for symbol_data in deity_figures.get('symbols', []):
        if 'goddess' in symbol_data['symbol_type'] or 'mother' in symbol_data['symbol_type']:
            goddess_indicators.append(symbol_data)
    
    # Fertility cult significance
    fertility_freq = fertility_symbols.get('total_frequency', 0)
    goddess_freq = sum(ind['frequency'] for ind in goddess_indicators)
    
    print(f"   👸 Goddess worship indicators:")
    print(f"      Direct goddess figures: {len(goddess_indicators)}")
    print(f"      Fertility symbol frequency: {fertility_freq}")
    print(f"      Goddess-specific frequency: {goddess_freq}")
    
    # Mother Goddess characteristics
    goddess_aspects = {
        'fertility': 'Life-giving power, agricultural abundance',
        'protection': 'Maternal care, community guardian',
        'earth_deity': 'Earth mother, natural cycles',
        'water_goddess': 'River goddess, purification'
    }
    
    return {
        'indicators': goddess_indicators,
        'fertility_emphasis': fertility_freq,
        'goddess_frequency': goddess_freq,
        'aspects': goddess_aspects,
        'significance': 'Central maternal deity in Indus pantheon'
    }

def analyze_water_cult(iconographic_analysis):
    """Analysis of water worship and purification rituals"""
    print(f"💧 WATER CULT ANALYSIS")
    print("=" * 21)
    
    water_symbols = iconographic_analysis.get('water_symbols', {})
    water_freq = water_symbols.get('total_frequency', 0)
    water_types = water_symbols.get('symbols', [])
    
    print(f"   💧 Water worship evidence:")
    print(f"      Water symbols found: {len(water_types)}")
    print(f"      Total frequency: {water_freq}")
    
    # Water ritual significance
    water_practices = {
        'ritual_bathing': 'Great Bath of Mohenjo-daro, purification ceremonies',
        'water_worship': 'River goddess veneration, sacred wells',
        'fertility_rites': 'Water and agricultural fertility connection',
        'purification': 'Spiritual cleansing, ritual purity'
    }
    
    # Aquatic symbols
    aquatic_symbolism = {}
    for symbol in water_types:
        aquatic_symbolism[symbol['symbol_type']] = symbol['interpretation']
    
    return {
        'water_frequency': water_freq,
        'symbol_diversity': len(water_types),
        'ritual_practices': water_practices,
        'aquatic_symbols': aquatic_symbolism,
        'significance': 'Central water cult with ritual purification'
    }

def compile_religious_summary(iconographic_analysis, sacred_animals, goddess_analysis, water_cult):
    """Compile comprehensive religious system summary"""
    print(f"\n🕉️ COMPREHENSIVE RELIGIOUS SYSTEM")
    print("=" * 35)
    
    # Calculate overall religious activity
    total_religious_freq = sum(cat['total_frequency'] for cat in iconographic_analysis.values())
    total_symbol_count = sum(cat['symbol_count'] for cat in iconographic_analysis.values())
    
    # Religious system characteristics
    religious_system = {
        'pantheon_type': 'Polytheistic with mother goddess emphasis',
        'primary_deities': ['Mother Goddess', 'Proto-Shiva', 'Animal spirits'],
        'sacred_animals': sacred_animals['hierarchy'][:5],
        'ritual_practices': ['Water worship', 'Fire ceremonies', 'Fertility rites'],
        'cosmic_beliefs': ['Divine order', 'Natural cycles', 'Spiritual purity'],
        'cultural_values': ['Fertility', 'Purification', 'Divine protection']
    }
    
    # Religious sophistication metrics
    sophistication_metrics = {
        'symbol_diversity': total_symbol_count,
        'religious_frequency': total_religious_freq,
        'pantheon_complexity': len(iconographic_analysis),
        'ritual_evidence': len(religious_system['ritual_practices']),
        'cultural_integration': 'High - pervasive religious symbolism'
    }
    
    print(f"   🎯 Religious system characteristics:")
    print(f"      Pantheon type: {religious_system['pantheon_type']}")
    print(f"      Primary deities: {', '.join(religious_system['primary_deities'])}")
    print(f"      Sacred animal diversity: {sacred_animals['diversity']} species")
    print(f"      Total religious symbols: {total_symbol_count}")
    print(f"      Religious symbol frequency: {total_religious_freq}")
    
    return {
        'system_type': religious_system,
        'sophistication': sophistication_metrics,
        'goddess_cult': goddess_analysis,
        'animal_worship': sacred_animals,
        'water_cult': water_cult
    }

def save_religious_analysis(iconographic_analysis, religious_summary, out_csv):
    """Save religious analysis to CSV"""
    religious_data = []
    
    for category, data in iconographic_analysis.items():
        for symbol in data['symbols']:
            religious_data.append({
                'category': category,
                'symbol_type': symbol['symbol_type'],
                'sign_id': symbol['sign_id'],
                'frequency': symbol['frequency'],
                'sites': symbol['sites'],
                'interpretation': symbol['interpretation'],
                'religious_significance': data['religious_significance']
            })
    
    religious_df = pd.DataFrame(religious_data)
    religious_df.to_csv(out_csv, index=False)

def create_religious_visualizations(iconographic_analysis, religious_summary, out_png):
    """Create religious iconography visualizations"""
    print(f"\n📊 CREATING RELIGIOUS VISUALIZATIONS")
    print("=" * 37)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Plot 1: Religious category distribution
    categories = list(iconographic_analysis.keys())
    frequencies = [iconographic_analysis[cat]['total_frequency'] for cat in categories]
    
    ax1.pie(frequencies, labels=[cat.replace('_', ' ').title() for cat in categories], 
            autopct='%1.1f%%', startangle=90)
    ax1.set_title('Religious Symbol Distribution', fontweight='bold', fontsize=14)
    
    # Plot 2: Sacred animal hierarchy
    sacred_animals = religious_summary['animal_worship']['hierarchy']
    if sacred_animals:
        animals, freqs = zip(*sacred_animals[:8])
        ax2.barh(range(len(animals)), freqs, color='brown', alpha=0.7)
        ax2.set_yticks(range(len(animals)))
        ax2.set_yticklabels([animal.replace('_', ' ').title() for animal in animals])
        ax2.set_title('Sacred Animal Worship Hierarchy', fontweight='bold', fontsize=14)
        ax2.set_xlabel('Frequency')
    
    # Plot 3: Religious symbol counts by category
    symbol_counts = [iconographic_analysis[cat]['symbol_count'] for cat in categories]
    ax3.bar(range(len(categories)), symbol_counts, color='purple', alpha=0.7)
    ax3.set_xticks(range(len(categories)))
    ax3.set_xticklabels([cat.replace('_', ' ').title() for cat in categories], rotation=45, ha='right')
    ax3.set_title('Religious Symbol Diversity by Category', fontweight='bold', fontsize=14)
    ax3.set_ylabel('Number of Different Symbols')
    
    # Plot 4: Religious sophistication metrics
    sophistication = religious_summary['sophistication']
    metrics = ['Symbol\nDiversity', 'Religious\nFrequency', 'Pantheon\nComplexity', 'Ritual\nEvidence']
    values = [
        sophistication['symbol_diversity'],
        sophistication['religious_frequency'] / 10,  # Scale for visualization
        sophistication['pantheon_complexity'] * 5,   # Scale for visualization  
        sophistication['ritual_evidence'] * 10       # Scale for visualization
    ]
    
    ax4.bar(metrics, values, color=['blue', 'green', 'orange', 'red'], alpha=0.7)
    ax4.set_title('Religious System Sophistication Metrics', fontweight='bold', fontsize=14)
    ax4.set_ylabel('Scaled Values')
    
    plt.tight_layout()
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    parser = argparse.ArgumentParser(description='Analyze Indus Valley religious iconography')
    parser.add_argument('--signs', required=True, help='Signs CSV file')
    parser.add_argument('--out_csv', required=True, help='Output religious analysis CSV')
    parser.add_argument('--out_png', required=True, help='Output religious visualization PNG')
    
    args = parser.parse_args()
    analyze_religious_symbols(args.signs, args.out_csv, args.out_png)

if __name__ == "__main__":
    main() 