#!/usr/bin/env python3
import pandas as pd
import json
from collections import Counter, defaultdict
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.linear_model import LogisticRegression
import re

print("🔬 LEDGER-AWARE LINGUISTIC ANALYSIS")
print("=" * 36)
print("🎯 Testing: Genre vs Script Capability")

class LedgerAwareLinguistics:
    def __init__(self):
        self.load_comprehensive_data()
        self.setup_analysis_framework()
    
    def load_comprehensive_data(self):
        """Load all data with enhanced metadata"""
        print("\n📚 LOADING COMPREHENSIVE DATA:")
        
        # Load sequences
        with open('grammar/phon_seq.txt', 'r') as f:
            self.sequences = [line.strip() for line in f if line.strip()]
        
        # Load original sign data for cross-reference
        self.phoneme_df = pd.read_csv('output/phase_a_expanded_phoneme_table.csv')
        self.real_corpus_df = pd.read_csv('output/indus_proper_name_candidates.csv')
        self.ledger_df = pd.read_csv('data/ledger_en.tsv', sep='\t')
        
        # Create comprehensive phoneme mapping
        self.phoneme_dict = {}
        for _, row in self.phoneme_df.iterrows():
            if row['probability'] >= 0.7:
                sign_id = int(row['sign_id'])
                phoneme = str(row['phoneme'])
                self.phoneme_dict[sign_id] = phoneme
        
        print(f"✓ {len(self.sequences)} phoneme sequences")
        print(f"✓ {len(self.phoneme_dict)} high-confidence phoneme mappings")
        print(f"✓ {len(self.real_corpus_df)} archaeological inscriptions")
        
    def setup_analysis_framework(self):
        """Setup comprehensive analysis categories"""
        
        # Define semantic categories based on our translations
        self.semantic_categories = {
            'AUTHORITY': ['ra', 'ka', 'pa', 'ma'],  # king, person, father, mother
            'COMMODITY': ['ku', 'na', 'nan'],       # grain, river, water
            'ACTION': ['ta', 'da', 'ja', 'ya'],     # give, do, come, go
            'QUALIFIER': ['la', 'sa', 'cha'],       # small, sacred, sacred
            'LOCATION': ['ha', 'jha'],              # land, place
            'NUMERAL': []  # Will be identified by repetition patterns
        }
        
        # Reverse mapping for POS tagging
        self.morpheme_to_category = {}
        for category, morphemes in self.semantic_categories.items():
            for morpheme in morphemes:
                self.morpheme_to_category[morpheme] = category
        
        print(f"✓ Semantic framework: {len(self.morpheme_to_category)} categorized morphemes")
    
    def task_a_genre_segmented_zipf_test(self):
        """Task A: Genre-segmented Zipf test"""
        print(f"\n📊 TASK A: GENRE-SEGMENTED ZIPF TEST")
        print("=" * 37)
        
        # Classify sequences by genre
        commodity_sequences = []
        ritual_sequences = []
        other_sequences = []
        
        for seq in self.sequences:
            morphemes = seq.split()
            
            # Check for commodity patterns (AUTHORITY + COMMODITY + NUMERAL/QUALIFIER)
            has_authority = any(m in self.semantic_categories['AUTHORITY'] for m in morphemes)
            has_commodity = any(m in self.semantic_categories['COMMODITY'] for m in morphemes)
            has_repetition = len(morphemes) != len(set(morphemes))
            
            # Check for ritual patterns (SACRED + AUTHORITY + repetitive structure)
            has_sacred = any(m in ['sa', 'cha'] for m in morphemes)
            has_ritual_structure = has_sacred and (has_authority or has_repetition)
            
            if has_authority and has_commodity:
                commodity_sequences.append(seq)
            elif has_ritual_structure:
                ritual_sequences.append(seq)
            else:
                other_sequences.append(seq)
        
        print(f"✓ Commodity sequences: {len(commodity_sequences)}")
        print(f"✓ Ritual sequences: {len(ritual_sequences)}")
        print(f"✓ Other sequences: {len(other_sequences)}")
        
        # Test Zipf's law on each genre
        def test_zipf(sequences, genre_name):
            if len(sequences) < 10:
                return None, f"Too few {genre_name} sequences for Zipf test"
            
            # Get morpheme frequencies
            all_morphemes = []
            for seq in sequences:
                all_morphemes.extend(seq.split())
            
            freq_values = sorted(Counter(all_morphemes).values(), reverse=True)
            if len(freq_values) < 5:
                return None, f"Too few unique morphemes in {genre_name}"
            
            # Calculate Zipf ratios (rank * frequency / max_frequency)
            zipf_ratios = []
            max_freq = freq_values[0]
            for i, freq in enumerate(freq_values[:10], 1):
                ratio = (i * freq) / max_freq
                zipf_ratios.append(ratio)
            
            zipf_consistency = np.std(zipf_ratios)
            zipf_passes = zipf_consistency < 0.5
            
            return zipf_passes, f"Zipf std: {zipf_consistency:.3f}"
        
        # Test each genre
        commodity_zipf, commodity_msg = test_zipf(commodity_sequences, "commodity")
        ritual_zipf, ritual_msg = test_zipf(ritual_sequences, "ritual")
        other_zipf, other_msg = test_zipf(other_sequences, "other")
        
        print(f"\n🎯 ZIPF TEST RESULTS:")
        print(f"  Commodity genre: {'✅ PASSES' if commodity_zipf else '❌ FAILS'} ({commodity_msg})")
        print(f"  Ritual genre: {'✅ PASSES' if ritual_zipf else '❌ FAILS'} ({ritual_msg})")
        print(f"  Other genre: {'✅ PASSES' if other_zipf else '❌ FAILS'} ({other_msg})")
        
        return {
            'commodity_sequences': commodity_sequences,
            'ritual_sequences': ritual_sequences,
            'other_sequences': other_sequences,
            'zipf_results': {
                'commodity': commodity_zipf,
                'ritual': ritual_zipf,
                'other': other_zipf
            }
        }
    
    def task_b_template_mining(self):
        """Task B: Template mining with K-means clustering"""
        print(f"\n🔧 TASK B: TEMPLATE MINING")
        print("=" * 26)
        
        # Create POS tag sequences for clustering
        pos_sequences = []
        valid_sequences = []
        
        for seq in self.sequences:
            morphemes = seq.split()
            pos_tags = []
            
            for morpheme in morphemes:
                if morpheme in self.morpheme_to_category:
                    pos_tags.append(self.morpheme_to_category[morpheme])
                else:
                    # Try to identify numerals by repetition
                    if morphemes.count(morpheme) > 1:
                        pos_tags.append('NUMERAL')
                    else:
                        pos_tags.append('UNKNOWN')
            
            if pos_tags and 'UNKNOWN' not in pos_tags:  # Only use well-categorized sequences
                pos_sequences.append(pos_tags)
                valid_sequences.append(seq)
        
        print(f"✓ Categorized {len(pos_sequences)} sequences for clustering")
        
        if len(pos_sequences) < 10:
            return {'error': 'Too few categorized sequences for template analysis'}
        
        # Convert POS sequences to numerical vectors for clustering
        all_categories = list(self.semantic_categories.keys()) + ['NUMERAL']
        max_length = max(len(seq) for seq in pos_sequences)
        
        # Create feature vectors
        feature_vectors = []
        for pos_seq in pos_sequences:
            vector = [0] * (len(all_categories) * max_length)
            for i, pos in enumerate(pos_seq):
                if i < max_length and pos in all_categories:
                    cat_idx = all_categories.index(pos)
                    vector[i * len(all_categories) + cat_idx] = 1
            feature_vectors.append(vector)
        
        feature_vectors = np.array(feature_vectors)
        
        # Try different numbers of clusters
        best_score = -1
        best_k = 2
        silhouette_scores = {}
        
        for k in range(2, min(8, len(pos_sequences) // 2)):
            try:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(feature_vectors)
                score = silhouette_score(feature_vectors, cluster_labels)
                silhouette_scores[k] = score
                
                if score > best_score:
                    best_score = score
                    best_k = k
            except:
                continue
        
        # Final clustering with best k
        kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(feature_vectors)
        
        # Analyze templates
        templates = defaultdict(list)
        for i, label in enumerate(cluster_labels):
            templates[label].append((valid_sequences[i], pos_sequences[i]))
        
        print(f"\n🎯 TEMPLATE ANALYSIS RESULTS:")
        print(f"✓ Best cluster count: {best_k}")
        print(f"✓ Silhouette score: {best_score:.3f}")
        
        print(f"\n📋 DISCOVERED TEMPLATES:")
        for cluster_id, sequences in templates.items():
            print(f"\n  Template {cluster_id} ({len(sequences)} sequences):")
            # Show common POS pattern
            pos_patterns = [' '.join(pos_seq) for _, pos_seq in sequences]
            most_common_pattern = Counter(pos_patterns).most_common(1)[0]
            print(f"    Common pattern: {most_common_pattern[0]} ({most_common_pattern[1]} times)")
            
            # Show sample sequences
            for j, (seq, pos_seq) in enumerate(sequences[:3]):
                print(f"    {j+1}. {seq} → {' '.join(pos_seq)}")
        
        return {
            'best_k': best_k,
            'silhouette_score': best_score,
            'templates': dict(templates),
            'silhouette_scores': silhouette_scores
        }
    
    def task_c_cross_genre_hunt(self):
        """Task C: Hunt for non-economic inscriptions"""
        print(f"\n🔍 TASK C: CROSS-GENRE HUNT")
        print("=" * 27)
        
        # Look for sequences > 8 signs without obvious numerals/commerce
        long_sequences = []
        non_economic_candidates = []
        
        for seq in self.sequences:
            morphemes = seq.split()
            
            if len(morphemes) > 8:
                long_sequences.append(seq)
            
            # Check for non-economic indicators
            has_commerce = any(m in ['ta', 'ku', 'pa'] for m in morphemes)  # give, grain, father/agent
            has_repetition = len(morphemes) != len(set(morphemes))
            has_sacred_only = any(m in ['sa', 'cha', 'ma'] for m in morphemes) and not has_commerce
            
            if len(morphemes) >= 5 and (not has_commerce or has_sacred_only):
                non_economic_candidates.append(seq)
        
        print(f"✓ Long sequences (>8 morphemes): {len(long_sequences)}")
        print(f"✓ Non-economic candidates: {len(non_economic_candidates)}")
        
        # Re-run linguistic tests on non-economic subset
        if non_economic_candidates:
            print(f"\n🧪 LINGUISTIC TESTS ON NON-ECONOMIC SUBSET:")
            
            # Get morpheme frequencies from non-economic sequences
            all_morphemes = []
            for seq in non_economic_candidates:
                all_morphemes.extend(seq.split())
            
            morpheme_freq = Counter(all_morphemes)
            freq_values = sorted(morpheme_freq.values(), reverse=True)
            
            # Test Zipf's law
            if len(freq_values) >= 5:
                zipf_ratios = []
                max_freq = freq_values[0]
                for i, freq in enumerate(freq_values[:min(10, len(freq_values))], 1):
                    ratio = (i * freq) / max_freq
                    zipf_ratios.append(ratio)
                
                zipf_std = np.std(zipf_ratios)
                zipf_passes = zipf_std < 0.5
                
                print(f"  Zipf test: {'✅ PASSES' if zipf_passes else '❌ FAILS'} (std: {zipf_std:.3f})")
            else:
                print(f"  Zipf test: ❌ Too few morphemes ({len(freq_values)})")
            
            # Calculate TTR
            ttr = len(morpheme_freq) / len(all_morphemes)
            ttr_acceptable = 0.01 <= ttr <= 0.1  # Broader range for specialized texts
            print(f"  TTR: {'✅ ACCEPTABLE' if ttr_acceptable else '❌ ABNORMAL'} ({ttr:.4f})")
            
            # Show sample non-economic sequences
            print(f"\n📜 SAMPLE NON-ECONOMIC SEQUENCES:")
            for i, seq in enumerate(non_economic_candidates[:5]):
                morphemes = seq.split()
                print(f"  {i+1}. {seq} ({len(morphemes)} morphemes)")
        
        return {
            'long_sequences': long_sequences,
            'non_economic_candidates': non_economic_candidates,
            'analysis_performed': len(non_economic_candidates) > 0
        }
    
    def task_d_numeral_case_regression(self):
        """Task D: Test if affixes correlate with quantity"""
        print(f"\n📈 TASK D: NUMERAL-CASE REGRESSION")
        print("=" * 33)
        
        # Identify potential affixes and quantities
        affix_data = []
        
        for seq in self.sequences:
            morphemes = seq.split()
            
            # Count repetitions as quantity indicators
            quantity_score = 0
            for morpheme in set(morphemes):
                count = morphemes.count(morpheme)
                if count > 1:
                    quantity_score += count - 1
            
            # Look for potential affixes (end morphemes in specific contexts)
            if len(morphemes) >= 2:
                last_morpheme = morphemes[-1]
                
                # Check if last morpheme appears frequently in final position
                final_position_count = sum(1 for s in self.sequences 
                                         if s.split() and s.split()[-1] == last_morpheme)
                
                if final_position_count >= 5:  # Appears frequently at end
                    affix_data.append({
                        'sequence': seq,
                        'potential_affix': last_morpheme,
                        'quantity_score': quantity_score,
                        'has_quantity': quantity_score > 0,
                        'sequence_length': len(morphemes)
                    })
        
        print(f"✓ Identified {len(affix_data)} sequences with potential affixes")
        
        if len(affix_data) < 10:
            return {'error': 'Too few sequences for regression analysis'}
        
        # Prepare data for regression
        affix_types = list(set(item['potential_affix'] for item in affix_data))
        
        regression_results = {}
        for affix in affix_types:
            affix_subset = [item for item in affix_data if item['potential_affix'] == affix]
            
            if len(affix_subset) >= 5:
                # Prepare features and target
                X = np.array([[item['sequence_length']] for item in affix_subset])
                y = np.array([item['has_quantity'] for item in affix_subset])
                
                # Logistic regression
                try:
                    model = LogisticRegression(random_state=42)
                    model.fit(X, y)
                    
                    # Calculate significance (simplified)
                    quantity_rate = np.mean(y)
                    baseline_rate = np.mean([item['has_quantity'] for item in affix_data])
                    
                    regression_results[affix] = {
                        'count': len(affix_subset),
                        'quantity_rate': quantity_rate,
                        'baseline_rate': baseline_rate,
                        'effect_size': quantity_rate - baseline_rate,
                        'coefficient': model.coef_[0][0] if len(model.coef_[0]) > 0 else 0
                    }
                except:
                    regression_results[affix] = {'error': 'regression_failed'}
        
        print(f"\n🎯 AFFIX-QUANTITY CORRELATION RESULTS:")
        significant_affixes = []
        
        for affix, results in regression_results.items():
            if 'error' not in results:
                effect = results['effect_size']
                significant = abs(effect) > 0.2  # 20% difference from baseline
                
                print(f"  '{affix}': {results['quantity_rate']:.1%} quantity rate "
                      f"(baseline: {results['baseline_rate']:.1%}, "
                      f"effect: {effect:+.1%}) "
                      f"{'✅ SIGNIFICANT' if significant else '❌ NOT SIG'}")
                
                if significant:
                    significant_affixes.append(affix)
        
        return {
            'affix_data': affix_data,
            'regression_results': regression_results,
            'significant_affixes': significant_affixes
        }
    
    def generate_comprehensive_synthesis(self, results):
        """Generate comprehensive synthesis of all analyses"""
        print(f"\n🎯 COMPREHENSIVE SYNTHESIS")
        print("=" * 26)
        
        # Evaluate evidence for language capability
        language_evidence = []
        ledger_evidence = []
        
        # Task A results
        zipf_results = results['task_a']['zipf_results']
        if zipf_results.get('ritual') or zipf_results.get('other'):
            language_evidence.append("Zipf law satisfied in non-commodity genres")
        else:
            ledger_evidence.append("Zipf law fails across all genres")
        
        # Task B results
        if results['task_b'].get('silhouette_score', 0) > 0.5:
            ledger_evidence.append(f"Strong template structure (silhouette: {results['task_b']['silhouette_score']:.3f})")
        
        # Task C results
        if results['task_c']['non_economic_candidates']:
            language_evidence.append(f"Found {len(results['task_c']['non_economic_candidates'])} non-economic sequences")
        else:
            ledger_evidence.append("No non-economic sequences found")
        
        # Task D results
        if results['task_d'].get('significant_affixes'):
            language_evidence.append(f"Found {len(results['task_d']['significant_affixes'])} grammatical affixes")
        else:
            ledger_evidence.append("No grammatical affixes detected")
        
        # Calculate confidence scores
        total_tests = len(language_evidence) + len(ledger_evidence)
        language_score = len(language_evidence) / total_tests if total_tests > 0 else 0
        
        print(f"🏆 FINAL SYNTHESIS:")
        print(f"\n✅ EVIDENCE FOR LANGUAGE CAPABILITY:")
        for evidence in language_evidence:
            print(f"  • {evidence}")
        
        print(f"\n📊 EVIDENCE FOR LEDGER-ONLY SYSTEM:")
        for evidence in ledger_evidence:
            print(f"  • {evidence}")
        
        print(f"\n🎯 CONCLUSION:")
        if language_score >= 0.5:
            print(f"⚡ LANGUAGE-BEARING SCRIPT: Evidence suggests the Indus script")
            print(f"   could encode full language, but our corpus consists mainly")
            print(f"   of specialized accounting/ledger records.")
            conclusion = "LANGUAGE_BEARING_SCRIPT"
        else:
            print(f"📋 SPECIALIZED LEDGER SYSTEM: Evidence suggests the Indus")
            print(f"   script was primarily designed for accounting/commercial")
            print(f"   records, similar to Proto-Elamite.")
            conclusion = "SPECIALIZED_LEDGER"
        
        # Save comprehensive results
        final_report = {
            'conclusion': conclusion,
            'language_score': language_score,
            'language_evidence': language_evidence,
            'ledger_evidence': ledger_evidence,
            'detailed_results': results,
            'phonetic_scaffold_value': 'HIGH' if language_score >= 0.3 else 'MEDIUM'
        }
        
        # Convert numpy int32 keys to strings for JSON serialization
        def convert_keys(obj):
            if isinstance(obj, dict):
                return {str(k): convert_keys(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_keys(v) for v in obj]
            else:
                return obj
        
        serializable_report = convert_keys(final_report)
        
        with open('grammar/comprehensive_linguistic_analysis.json', 'w') as f:
            json.dump(serializable_report, f, indent=2, default=str)
        
        print(f"\n✅ COMPREHENSIVE ANALYSIS COMPLETE:")
        print(f"✓ Language capability score: {language_score:.2f}")
        print(f"✓ Phonetic scaffold remains {'highly' if language_score >= 0.3 else 'moderately'} valuable")
        print(f"✓ Saved complete analysis to grammar/comprehensive_linguistic_analysis.json")
        
        return final_report
    
    def run_complete_analysis(self):
        """Run all four tasks and generate synthesis"""
        print("\n" + "=" * 60)
        print("🚀 EXECUTING COMPLETE LEDGER-AWARE LINGUISTIC ANALYSIS")
        print("=" * 60)
        
        results = {}
        
        # Execute all tasks
        results['task_a'] = self.task_a_genre_segmented_zipf_test()
        results['task_b'] = self.task_b_template_mining()
        results['task_c'] = self.task_c_cross_genre_hunt()
        results['task_d'] = self.task_d_numeral_case_regression()
        
        # Generate synthesis
        final_report = self.generate_comprehensive_synthesis(results)
        
        return final_report

# Execute the complete analysis
if __name__ == "__main__":
    analyzer = LedgerAwareLinguistics()
    report = analyzer.run_complete_analysis() 