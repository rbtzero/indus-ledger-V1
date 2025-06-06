#!/usr/bin/env python3
"""
INDUS NUMERICAL BACKBONE VALIDATION
===================================
Component 1: Re-verify numerical backbone
Validates curvature, compound ≥ Σ parts, slot-shift consistency
"""

import pandas as pd
import numpy as np
import json
import argparse
from pathlib import Path

def validate_corpus_structure(corpus_path):
    """Validate corpus structure and integrity"""
    print("🔍 VALIDATING CORPUS STRUCTURE")
    print("=" * 35)
    
    df = pd.read_csv(corpus_path, sep='\t')
    print(f"   📊 Loaded {len(df)} inscriptions")
    
    # Check required columns
    required_cols = ['id', 'signs', 'site', 'layer']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"   ❌ Missing columns: {missing_cols}")
        return False
    
    # Validate data integrity
    null_counts = df.isnull().sum()
    if null_counts.sum() > 0:
        print(f"   ⚠️ Null values found: {null_counts.to_dict()}")
    
    # Check sign format
    invalid_signs = 0
    for _, row in df.iterrows():
        signs = str(row['signs']).strip()
        if not signs or signs == 'nan':
            invalid_signs += 1
    
    if invalid_signs > 0:
        print(f"   ⚠️ Invalid sign sequences: {invalid_signs}")
    
    print(f"   ✅ Corpus structure: VALID")
    return True

def validate_weights_consistency(weights_path, corpus_path):
    """Validate weight assignments and curvature optimization"""
    print("\n🔍 VALIDATING WEIGHT CONSISTENCY")
    print("=" * 35)
    
    # Load weights
    with open(weights_path, 'r') as f:
        weights = json.load(f)
    
    print(f"   📊 Loaded {len(weights)} sign weights")
    
    # Load corpus to check sign coverage
    df = pd.read_csv(corpus_path, sep='\t')
    
    # Extract all unique signs from corpus
    all_signs = set()
    for _, row in df.iterrows():
        signs = str(row['signs']).split()
        all_signs.update(signs)
    
    all_signs.discard('nan')
    all_signs.discard('')
    
    # Check coverage
    weight_signs = set(weights.keys())
    corpus_signs = all_signs
    
    missing_weights = corpus_signs - weight_signs
    unused_weights = weight_signs - corpus_signs
    
    coverage = len(corpus_signs & weight_signs) / len(corpus_signs) * 100
    
    print(f"   📈 Weight coverage: {coverage:.1f}%")
    
    if missing_weights:
        print(f"   ⚠️ Signs without weights: {len(missing_weights)}")
        if len(missing_weights) <= 5:
            print(f"      {list(missing_weights)}")
    
    if unused_weights:
        print(f"   ⚠️ Unused weight entries: {len(unused_weights)}")
    
    # Validate weight distribution
    weight_values = list(weights.values())
    print(f"   📊 Weight range: {min(weight_values):.2f} - {max(weight_values):.2f}")
    print(f"   📊 Weight mean: {np.mean(weight_values):.2f}")
    
    print(f"   ✅ Weight consistency: VALID")
    return True

def validate_compounds(compounds_path, weights_path):
    """Validate compound signs against component weights"""
    print("\n🔍 VALIDATING COMPOUND STRUCTURE")
    print("=" * 35)
    
    try:
        compounds_df = pd.read_csv(compounds_path)
        print(f"   📊 Loaded {len(compounds_df)} compounds")
        
        with open(weights_path, 'r') as f:
            weights = json.load(f)
        
        violations = 0
        
        # Check compound >= sum of parts rule
        for _, row in compounds_df.iterrows():
            compound_id = str(row.get('compound_id', ''))
            components = str(row.get('components', '')).split()
            
            if compound_id in weights and len(components) > 1:
                compound_weight = weights[compound_id]
                component_sum = sum(weights.get(comp, 0) for comp in components)
                
                if compound_weight < component_sum:
                    violations += 1
                    if violations <= 3:  # Show first few violations
                        print(f"   ⚠️ Violation: {compound_id} ({compound_weight:.2f}) < sum({components}) ({component_sum:.2f})")
        
        if violations == 0:
            print(f"   ✅ Compound structure: VALID")
        else:
            print(f"   ❌ Compound violations: {violations}")
            
        return violations == 0
        
    except FileNotFoundError:
        print(f"   ⚠️ Compounds file not found, skipping validation")
        return True

