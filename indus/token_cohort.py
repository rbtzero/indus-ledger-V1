#!/usr/bin/env python3
"""
token_cohort.py
Analyzes ownership terms and their associated commodities in the sacred-economy model
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import argparse
import csv

class TokenCohortAnalyzer:
    """Analyzes ownership terms and their commodity associations"""
    
    def __init__(self):
        self.ownership_terms = ['father', 'mother', 'king', 'priest', 'person', 'house', 'lord', 'chief']
        self.commodity_terms = ['water', 'grain', 'cattle', 'copper', 'land', 'cattle', 'fish', 'salt']
        
    def load_ledger(self, ledger_path):
        """Load the ledger data"""
        try:
            self.ledger = pd.read_csv(ledger_path, sep='\t')
            print(f"✓ Loaded {len(self.ledger)} ledger entries")
            return True
        except Exception as e:
            print(f"❌ Error loading ledger: {e}")
            return False
    
    def extract_ownership_commodity_pairs(self, slot_type='ownership'):
        """Extract ownership-commodity associations"""
        print(f"\n🔍 EXTRACTING {slot_type.upper()} ASSOCIATIONS")
        print("=" * 40)
        
        ownership_commodity_pairs = []
        ownership_counts = Counter()
        commodity_counts = Counter()
        
        # Load translations if available
        try:
            translations = pd.read_csv('output/corrected_translations.tsv', sep='\t')
            print(f"✓ Using {len(translations)} translations")
            
            for _, row in translations.iterrows():
                original = row['original_indus']
                translation = row['english_translation'].lower()
                
                # Find ownership terms
                found_owners = [term for term in self.ownership_terms if term in translation]
                found_commodities = [term for term in self.commodity_terms if term in translation]
                
                for owner in found_owners:
                    ownership_counts[owner] += 1
                    for commodity in found_commodities:
                        commodity_counts[commodity] += 1
                        ownership_commodity_pairs.append({
                            'original_sequence': original,
                            'owner_term': owner,
                            'commodity': commodity,
                            'translation': translation,
                            'strength': translation.count(owner) + translation.count(commodity)
                        })
        
        except Exception as e:
            print(f"⚠️ Using ledger fallback: {e}")
            # Fallback to ledger analysis
            for _, row in self.ledger.iterrows():
                if 'english' in row and pd.notna(row['english']):
                    text = str(row['english']).lower()
                    found_owners = [term for term in self.ownership_terms if term in text]
                    found_commodities = [term for term in self.commodity_terms if term in text]
                    
                    for owner in found_owners:
                        ownership_counts[owner] += 1
                        for commodity in found_commodities:
                            commodity_counts[commodity] += 1
                            ownership_commodity_pairs.append({
                                'original_sequence': row.get('indus', ''),
                                'owner_term': owner,
                                'commodity': commodity,
                                'translation': text,
                                'strength': 1
                            })
        
        print(f"📊 OWNERSHIP ANALYSIS RESULTS:")
        print(f"   • Total ownership-commodity pairs: {len(ownership_commodity_pairs)}")
        print(f"   • Unique owner terms: {len(ownership_counts)}")
        print(f"   • Unique commodities: {len(commodity_counts)}")
        
        return ownership_commodity_pairs, ownership_counts, commodity_counts
    
    def analyze_authority_patterns(self, pairs):
        """Analyze which authorities control which commodities"""
        print(f"\n👑 AUTHORITY-COMMODITY CONTROL PATTERNS")
        print("=" * 40)
        
        # Create authority-commodity matrix
        authority_matrix = defaultdict(lambda: defaultdict(int))
        
        for pair in pairs:
            authority_matrix[pair['owner_term']][pair['commodity']] += pair['strength']
        
        # Calculate specialization scores
        specialization_data = []
        
        for owner, commodities in authority_matrix.items():
            total_control = sum(commodities.values())
            max_commodity = max(commodities.keys(), key=lambda x: commodities[x]) if commodities else None
            max_control = commodities[max_commodity] if max_commodity else 0
            specialization = (max_control / total_control) if total_control > 0 else 0
            
            specialization_data.append({
                'owner_term': owner,
                'primary_commodity': max_commodity,
                'primary_control': max_control,
                'total_control': total_control,
                'specialization_ratio': specialization,
                'commodity_diversity': len(commodities)
            })
        
        # Sort by specialization
        specialization_data.sort(key=lambda x: x['specialization_ratio'], reverse=True)
        
        print(f"🎯 AUTHORITY SPECIALIZATION RANKINGS:")
        for i, auth in enumerate(specialization_data[:8]):
            print(f"   {i+1}. {auth['owner_term'].upper()}")
            print(f"      Primary commodity: {auth['primary_commodity']} ({auth['primary_control']} instances)")
            print(f"      Specialization: {auth['specialization_ratio']:.2%}")
            print(f"      Diversity: {auth['commodity_diversity']} commodities")
            print()
        
        return specialization_data, authority_matrix
    
    def generate_certification_model(self, authority_matrix):
        """Generate the sacred-economy certification model"""
        print(f"\n🏛️ SACRED-ECONOMY CERTIFICATION MODEL")
        print("=" * 38)
        
        certification_rules = []
        
        for owner, commodities in authority_matrix.items():
            if not commodities:
                continue
                
            # Calculate authority scope
            total_certifications = sum(commodities.values())
            primary_commodity = max(commodities.keys(), key=lambda x: commodities[x])
            primary_strength = commodities[primary_commodity]
            
            # Determine certification type
            if primary_strength / total_certifications >= 0.7:
                cert_type = "SPECIALIST"
            elif len(commodities) >= 4:
                cert_type = "GENERAL"
            else:
                cert_type = "LIMITED"
            
            certification_rules.append({
                'authority': owner,
                'certification_type': cert_type,
                'primary_commodity': primary_commodity,
                'commodity_count': len(commodities),
                'total_certifications': total_certifications,
                'authority_scope': list(commodities.keys())
            })
        
        # Sort by total certifications
        certification_rules.sort(key=lambda x: x['total_certifications'], reverse=True)
        
        print(f"📜 DIVINE CERTIFICATION HIERARCHY:")
        for i, rule in enumerate(certification_rules):
            print(f"   {i+1}. {rule['authority'].upper()} ({rule['certification_type']})")
            print(f"      Primary domain: {rule['primary_commodity']}")
            print(f"      Full authority: {', '.join(rule['authority_scope'])}")
            print(f"      Total certifications: {rule['total_certifications']}")
            print()
        
        return certification_rules
    
    def save_results(self, pairs, specialization_data, certification_rules, output_path):
        """Save the ownership analysis results"""
        print(f"\n💾 SAVING RESULTS TO {output_path}")
        
        # Prepare data for CSV output
        csv_data = []
        
        # Add ownership-commodity pairs
        for pair in pairs:
            csv_data.append({
                'type': 'ownership_commodity_pair',
                'owner_term': pair['owner_term'],
                'commodity': pair['commodity'],
                'original_sequence': pair['original_sequence'],
                'strength': pair['strength'],
                'translation': pair['translation']
            })
        
        # Add specialization data
        for spec in specialization_data:
            csv_data.append({
                'type': 'authority_specialization',
                'owner_term': spec['owner_term'],
                'commodity': spec['primary_commodity'],
                'original_sequence': '',
                'strength': spec['specialization_ratio'],
                'translation': f"Primary: {spec['primary_commodity']}, Diversity: {spec['commodity_diversity']}"
            })
        
        # Add certification rules
        for cert in certification_rules:
            csv_data.append({
                'type': 'certification_rule',
                'owner_term': cert['authority'],
                'commodity': cert['primary_commodity'],
                'original_sequence': '',
                'strength': cert['total_certifications'],
                'translation': f"{cert['certification_type']}: {', '.join(cert['authority_scope'])}"
            })
        
        # Save to CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['type', 'owner_term', 'commodity', 'original_sequence', 'strength', 'translation']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)
        
        print(f"✅ Saved {len(csv_data)} records to {output_path}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Analyze ownership terms and commodity associations')
    parser.add_argument('--ledger', required=True, help='Path to ledger file')
    parser.add_argument('--slot', default='ownership', help='Analysis slot type')
    parser.add_argument('--out_csv', required=True, help='Output CSV path')
    
    args = parser.parse_args()
    
    print("🔍 TOKEN COHORT ANALYSIS")
    print("=" * 25)
    print(f"Research Question: Which authorities certify which commodities?")
    
    analyzer = TokenCohortAnalyzer()
    
    # Load data
    if not analyzer.load_ledger(args.ledger):
        return 1
    
    # Run analysis
    pairs, ownership_counts, commodity_counts = analyzer.extract_ownership_commodity_pairs(args.slot)
    
    if not pairs:
        print("❌ No ownership-commodity pairs found!")
        return 1
    
    specialization_data, authority_matrix = analyzer.analyze_authority_patterns(pairs)
    certification_rules = analyzer.generate_certification_model(authority_matrix)
    
    # Save results
    analyzer.save_results(pairs, specialization_data, certification_rules, args.out_csv)
    
    print(f"\n🎉 ANALYSIS COMPLETE!")
    print(f"📊 Sacred-economy certification model generated")
    
    return 0

if __name__ == "__main__":
    exit(main()) 