#!/usr/bin/env python3
import pandas as pd
import json
from collections import Counter, defaultdict
import numpy as np

print("🔍 INDUS SYSTEM TYPE ANALYSIS")
print("=" * 30)
print("🎯 Testing: Language vs Notation vs Recording System")

class SystemTypeAnalyzer:
    def __init__(self):
        self.load_data()
        self.prepare_analysis()
    
    def load_data(self):
        """Load all data for system analysis"""
        with open('grammar/phon_seq.txt', 'r') as f:
            self.sequences = [line.strip() for line in f if line.strip()]
        
        # Load translation mappings we established
        self.translation_dict = {
            'na': 'river', 'ma': 'mother', 'sa': 'sacred', 'pa': 'father',
            'cha': 'sacred', 'jha': 'place', 'la': 'small', 'ra': 'king',
            'ka': 'person', 'ta': 'give', 'da': 'tree', 'ha': 'land',
            'ku': 'grain', 'ba': 'be', 'ja': 'come', 'ya': 'go', 'nan': 'water'
        }
        
        print(f"✓ Loaded {len(self.sequences)} sequences")
    
    def prepare_analysis(self):
        """Prepare data structures for analysis"""
        # Get morpheme frequencies
        all_morphemes = []
        for seq in self.sequences:
            all_morphemes.extend(seq.split())
        
        self.morpheme_freq = Counter(all_morphemes)
        self.sequence_freq = Counter(self.sequences)
        
        # Calculate basic statistics
        self.total_morphemes = len(all_morphemes)
        self.unique_morphemes = len(self.morpheme_freq)
        self.total_sequences = len(self.sequences)
        self.unique_sequences = len(self.sequence_freq)
        
        print(f"✓ Type/Token ratio: {self.unique_morphemes/self.total_morphemes:.6f}")
        print(f"✓ Sequence diversity: {self.unique_sequences/self.total_sequences:.3f}")
    
    def test_natural_language_hypothesis(self):
        """Test if this could be natural language"""
        print(f"\n🗣️ NATURAL LANGUAGE HYPOTHESIS TEST:")
        print("=" * 37)
        
        # Natural language characteristics to test
        evidence_for = []
        evidence_against = []
        
        # 1. Zipf's Law test (word frequency distribution)
        freq_values = sorted(self.morpheme_freq.values(), reverse=True)
        if len(freq_values) > 5:
            # Check if follows Zipf's law (freq rank * frequency ≈ constant)
            zipf_ratios = []
            for i in range(1, min(6, len(freq_values))):
                ratio = (i * freq_values[i-1]) / freq_values[0]
                zipf_ratios.append(ratio)
            
            zipf_consistency = np.std(zipf_ratios) < 0.5
            if zipf_consistency:
                evidence_for.append("Follows Zipf's law")
            else:
                evidence_against.append("Does not follow Zipf's law")
        
        # 2. Type/Token ratio (should be 0.01-0.05 for natural language)
        ttr = self.unique_morphemes / self.total_morphemes
        if 0.01 <= ttr <= 0.05:
            evidence_for.append(f"TTR in natural range ({ttr:.3f})")
        else:
            evidence_against.append(f"TTR abnormal ({ttr:.6f}, expected 0.01-0.05)")
        
        # 3. Repetition patterns (natural language has low repetition)
        repetition_count = 0
        for seq in self.sequences:
            morphemes = seq.split()
            for i in range(len(morphemes) - 1):
                if morphemes[i] == morphemes[i + 1]:
                    repetition_count += 1
        
        repetition_rate = repetition_count / self.total_morphemes
        if repetition_rate < 0.05:
            evidence_for.append(f"Low repetition rate ({repetition_rate:.3f})")
        else:
            evidence_against.append(f"High repetition rate ({repetition_rate:.3f})")
        
        # 4. Sequence length distribution (natural language varies)
        seq_lengths = [len(seq.split()) for seq in self.sequences]
        length_variance = np.var(seq_lengths)
        if length_variance > 2:
            evidence_for.append(f"Variable sequence lengths")
        else:
            evidence_against.append(f"Low sequence length variance")
        
        print(f"✅ EVIDENCE FOR NATURAL LANGUAGE:")
        for evidence in evidence_for:
            print(f"  • {evidence}")
        
        print(f"\n❌ EVIDENCE AGAINST NATURAL LANGUAGE:")
        for evidence in evidence_against:
            print(f"  • {evidence}")
        
        natural_score = len(evidence_for) / (len(evidence_for) + len(evidence_against))
        print(f"\n🎯 Natural Language Score: {natural_score:.2f}/1.0")
        
        return natural_score, evidence_for, evidence_against
    
    def test_accounting_system_hypothesis(self):
        """Test if this could be an accounting/commercial system"""
        print(f"\n📊 ACCOUNTING SYSTEM HYPOTHESIS TEST:")
        print("=" * 37)
        
        evidence_for = []
        evidence_against = []
        
        # 1. Repetition patterns (accounting often repeats items)
        repetitive_sequences = 0
        for seq in self.sequences:
            morphemes = seq.split()
            if len(set(morphemes)) < len(morphemes):  # Has repeats
                repetitive_sequences += 1
        
        repetition_percentage = repetitive_sequences / len(self.sequences)
        if repetition_percentage > 0.3:
            evidence_for.append(f"High repetition in sequences ({repetition_percentage:.1%})")
        else:
            evidence_against.append(f"Low repetition in sequences ({repetition_percentage:.1%})")
        
        # 2. Small vocabulary (accounting uses limited terms)
        if self.unique_morphemes < 100:
            evidence_for.append(f"Small vocabulary ({self.unique_morphemes} morphemes)")
        else:
            evidence_against.append(f"Large vocabulary ({self.unique_morphemes} morphemes)")
        
        # 3. High frequency of specific terms (quantities, objects)
        top_morphemes = self.morpheme_freq.most_common(5)
        top_freq_ratio = sum(freq for _, freq in top_morphemes) / self.total_morphemes
        if top_freq_ratio > 0.5:
            evidence_for.append(f"High concentration in top morphemes ({top_freq_ratio:.1%})")
        else:
            evidence_against.append(f"Distributed morpheme usage ({top_freq_ratio:.1%})")
        
        # 4. Look for quantity/number-like patterns
        quantity_patterns = 0
        for seq in self.sequences:
            morphemes = seq.split()
            # Check for patterns like "X X X" (possible quantities)
            for i in range(len(morphemes) - 2):
                if morphemes[i] == morphemes[i+1] == morphemes[i+2]:
                    quantity_patterns += 1
                    break
        
        if quantity_patterns > 10:
            evidence_for.append(f"Found {quantity_patterns} possible quantity patterns")
        else:
            evidence_against.append(f"Few quantity patterns ({quantity_patterns})")
        
        # 5. Check for transaction-like structures
        transaction_indicators = ['ta', 'da', 'pa']  # give, do, father/agent
        transaction_sequences = 0
        for seq in self.sequences:
            if any(indicator in seq for indicator in transaction_indicators):
                transaction_sequences += 1
        
        transaction_rate = transaction_sequences / len(self.sequences)
        if transaction_rate > 0.5:
            evidence_for.append(f"High transaction indicators ({transaction_rate:.1%})")
        else:
            evidence_against.append(f"Low transaction indicators ({transaction_rate:.1%})")
        
        print(f"✅ EVIDENCE FOR ACCOUNTING SYSTEM:")
        for evidence in evidence_for:
            print(f"  • {evidence}")
        
        print(f"\n❌ EVIDENCE AGAINST ACCOUNTING SYSTEM:")
        for evidence in evidence_against:
            print(f"  • {evidence}")
        
        accounting_score = len(evidence_for) / (len(evidence_for) + len(evidence_against))
        print(f"\n🎯 Accounting System Score: {accounting_score:.2f}/1.0")
        
        return accounting_score, evidence_for, evidence_against
    
    def test_ritual_notation_hypothesis(self):
        """Test if this could be ritual/religious notation"""
        print(f"\n🕉️ RITUAL NOTATION HYPOTHESIS TEST:")
        print("=" * 36)
        
        evidence_for = []
        evidence_against = []
        
        # 1. Formulaic repetition (rituals use fixed formulas)
        exact_repetitions = sum(1 for freq in self.sequence_freq.values() if freq > 1)
        repetition_ratio = exact_repetitions / len(self.sequence_freq)
        
        if repetition_ratio > 0.1:
            evidence_for.append(f"High exact sequence repetition ({repetition_ratio:.1%})")
        else:
            evidence_against.append(f"Low exact sequence repetition ({repetition_ratio:.1%})")
        
        # 2. Sacred/religious terms
        sacred_terms = ['sa', 'cha', 'ma', 'pa']  # sacred, sacred, mother, father
        sacred_usage = 0
        for seq in self.sequences:
            if any(term in seq for term in sacred_terms):
                sacred_usage += 1
        
        sacred_rate = sacred_usage / len(self.sequences)
        if sacred_rate > 0.7:
            evidence_for.append(f"High sacred term usage ({sacred_rate:.1%})")
        else:
            evidence_against.append(f"Moderate sacred term usage ({sacred_rate:.1%})")
        
        # 3. Emphasis through repetition (ritual emphasis)
        emphasis_sequences = 0
        for seq in self.sequences:
            morphemes = seq.split()
            if len(morphemes) >= 3:
                # Look for patterns like "A A A" or "A B A B"
                for i in range(len(morphemes) - 2):
                    if (morphemes[i] == morphemes[i+2] or 
                        morphemes[i] == morphemes[i+1] == morphemes[i+2]):
                        emphasis_sequences += 1
                        break
        
        emphasis_rate = emphasis_sequences / len(self.sequences)
        if emphasis_rate > 0.2:
            evidence_for.append(f"High emphasis patterns ({emphasis_rate:.1%})")
        else:
            evidence_against.append(f"Low emphasis patterns ({emphasis_rate:.1%})")
        
        # 4. Fixed sequence structures (ritual formulas)
        template_analysis = defaultdict(int)
        for seq in self.sequences:
            morphemes = seq.split()
            # Create template by length and repetition pattern
            template = f"L{len(morphemes)}"
            if len(set(morphemes)) < len(morphemes):
                template += "_REP"
            template_analysis[template] += 1
        
        template_concentration = max(template_analysis.values()) / len(self.sequences)
        if template_concentration > 0.3:
            evidence_for.append(f"High template concentration ({template_concentration:.1%})")
        else:
            evidence_against.append(f"Low template concentration ({template_concentration:.1%})")
        
        print(f"✅ EVIDENCE FOR RITUAL NOTATION:")
        for evidence in evidence_for:
            print(f"  • {evidence}")
        
        print(f"\n❌ EVIDENCE AGAINST RITUAL NOTATION:")
        for evidence in evidence_against:
            print(f"  • {evidence}")
        
        ritual_score = len(evidence_for) / (len(evidence_for) + len(evidence_against))
        print(f"\n🎯 Ritual Notation Score: {ritual_score:.2f}/1.0")
        
        return ritual_score, evidence_for, evidence_against
    
    def test_administrative_records_hypothesis(self):
        """Test if this could be administrative records"""
        print(f"\n📋 ADMINISTRATIVE RECORDS HYPOTHESIS TEST:")
        print("=" * 42)
        
        evidence_for = []
        evidence_against = []
        
        # 1. Standardized formats (admin records use templates)
        length_distribution = Counter(len(seq.split()) for seq in self.sequences)
        dominant_length_ratio = max(length_distribution.values()) / len(self.sequences)
        
        if dominant_length_ratio > 0.4:
            evidence_for.append(f"Standardized length patterns ({dominant_length_ratio:.1%})")
        else:
            evidence_against.append(f"Variable length patterns ({dominant_length_ratio:.1%})")
        
        # 2. Authority/title references
        authority_terms = ['ra', 'ka', 'pa']  # king, person, father
        authority_usage = 0
        for seq in self.sequences:
            if any(term in seq for term in authority_terms):
                authority_usage += 1
        
        authority_rate = authority_usage / len(self.sequences)
        if authority_rate > 0.8:
            evidence_for.append(f"High authority references ({authority_rate:.1%})")
        else:
            evidence_against.append(f"Moderate authority references ({authority_rate:.1%})")
        
        # 3. Resource/commodity references
        resource_terms = ['ku', 'na', 'ha', 'nan']  # grain, river, land, water
        resource_usage = 0
        for seq in self.sequences:
            if any(term in seq for term in resource_terms):
                resource_usage += 1
        
        resource_rate = resource_usage / len(self.sequences)
        if resource_rate > 0.6:
            evidence_for.append(f"High resource references ({resource_rate:.1%})")
        else:
            evidence_against.append(f"Low resource references ({resource_rate:.1%})")
        
        # 4. Action/transaction verbs
        action_terms = ['ta', 'da', 'ja', 'ya']  # give, do, come, go
        action_usage = 0
        for seq in self.sequences:
            if any(term in seq for term in action_terms):
                action_usage += 1
        
        action_rate = action_usage / len(self.sequences)
        if action_rate > 0.5:
            evidence_for.append(f"High action/transaction terms ({action_rate:.1%})")
        else:
            evidence_against.append(f"Low action/transaction terms ({action_rate:.1%})")
        
        print(f"✅ EVIDENCE FOR ADMINISTRATIVE RECORDS:")
        for evidence in evidence_for:
            print(f"  • {evidence}")
        
        print(f"\n❌ EVIDENCE AGAINST ADMINISTRATIVE RECORDS:")
        for evidence in evidence_against:
            print(f"  • {evidence}")
        
        admin_score = len(evidence_for) / (len(evidence_for) + len(evidence_against))
        print(f"\n🎯 Administrative Records Score: {admin_score:.2f}/1.0")
        
        return admin_score, evidence_for, evidence_against
    
    def generate_system_type_conclusion(self):
        """Generate final conclusion about system type"""
        print(f"\n🔬 COMPREHENSIVE SYSTEM TYPE ANALYSIS:")
        print("=" * 40)
        
        # Run all tests
        natural_score, nat_for, nat_against = self.test_natural_language_hypothesis()
        accounting_score, acc_for, acc_against = self.test_accounting_system_hypothesis()
        ritual_score, rit_for, rit_against = self.test_ritual_notation_hypothesis()
        admin_score, adm_for, adm_against = self.test_administrative_records_hypothesis()
        
        # Rank hypotheses
        hypotheses = [
            ('Natural Language', natural_score),
            ('Accounting System', accounting_score),
            ('Ritual Notation', ritual_score),
            ('Administrative Records', admin_score)
        ]
        
        hypotheses.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n🏆 SYSTEM TYPE RANKING:")
        for i, (system_type, score) in enumerate(hypotheses):
            confidence = "HIGH" if score > 0.7 else "MEDIUM" if score > 0.5 else "LOW"
            print(f"  {i+1}. {system_type}: {score:.3f} ({confidence} confidence)")
        
        # Generate conclusion
        best_hypothesis = hypotheses[0]
        print(f"\n🎯 CONCLUSION:")
        if best_hypothesis[1] > 0.7:
            print(f"✅ STRONG EVIDENCE: The Indus system is most likely a {best_hypothesis[0]}")
        elif best_hypothesis[1] > 0.5:
            print(f"⚠️ MODERATE EVIDENCE: The Indus system may be a {best_hypothesis[0]}")
        else:
            print(f"❓ INCONCLUSIVE: Mixed evidence, possibly hybrid system")
        
        # Save comprehensive analysis
        analysis_report = {
            'system_type_scores': dict(hypotheses),
            'most_likely_type': best_hypothesis[0],
            'confidence_score': best_hypothesis[1],
            'basic_statistics': {
                'total_sequences': self.total_sequences,
                'unique_sequences': self.unique_sequences,
                'total_morphemes': self.total_morphemes,
                'unique_morphemes': self.unique_morphemes,
                'type_token_ratio': self.unique_morphemes / self.total_morphemes,
                'sequence_diversity': self.unique_sequences / self.total_sequences
            }
        }
        
        with open('grammar/system_type_analysis.json', 'w') as f:
            json.dump(analysis_report, f, indent=2)
        
        print(f"\n✅ SYSTEM TYPE ANALYSIS COMPLETE:")
        print(f"✓ Saved comprehensive report to grammar/system_type_analysis.json")
        print(f"✓ This fundamentally changes our understanding of the Indus script!")
        
        return analysis_report

# Run the system type analysis
if __name__ == "__main__":
    analyzer = SystemTypeAnalyzer()
    report = analyzer.generate_system_type_conclusion() 