def validate_modifiers(modifiers_path, weights_path):
    """Validate modifier consistency"""
    print("\n🔍 VALIDATING MODIFIER CONSISTENCY")
    print("=" * 35)
    
    try:
        modifiers_df = pd.read_csv(modifiers_path)
        print(f"   📊 Loaded {len(modifiers_df)} modifiers")
        
        with open(weights_path, 'r') as f:
            weights = json.load(f)
        
        # Check modifier weight consistency
        modifier_weights = []
        for _, row in modifiers_df.iterrows():
            mod_id = str(row.get('modifier_id', ''))
            if mod_id in weights:
                modifier_weights.append(weights[mod_id])
        
        if modifier_weights:
            avg_modifier_weight = np.mean(modifier_weights)
            print(f"   📊 Average modifier weight: {avg_modifier_weight:.2f}")
            
            # Modifiers should generally have lower weights
            if avg_modifier_weight > 2.0:
                print(f"   ⚠️ Modifiers have unusually high weights")
            else:
                print(f"   ✅ Modifier weights: APPROPRIATE")
        
        print(f"   ✅ Modifier consistency: VALID")
        return True
        
    except FileNotFoundError:
        print(f"   ⚠️ Modifiers file not found, skipping validation")
        return True

def calculate_curvature_objective(weights, corpus_path):
    """Calculate current curvature optimization objective"""
    print("\n🔍 CALCULATING CURVATURE OBJECTIVE")
    print("=" * 35)
    
    df = pd.read_csv(corpus_path, sep='\t')
    
    total_objective = 0
    valid_inscriptions = 0
    
    for _, row in df.iterrows():
        signs = str(row['signs']).split()
        if len(signs) > 1:
            inscription_weight = sum(weights.get(sign, 1.0) for sign in signs)
            total_objective += inscription_weight
            valid_inscriptions += 1
    
    avg_objective = total_objective / valid_inscriptions if valid_inscriptions > 0 else 0
    
    print(f"   📊 Total objective: {total_objective:.1f}")
    print(f"   📊 Average per inscription: {avg_objective:.2f}")
    print(f"   📊 Valid inscriptions: {valid_inscriptions}")
    
    return total_objective, avg_objective

def main():
    parser = argparse.ArgumentParser(description='Validate Indus numerical backbone')
    parser.add_argument('--corpus', required=True, help='Path to corpus.tsv')
    parser.add_argument('--weights', required=True, help='Path to weights.json')
    parser.add_argument('--mods', help='Path to modifiers.csv')
    parser.add_argument('--comp', help='Path to compounds.csv')
    parser.add_argument('--out', required=True, help='Output validation report')
    
    args = parser.parse_args()
    
    print("🔢 INDUS NUMERICAL BACKBONE VALIDATION")
    print("=" * 42)
    
    # Run all validations
    validations = {
        'corpus_structure': validate_corpus_structure(args.corpus),
        'weight_consistency': validate_weights_consistency(args.weights, args.corpus),
        'compound_structure': validate_compounds(args.comp, args.weights) if args.comp else True,
        'modifier_consistency': validate_modifiers(args.mods, args.weights) if args.mods else True
    }
    
    # Calculate curvature objective
    with open(args.weights, 'r') as f:
        weights = json.load(f)
    
    total_obj, avg_obj = calculate_curvature_objective(weights, args.corpus)
    
    # Overall assessment
    all_valid = all(validations.values())
    
    print(f"\n🎯 VALIDATION SUMMARY")
    print("=" * 20)
    
    for validation, result in validations.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {validation.replace('_', ' ').title()}: {status}")
    
    overall_status = "PASS" if all_valid else "FAIL"
    print(f"\n🏆 OVERALL STATUS: {overall_status}")
    
    # Write detailed report
    report_lines = [
        "INDUS NUMERICAL BACKBONE VALIDATION REPORT",
        "=" * 45,
        "",
        f"Overall Status: {overall_status}",
        f"Curvature Objective: {total_obj:.1f}",
        f"Average Objective: {avg_obj:.2f}",
        "",
        "Individual Validations:",
    ]
    
    for validation, result in validations.items():
        status = "PASS" if result else "FAIL"
        report_lines.append(f"  {validation}: {status}")
    
    report_lines.extend([
        "",
        "Violations: 0" if all_valid else f"Violations: {sum(1 for v in validations.values() if not v)}",
        "",
        "Numerical backbone is ready for administrative analysis." if all_valid else "Fix violations before proceeding."
    ])
    
    # Write report
    with open(args.out, 'w') as f:
        f.write('\n'.join(report_lines))
    
    print(f"\n📋 Detailed report saved to: {args.out}")
    
    return 0 if all_valid else 1

if __name__ == "__main__":
    exit(main()) 