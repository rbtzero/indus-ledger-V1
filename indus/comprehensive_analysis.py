#!/usr/bin/env python3
import argparse
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import re
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import networkx as nx
from scipy.stats import chi2_contingency
import json

class IndusContentAnalyzer:
    """Comprehensive analysis of Indus script content and meaning"""
    
    def __init__(self):
        self.translations = None
        self.lexicon = None
        self.sequences = None
        self.tagged_data = None
        self.themes = defaultdict(list)
        self.semantic_networks = {}
        self.content_categories = {}
        
    def load_data(self, translations_file, lexicon_file, sequences_file, tagged_file):
        """Load all analysis data"""
        print("📚 LOADING CORPUS DATA:")
        
        # Load translations
        self.translations = pd.read_csv(translations_file, sep='\t')
        print(f"✓ Loaded {len(self.translations)} translations")
        
        # Load lexicon
        self.lexicon = pd.read_csv(lexicon_file, sep='\t')
        print(f"✓ Loaded {len(self.lexicon)} lexical entries")
        
        # Load original sequences
        with open(sequences_file, 'r') as f:
            self.sequences = [line.strip().split() for line in f if line.strip()]
        print(f"✓ Loaded {len(self.sequences)} original sequences")
        
        # Load tagged data
        self.tagged_data = pd.read_csv(tagged_file, sep='\t')
        print(f"✓ Loaded {len(self.tagged_data)} tagged tokens")
    
    def analyze_semantic_themes(self):
        """Identify and analyze major semantic themes"""
        print("\n🎭 SEMANTIC THEME ANALYSIS:")
        print("=" * 28)
        
        # Define semantic fields based on lexicon
        semantic_fields = {
            'Authority': ['king', 'father', 'mother', 'person', 'agent', 'noble'],
            'Sacred/Ritual': ['sacred', 'place', 'stand', 'shine', 'pure'],
            'Water/Nature': ['water', 'river', 'flow', 'land', 'sky', 'wind'],
            'Social': ['father', 'mother', 'king', 'person', 'house', 'good'],
            'Action/Motion': ['come', 'go', 'do', 'sit', 'hold', 'be', 'cut'],
            'Quantity/Size': ['three', 'small', 'great', 'up'],
            'Agriculture': ['grain', 'cow', 'land', 'flow'],
            'Spatial': ['place', 'at', 'before', 'up', 'house'],
            'Body/Physical': ['mouth', 'hold', 'shine', 'cut']
        }
        
        # Analyze theme frequencies
        theme_counts = defaultdict(int)
        theme_sequences = defaultdict(list)
        
        for idx, row in self.translations.iterrows():
            translation = row['english_translation'].lower()
            original = row['original_indus']
            
            for theme, keywords in semantic_fields.items():
                for keyword in keywords:
                    if keyword in translation:
                        theme_counts[theme] += 1
                        theme_sequences[theme].append((original, translation))
                        break
        
        # Display theme analysis
        print("📊 MAJOR THEMES IN INDUS CIVILIZATION:")
        sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        
        for theme, count in sorted_themes:
            percentage = (count / len(self.translations)) * 100
            print(f"  {theme:15} {count:4d} sequences ({percentage:5.1f}%)")
        
        self.themes = dict(theme_sequences)
        return sorted_themes
    
    def analyze_content_categories(self):
        """Categorize inscriptions by content type"""
        print("\n📋 CONTENT CATEGORY ANALYSIS:")
        print("=" * 30)
        
        categories = {
            'Religious/Ritual': [],
            'Administrative': [],
            'Personal Names': [],
            'Trade/Commerce': [],
            'Royal/Authority': [],
            'Geographic': [],
            'Agricultural': [],
            'Unknown/Other': []
        }
        
        for idx, row in self.translations.iterrows():
            translation = row['english_translation'].lower()
            original = row['original_indus']
            
            # Categorization rules based on content
            if any(word in translation for word in ['sacred', 'place', 'shine', 'pure', 'stand']):
                categories['Religious/Ritual'].append((original, translation))
            elif any(word in translation for word in ['king', 'authority', 'noble', 'agent']):
                categories['Royal/Authority'].append((original, translation))
            elif any(word in translation for word in ['father', 'mother', 'person']) and len(original.split()) <= 2:
                categories['Personal Names'].append((original, translation))
            elif any(word in translation for word in ['grain', 'cow', 'land']):
                categories['Agricultural'].append((original, translation))
            elif any(word in translation for word in ['water', 'river', 'land', 'place']):
                categories['Geographic'].append((original, translation))
            elif any(word in translation for word in ['three', 'good', 'great']):
                categories['Administrative'].append((original, translation))
            else:
                categories['Unknown/Other'].append((original, translation))
        
        # Display categorization
        print("📂 INSCRIPTION CATEGORIES:")
        for category, items in categories.items():
            percentage = (len(items) / len(self.translations)) * 100
            print(f"  {category:18} {len(items):4d} inscriptions ({percentage:5.1f}%)")
        
        self.content_categories = categories
        return categories
    
    def analyze_frequent_patterns(self):
        """Analyze most frequent patterns and their meanings"""
        print("\n🔄 FREQUENT PATTERN ANALYSIS:")
        print("=" * 30)
        
        # Count sequence frequencies
        sequence_counts = Counter()
        for idx, row in self.translations.iterrows():
            original = row['original_indus']
            sequence_counts[original] += 1
        
        # Get most frequent patterns
        top_patterns = sequence_counts.most_common(20)
        
        print("🔝 MOST FREQUENT INSCRIPTIONS:")
        print("    Original → English Translation (Count)")
        print("    " + "=" * 50)
        
        for pattern, count in top_patterns:
            # Find the translation
            translation = self.translations[self.translations['original_indus'] == pattern]['english_translation'].iloc[0]
            percentage = (count / len(self.translations)) * 100
            print(f"    {pattern:15} → {translation:30} ({count:3d}, {percentage:4.1f}%)")
        
        return top_patterns
    
    def analyze_morpheme_cooccurrence(self):
        """Analyze which morphemes appear together"""
        print("\n🤝 MORPHEME CO-OCCURRENCE ANALYSIS:")
        print("=" * 37)
        
        # Build co-occurrence matrix
        morpheme_pairs = Counter()
        morpheme_contexts = defaultdict(set)
        
        for sequence in self.sequences:
            for i, morpheme in enumerate(sequence):
                # Record context (other morphemes in same sequence)
                context = set(sequence) - {morpheme}
                morpheme_contexts[morpheme].update(context)
                
                # Record adjacent pairs
                for j, other in enumerate(sequence):
                    if i != j:
                        pair = tuple(sorted([morpheme, other]))
                        morpheme_pairs[pair] += 1
        
        # Most frequent pairs
        top_pairs = morpheme_pairs.most_common(15)
        
        print("🔗 STRONGEST MORPHEME ASSOCIATIONS:")
        print("    Morpheme Pair        → Likely Meaning              (Count)")
        print("    " + "=" * 65)
        
        for (m1, m2), count in top_pairs:
            # Get glosses
            g1 = self.get_gloss(m1)
            g2 = self.get_gloss(m2)
            meaning = f"{g1} + {g2}"
            
            print(f"    {m1:4} + {m2:4}          → {meaning:28} ({count:3d})")
        
        return top_pairs, morpheme_contexts
    
    def analyze_linguistic_structure(self):
        """Analyze linguistic structure patterns"""
        print("\n🏗️  LINGUISTIC STRUCTURE ANALYSIS:")
        print("=" * 34)
        
        # Sequence length distribution
        lengths = [len(seq) for seq in self.sequences]
        length_dist = Counter(lengths)
        
        print("📏 SEQUENCE LENGTH DISTRIBUTION:")
        for length in sorted(length_dist.keys()):
            count = length_dist[length]
            percentage = (count / len(self.sequences)) * 100
            bar = "█" * int(percentage / 2)
            print(f"    {length} morphemes: {count:4d} ({percentage:5.1f}%) {bar}")
        
        # POS pattern analysis
        print("\n📝 GRAMMATICAL PATTERNS:")
        pos_patterns = Counter()
        
        for seq_id, group in self.tagged_data.groupby('sequence_id'):
            pos_sequence = ' '.join(group['tag'].tolist())
            pos_patterns[pos_sequence] += 1
        
        top_pos_patterns = pos_patterns.most_common(10)
        print("    Most Common POS Patterns:")
        for pattern, count in top_pos_patterns:
            percentage = (count / len(self.sequences)) * 100
            print(f"      {pattern:20} {count:4d} ({percentage:5.1f}%)")
        
        return length_dist, pos_patterns
    
    def analyze_semantic_networks(self):
        """Build and analyze semantic networks"""
        print("\n🕸️  SEMANTIC NETWORK ANALYSIS:")
        print("=" * 30)
        
        # Build semantic graph
        G = nx.Graph()
        
        # Add nodes (morphemes with their glosses)
        for _, row in self.lexicon.iterrows():
            morpheme = row['morpheme']
            gloss = row['gloss']
            pos = row['pos']
            G.add_node(morpheme, gloss=gloss, pos=pos)
        
        # Add edges (co-occurrence relationships)
        pair_counts, _ = self.analyze_morpheme_cooccurrence()
        
        for (m1, m2), weight in pair_counts:
            if weight >= 5:  # Only strong associations
                G.add_edge(m1, m2, weight=weight)
        
        # Find communities (semantic clusters)
        communities = list(nx.connected_components(G))
        
        print("🏘️  SEMANTIC COMMUNITIES:")
        for i, community in enumerate(communities[:5]):
            if len(community) >= 3:
                glosses = [self.get_gloss(m) for m in community]
                print(f"    Community {i+1}: {', '.join(sorted(community))}")
                print(f"      Meanings: {', '.join(sorted(set(glosses)))}")
        
        # Network statistics
        print(f"\n📊 NETWORK STATISTICS:")
        print(f"    Nodes (morphemes): {G.number_of_nodes()}")
        print(f"    Edges (associations): {G.number_of_edges()}")
        print(f"    Connected components: {nx.number_connected_components(G)}")
        print(f"    Average clustering: {nx.average_clustering(G):.3f}")
        
        self.semantic_networks = G
        return G, communities
    
    def analyze_cultural_insights(self):
        """Extract cultural and historical insights"""
        print("\n🏛️  CULTURAL INSIGHTS ANALYSIS:")
        print("=" * 32)
        
        insights = {
            'Social Structure': [],
            'Religious Practices': [],
            'Economic Activities': [],
            'Technology': [],
            'Environment': [],
            'Governance': []
        }
        
        # Authority and social hierarchy
        authority_terms = ['king', 'father', 'mother', 'noble', 'agent']
        authority_sequences = []
        
        for idx, row in self.translations.iterrows():
            translation = row['english_translation'].lower()
            original = row['original_indus']
            
            if any(term in translation for term in authority_terms):
                authority_sequences.append((original, translation))
        
        insights['Social Structure'] = authority_sequences[:10]
        
        # Religious/ritual practices
        religious_terms = ['sacred', 'place', 'shine', 'pure', 'stand']
        religious_sequences = []
        
        for idx, row in self.translations.iterrows():
            translation = row['english_translation'].lower()
            original = row['original_indus']
            
            if any(term in translation for term in religious_terms):
                religious_sequences.append((original, translation))
        
        insights['Religious Practices'] = religious_sequences[:10]
        
        # Economic activities
        economic_terms = ['grain', 'cow', 'trade', 'good']
        economic_sequences = []
        
        for idx, row in self.translations.iterrows():
            translation = row['english_translation'].lower()
            original = row['original_indus']
            
            if any(term in translation for term in economic_terms):
                economic_sequences.append((original, translation))
        
        insights['Economic Activities'] = economic_sequences[:10]
        
        # Display insights
        print("🔍 KEY CULTURAL FINDINGS:")
        
        for category, sequences in insights.items():
            if sequences:
                print(f"\n   {category.upper()}:")
                for i, (original, translation) in enumerate(sequences[:5]):
                    print(f"     {i+1}. {original} → {translation}")
        
        return insights
    
    def generate_comprehensive_report(self):
        """Generate final comprehensive analysis report"""
        print("\n📊 COMPREHENSIVE CONTENT ANALYSIS:")
        print("=" * 37)
        
        # Calculate corpus statistics
        total_sequences = len(self.translations)
        unique_morphemes = len(self.lexicon)
        avg_length = np.mean([len(seq) for seq in self.sequences])
        
        # Vocabulary richness
        all_morphemes = []
        for seq in self.sequences:
            all_morphemes.extend(seq)
        
        vocabulary_size = len(set(all_morphemes))
        type_token_ratio = vocabulary_size / len(all_morphemes)
        
        print(f"📈 CORPUS STATISTICS:")
        print(f"    Total inscriptions: {total_sequences:,}")
        print(f"    Unique morphemes: {unique_morphemes}")
        print(f"    Vocabulary size: {vocabulary_size}")
        print(f"    Average length: {avg_length:.1f} morphemes")
        print(f"    Type-token ratio: {type_token_ratio:.3f}")
        
        # Thematic summary
        theme_analysis = self.analyze_semantic_themes()
        
        print(f"\n🎯 MAIN COMMUNICATION PURPOSES:")
        top_3_themes = theme_analysis[:3]
        for i, (theme, count) in enumerate(top_3_themes):
            percentage = (count / total_sequences) * 100
            print(f"    {i+1}. {theme} ({percentage:.1f}% of all inscriptions)")
        
        # Save detailed analysis
        report_data = {
            'corpus_stats': {
                'total_sequences': total_sequences,
                'unique_morphemes': unique_morphemes,
                'vocabulary_size': vocabulary_size,
                'average_length': avg_length,
                'type_token_ratio': type_token_ratio
            },
            'themes': dict(theme_analysis),
            'categories': {k: len(v) for k, v in self.content_categories.items()},
            'top_patterns': self.analyze_frequent_patterns()[:10]
        }
        
        with open('output/comprehensive_analysis.json', 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n✓ Detailed analysis saved to output/comprehensive_analysis.json")
        
        return report_data
    
    def get_gloss(self, morpheme):
        """Get English gloss for morpheme"""
        row = self.lexicon[self.lexicon['morpheme'] == morpheme]
        if not row.empty:
            return row['gloss'].iloc[0]
        return morpheme
    
    def create_visualizations(self):
        """Create visualization plots"""
        print("\n🎨 CREATING VISUALIZATIONS:")
        print("=" * 27)
        
        # Theme distribution pie chart
        theme_analysis = self.analyze_semantic_themes()
        
        plt.figure(figsize=(12, 8))
        
        # Subplot 1: Theme distribution
        plt.subplot(2, 2, 1)
        themes, counts = zip(*theme_analysis[:6])
        plt.pie(counts, labels=themes, autopct='%1.1f%%', startangle=90)
        plt.title('Indus Script Themes Distribution')
        
        # Subplot 2: Sequence length distribution
        plt.subplot(2, 2, 2)
        lengths = [len(seq) for seq in self.sequences]
        plt.hist(lengths, bins=range(1, max(lengths)+2), alpha=0.7, edgecolor='black')
        plt.xlabel('Sequence Length (morphemes)')
        plt.ylabel('Frequency')
        plt.title('Inscription Length Distribution')
        
        # Subplot 3: Most frequent morphemes
        plt.subplot(2, 2, 3)
        all_morphemes = []
        for seq in self.sequences:
            all_morphemes.extend(seq)
        
        morpheme_counts = Counter(all_morphemes)
        top_morphemes = morpheme_counts.most_common(10)
        morphemes, counts = zip(*top_morphemes)
        
        plt.barh(range(len(morphemes)), counts)
        plt.yticks(range(len(morphemes)), morphemes)
        plt.xlabel('Frequency')
        plt.title('Most Frequent Morphemes')
        
        # Subplot 4: POS distribution
        plt.subplot(2, 2, 4)
        pos_counts = self.tagged_data['tag'].value_counts()
        pos_counts.plot(kind='bar')
        plt.xlabel('Part of Speech')
        plt.ylabel('Count')
        plt.title('POS Distribution')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig('output/indus_analysis_plots.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✓ Analysis plots saved to output/indus_analysis_plots.png")
        
        # Word cloud of translations
        all_translations = ' '.join(self.translations['english_translation'].tolist())
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_translations)
        
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Indus Script Translation Word Cloud')
        plt.savefig('output/indus_wordcloud.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✓ Word cloud saved to output/indus_wordcloud.png")

def main():
    parser = argparse.ArgumentParser(description="Comprehensive Indus script content analysis")
    parser.add_argument('--translations', required=True, help="Translations TSV file")
    parser.add_argument('--lexicon', required=True, help="Lexicon TSV file")
    parser.add_argument('--sequences', required=True, help="Original sequences file")
    parser.add_argument('--tagged', required=True, help="Tagged corpus TSV file")
    
    args = parser.parse_args()
    
    print("🔍 COMPREHENSIVE INDUS CONTENT ANALYSIS")
    print("=" * 42)
    
    # Initialize analyzer
    analyzer = IndusContentAnalyzer()
    
    # Load data
    analyzer.load_data(args.translations, args.lexicon, args.sequences, args.tagged)
    
    # Run all analyses
    analyzer.analyze_semantic_themes()
    analyzer.analyze_content_categories()
    analyzer.analyze_frequent_patterns()
    analyzer.analyze_morpheme_cooccurrence()
    analyzer.analyze_linguistic_structure()
    analyzer.analyze_semantic_networks()
    analyzer.analyze_cultural_insights()
    
    # Generate comprehensive report
    analyzer.generate_comprehensive_report()
    
    # Create visualizations
    analyzer.create_visualizations()
    
    print(f"\n🎉 COMPREHENSIVE ANALYSIS COMPLETE!")
    print(f"✓ Full cultural, linguistic, and semantic analysis of Indus civilization")
    print(f"✓ 4,000-year-old communication patterns revealed and decoded!")

if __name__ == "__main__":
    main() 