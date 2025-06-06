#!/usr/bin/env python3
"""
truth_detector.py
Critical analysis: Religious vs Secular/Pragmatic interpretation of Indus society
Searches for ACTUAL evidence without imposing frameworks
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import json
import re

class IndusRealityDetector:
    """Analyzes actual evidence for religious vs secular/pragmatic society"""
    
    def __init__(self):
        self.religious_indicators = []
        self.secular_indicators = []
        self.pragmatic_indicators = []
        self.liberal_indicators = []
        
    def load_all_data(self):
        """Load all available data sources"""
        print("📚 LOADING ALL EVIDENCE SOURCES")
        print("=" * 32)
        
        try:
            self.translations = pd.read_csv('output/corrected_translations.tsv', sep='\t')
            print(f"✓ Translations: {len(self.translations)} records")
        except:
            print("❌ No translations found")
            return False
        
        try:
            self.corpus = pd.read_csv('data/corpus.tsv', sep='\t', names=['id', 'sequence'])
            print(f"✓ Corpus: {len(self.corpus)} sequences")
        except:
            print("❌ No corpus found")
        
        try:
            self.ledger = pd.read_csv('data/ledger_en.tsv', sep='\t')
            print(f"✓ Ledger: {len(self.ledger)} entries")
        except:
            print("❌ No ledger found")
        
        try:
            with open('data/weights.json', 'r') as f:
                self.weights = json.load(f)
            print(f"✓ Sign weights: {len(self.weights)} signs")
        except:
            print("❌ No weights found")
        
        return True
    
    def analyze_actual_content_without_bias(self):
        """Analyze what the translations ACTUALLY say, without religious assumptions"""
        print(f"\n🔍 UNBIASED CONTENT ANALYSIS")
        print("=" * 27)
        
        # Look for ACTUAL religious terms vs practical terms
        actual_religious_terms = [
            'sacred', 'holy', 'divine', 'god', 'goddess', 'temple', 'priest', 'worship', 
            'ritual', 'ceremony', 'blessing', 'prayer', 'offering', 'sacrifice'
        ]
        
        actual_practical_terms = [
            'trade', 'sell', 'buy', 'price', 'cost', 'payment', 'exchange', 'market',
            'store', 'warehouse', 'count', 'measure', 'weight', 'quantity', 'amount'
        ]
        
        organizational_terms = [
            'agreement', 'contract', 'rule', 'law', 'permit', 'allow', 'authorize',
            'certificate', 'document', 'record', 'register', 'official', 'formal'
        ]
        
        family_social_terms = [
            'father', 'mother', 'child', 'family', 'house', 'person', 'people',
            'community', 'group', 'together', 'share', 'help', 'cooperate'
        ]
        
        # Count actual occurrences
        religious_count = 0
        practical_count = 0
        organizational_count = 0
        family_social_count = 0
        
        religious_examples = []
        practical_examples = []
        organizational_examples = []
        family_examples = []
        
        for _, row in self.translations.iterrows():
            translation = row['english_translation'].lower()
            original = row['original_indus']
            
            # Check for actual religious content
            found_religious = [term for term in actual_religious_terms if term in translation]
            if found_religious:
                religious_count += len(found_religious)
                religious_examples.append({
                    'original': original,
                    'translation': translation,
                    'religious_terms': found_religious
                })
            
            # Check for practical/commercial content
            found_practical = [term for term in actual_practical_terms if term in translation]
            if found_practical:
                practical_count += len(found_practical)
                practical_examples.append({
                    'original': original,
                    'translation': translation,
                    'practical_terms': found_practical
                })
            
            # Check for organizational content
            found_organizational = [term for term in organizational_terms if term in translation]
            if found_organizational:
                organizational_count += len(found_organizational)
                organizational_examples.append({
                    'original': original,
                    'translation': translation,
                    'organizational_terms': found_organizational
                })
            
            # Check for family/social content
            found_family = [term for term in family_social_terms if term in translation]
            if found_family:
                family_social_count += len(found_family)
                family_examples.append({
                    'original': original,
                    'translation': translation,
                    'family_terms': found_family
                })
        
        print(f"📊 ACTUAL CONTENT ANALYSIS RESULTS:")
        print(f"   🏛️ Religious terms: {religious_count} occurrences")
        print(f"   💼 Practical/Commercial terms: {practical_count} occurrences")
        print(f"   📋 Organizational terms: {organizational_count} occurrences")
        print(f"   👨‍👩‍👧‍👦 Family/Social terms: {family_social_count} occurrences")
        
        print(f"\n🔍 ACTUAL RELIGIOUS EXAMPLES:")
        for i, example in enumerate(religious_examples[:5]):
            print(f"   {i+1}. {example['original']} → {example['translation']}")
            print(f"      Religious terms: {example['religious_terms']}")
        
        print(f"\n💼 ACTUAL PRACTICAL EXAMPLES:")
        for i, example in enumerate(practical_examples[:5]):
            print(f"   {i+1}. {example['original']} → {example['translation']}")
            print(f"      Practical terms: {example['practical_terms']}")
        
        print(f"\n👨‍👩‍👧‍👦 FAMILY/SOCIAL EXAMPLES (Top 5):")
        for i, example in enumerate(family_examples[:5]):
            print(f"   {i+1}. {example['original']} → {example['translation']}")
            print(f"      Family terms: {example['family_terms']}")
        
        return {
            'religious_count': religious_count,
            'practical_count': practical_count,
            'organizational_count': organizational_count,
            'family_social_count': family_social_count,
            'religious_examples': religious_examples,
            'practical_examples': practical_examples,
            'family_examples': family_examples
        }
    
    def test_authority_vs_family_interpretation(self):
        """Test if 'father/mother' are religious authorities OR just family references"""
        print(f"\n👨‍👩‍👧‍👦 AUTHORITY VS FAMILY ANALYSIS")
        print("=" * 31)
        
        # Look for context clues around father/mother
        authority_contexts = [
            'command', 'order', 'rule', 'control', 'authorize', 'permit', 'official',
            'power', 'leader', 'chief', 'head', 'supreme', 'high', 'great'
        ]
        
        family_contexts = [
            'child', 'son', 'daughter', 'home', 'family', 'love', 'care', 'help',
            'together', 'share', 'give', 'take', 'come', 'go', 'house', 'live'
        ]
        
        father_authority = 0
        father_family = 0
        mother_authority = 0
        mother_family = 0
        
        father_authority_examples = []
        father_family_examples = []
        mother_authority_examples = []
        mother_family_examples = []
        
        for _, row in self.translations.iterrows():
            translation = row['english_translation'].lower()
            original = row['original_indus']
            
            if 'father' in translation:
                # Check context
                has_authority_context = any(term in translation for term in authority_contexts)
                has_family_context = any(term in translation for term in family_contexts)
                
                if has_authority_context:
                    father_authority += 1
                    father_authority_examples.append({
                        'original': original,
                        'translation': translation,
                        'authority_clues': [term for term in authority_contexts if term in translation]
                    })
                
                if has_family_context:
                    father_family += 1
                    father_family_examples.append({
                        'original': original,
                        'translation': translation,
                        'family_clues': [term for term in family_contexts if term in translation]
                    })
            
            if 'mother' in translation:
                # Check context
                has_authority_context = any(term in translation for term in authority_contexts)
                has_family_context = any(term in translation for term in family_contexts)
                
                if has_authority_context:
                    mother_authority += 1
                    mother_authority_examples.append({
                        'original': original,
                        'translation': translation,
                        'authority_clues': [term for term in authority_contexts if term in translation]
                    })
                
                if has_family_context:
                    mother_family += 1
                    mother_family_examples.append({
                        'original': original,
                        'translation': translation,
                        'family_clues': [term for term in family_contexts if term in translation]
                    })
        
        print(f"📊 FATHER CONTEXT ANALYSIS:")
        print(f"   Authority context: {father_authority} instances")
        print(f"   Family context: {father_family} instances")
        print(f"   Ratio (Authority/Family): {father_authority/father_family if father_family > 0 else 'N/A'}")
        
        print(f"\n📊 MOTHER CONTEXT ANALYSIS:")
        print(f"   Authority context: {mother_authority} instances")
        print(f"   Family context: {mother_family} instances")
        print(f"   Ratio (Authority/Family): {mother_authority/mother_family if mother_family > 0 else 'N/A'}")
        
        print(f"\n👨‍💼 FATHER AS AUTHORITY EXAMPLES:")
        for i, example in enumerate(father_authority_examples[:3]):
            print(f"   {i+1}. {example['original']} → {example['translation']}")
            print(f"      Authority clues: {example['authority_clues']}")
        
        print(f"\n👨‍👧‍👦 FATHER AS FAMILY EXAMPLES:")
        for i, example in enumerate(father_family_examples[:3]):
            print(f"   {i+1}. {example['original']} → {example['translation']}")
            print(f"      Family clues: {example['family_clues']}")
        
        # Determine interpretation
        total_father = father_authority + father_family
        total_mother = mother_authority + mother_family
        
        if total_father > 0:
            father_authority_ratio = father_authority / total_father
        else:
            father_authority_ratio = 0
        
        if total_mother > 0:
            mother_authority_ratio = mother_authority / total_mother
        else:
            mother_authority_ratio = 0
        
        print(f"\n🎯 INTERPRETATION VERDICT:")
        if father_authority_ratio > 0.7:
            father_interpretation = "AUTHORITY/OFFICIAL"
        elif father_authority_ratio > 0.3:
            father_interpretation = "MIXED (BOTH AUTHORITY & FAMILY)"
        else:
            father_interpretation = "FAMILY/PERSONAL"
        
        if mother_authority_ratio > 0.7:
            mother_interpretation = "AUTHORITY/OFFICIAL"
        elif mother_authority_ratio > 0.3:
            mother_interpretation = "MIXED (BOTH AUTHORITY & FAMILY)"
        else:
            mother_interpretation = "FAMILY/PERSONAL"
        
        print(f"   Father interpretation: {father_interpretation}")
        print(f"   Mother interpretation: {mother_interpretation}")
        
        return {
            'father_authority_ratio': father_authority_ratio,
            'mother_authority_ratio': mother_authority_ratio,
            'father_interpretation': father_interpretation,
            'mother_interpretation': mother_interpretation
        }
    
    def analyze_liberal_pragmatic_indicators(self):
        """Look for evidence of liberal, pragmatic, egalitarian society"""
        print(f"\n🌟 LIBERAL/PRAGMATIC SOCIETY INDICATORS")
        print("=" * 35)
        
        # Look for egalitarian indicators
        egalitarian_terms = [
            'equal', 'same', 'share', 'together', 'all', 'everyone', 'common',
            'fair', 'balance', 'cooperate', 'help', 'mutual', 'collective'
        ]
        
        # Look for practical organization
        practical_organization = [
            'organize', 'plan', 'arrange', 'manage', 'coordinate', 'system',
            'method', 'process', 'efficient', 'practical', 'useful', 'work'
        ]
        
        # Look for liberal/open indicators
        liberal_terms = [
            'open', 'free', 'choice', 'decide', 'choose', 'option', 'flexible',
            'change', 'adapt', 'different', 'various', 'diverse', 'welcome'
        ]
        
        egalitarian_count = 0
        practical_count = 0
        liberal_count = 0
        
        egalitarian_examples = []
        practical_examples = []
        liberal_examples = []
        
        for _, row in self.translations.iterrows():
            translation = row['english_translation'].lower()
            original = row['original_indus']
            
            # Check for egalitarian content
            found_egalitarian = [term for term in egalitarian_terms if term in translation]
            if found_egalitarian:
                egalitarian_count += len(found_egalitarian)
                egalitarian_examples.append({
                    'original': original,
                    'translation': translation,
                    'egalitarian_terms': found_egalitarian
                })
            
            # Check for practical organization
            found_practical = [term for term in practical_organization if term in translation]
            if found_practical:
                practical_count += len(found_practical)
                practical_examples.append({
                    'original': original,
                    'translation': translation,
                    'practical_terms': found_practical
                })
            
            # Check for liberal indicators
            found_liberal = [term for term in liberal_terms if term in translation]
            if found_liberal:
                liberal_count += len(found_liberal)
                liberal_examples.append({
                    'original': original,
                    'translation': translation,
                    'liberal_terms': found_liberal
                })
        
        print(f"📊 LIBERAL/PRAGMATIC INDICATORS:")
        print(f"   🤝 Egalitarian terms: {egalitarian_count} occurrences")
        print(f"   🔧 Practical organization: {practical_count} occurrences")
        print(f"   🆓 Liberal/Open terms: {liberal_count} occurrences")
        
        print(f"\n🤝 EGALITARIAN EXAMPLES:")
        for i, example in enumerate(egalitarian_examples[:3]):
            print(f"   {i+1}. {example['original']} → {example['translation']}")
            print(f"      Egalitarian terms: {example['egalitarian_terms']}")
        
        print(f"\n🔧 PRACTICAL ORGANIZATION EXAMPLES:")
        for i, example in enumerate(practical_examples[:3]):
            print(f"   {i+1}. {example['original']} → {example['translation']}")
            print(f"      Practical terms: {example['practical_terms']}")
        
        return {
            'egalitarian_count': egalitarian_count,
            'practical_count': practical_count,
            'liberal_count': liberal_count
        }
    
    def critical_translation_verification(self):
        """Critically examine if our translations are forcing religious interpretations"""
        print(f"\n🔍 CRITICAL TRANSLATION VERIFICATION")
        print("=" * 33)
        
        # Check if we're forcing "blessing", "sacred", "divine" where simpler interpretations exist
        suspected_forced_religious = []
        
        # Look for translations that might be forcing religious language
        for _, row in self.translations.iterrows():
            translation = row['english_translation'].lower()
            original = row['original_indus']
            
            # Check for potentially forced religious interpretations
            religious_words = ['blessing', 'sacred', 'divine', 'holy']
            secular_alternatives = {
                'blessing': ['approval', 'permission', 'agreement', 'validation'],
                'sacred': ['important', 'special', 'designated', 'official'],
                'divine': ['official', 'authorized', 'formal', 'important'],
                'holy': ['special', 'important', 'designated', 'official']
            }
            
            found_religious = [word for word in religious_words if word in translation]
            if found_religious:
                suspected_forced_religious.append({
                    'original': original,
                    'translation': translation,
                    'religious_words': found_religious,
                    'possible_secular_alternatives': [secular_alternatives.get(word, []) for word in found_religious]
                })
        
        print(f"⚠️ POTENTIALLY FORCED RELIGIOUS INTERPRETATIONS:")
        print(f"   Found {len(suspected_forced_religious)} cases")
        
        for i, case in enumerate(suspected_forced_religious[:5]):
            print(f"\n   {i+1}. {case['original']} → {case['translation']}")
            print(f"      Religious words used: {case['religious_words']}")
            for j, word in enumerate(case['religious_words']):
                alternatives = secular_alternatives.get(word, [])
                print(f"      '{word}' could be: {', '.join(alternatives)}")
        
        return suspected_forced_religious
    
    def generate_truth_assessment(self, content_analysis, authority_analysis, liberal_analysis, forced_religious):
        """Generate honest assessment of what the evidence actually shows"""
        print(f"\n🎯 TRUTH ASSESSMENT")
        print("=" * 17)
        
        # Calculate evidence weights
        total_translations = len(self.translations)
        
        religious_percentage = (content_analysis['religious_count'] / total_translations) * 100 if total_translations > 0 else 0
        practical_percentage = (content_analysis['practical_count'] / total_translations) * 100 if total_translations > 0 else 0
        family_percentage = (content_analysis['family_social_count'] / total_translations) * 100 if total_translations > 0 else 0
        
        print(f"📊 EVIDENCE BREAKDOWN:")
        print(f"   🏛️ Actual religious content: {religious_percentage:.1f}%")
        print(f"   💼 Practical/commercial content: {practical_percentage:.1f}%")
        print(f"   👨‍👩‍👧‍👦 Family/social content: {family_percentage:.1f}%")
        print(f"   ⚠️ Potentially forced religious interpretations: {len(forced_religious)}")
        
        print(f"\n🔍 AUTHORITY VS FAMILY ANALYSIS:")
        print(f"   Father as authority: {authority_analysis['father_interpretation']}")
        print(f"   Mother as authority: {authority_analysis['mother_interpretation']}")
        
        # Generate honest verdict
        print(f"\n⚖️ HONEST VERDICT:")
        
        if religious_percentage < 5 and len(forced_religious) > 10:
            verdict = "LIKELY SECULAR/PRAGMATIC"
            confidence = "HIGH"
            explanation = "Very little actual religious content found. Many religious interpretations appear forced."
        elif religious_percentage < 20 and family_percentage > 50:
            verdict = "PRIMARILY FAMILY/SOCIAL ORGANIZATION"
            confidence = "MODERATE"
            explanation = "Mostly family and social references, minimal religious content."
        elif religious_percentage > 30:
            verdict = "GENUINELY RELIGIOUS"
            confidence = "MODERATE"
            explanation = "Significant religious content found throughout."
        else:
            verdict = "MIXED/UNCLEAR"
            confidence = "LOW"
            explanation = "Evidence is mixed or unclear. Further analysis needed."
        
        print(f"   🎯 Most likely reality: {verdict}")
        print(f"   🎲 Confidence level: {confidence}")
        print(f"   💡 Explanation: {explanation}")
        
        # Specific challenges to my earlier interpretation
        print(f"\n🚨 CHALLENGES TO PREVIOUS 'SACRED-ECONOMY' INTERPRETATION:")
        
        if religious_percentage < 10:
            print(f"   ❌ Only {religious_percentage:.1f}% actual religious content - insufficient for 'sacred economy'")
        
        if len(forced_religious) > 20:
            print(f"   ❌ {len(forced_religious)} potentially forced religious interpretations - bias evident")
        
        if family_percentage > religious_percentage * 3:
            print(f"   ❌ Family content ({family_percentage:.1f}%) far exceeds religious ({religious_percentage:.1f}%) - suggests family organization")
        
        if authority_analysis['father_interpretation'] == "FAMILY/PERSONAL":
            print(f"   ❌ 'Father' appears to be family reference, not religious authority")
        
        if practical_percentage > religious_percentage:
            print(f"   ❌ Practical content ({practical_percentage:.1f}%) exceeds religious ({religious_percentage:.1f}%) - suggests pragmatic society")
        
        return {
            'verdict': verdict,
            'confidence': confidence,
            'religious_percentage': religious_percentage,
            'practical_percentage': practical_percentage,
            'family_percentage': family_percentage,
            'forced_religious_count': len(forced_religious)
        }

def main():
    print("🔍 INDUS VALLEY TRUTH DETECTOR")
    print("=" * 30)
    print("Objective: Find the ACTUAL truth without imposing frameworks")
    print("Question: Religious society OR Liberal/Pragmatic society?")
    
    detector = IndusRealityDetector()
    
    # Load all evidence
    if not detector.load_all_data():
        return 1
    
    # Analyze without bias
    content_analysis = detector.analyze_actual_content_without_bias()
    
    # Test authority vs family interpretation
    authority_analysis = detector.test_authority_vs_family_interpretation()
    
    # Look for liberal/pragmatic indicators
    liberal_analysis = detector.analyze_liberal_pragmatic_indicators()
    
    # Check for forced religious interpretations
    forced_religious = detector.critical_translation_verification()
    
    # Generate honest assessment
    truth_assessment = detector.generate_truth_assessment(content_analysis, authority_analysis, liberal_analysis, forced_religious)
    
    print(f"\n🎉 TRUTH DETECTION COMPLETE!")
    print(f"📊 Reality check: {truth_assessment['verdict']}")
    
    return 0

if __name__ == "__main__":
    exit(main()) 