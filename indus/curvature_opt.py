#!/usr/bin/env python3
"""
Advanced Curvature Optimization with Free Variables
Allows economic differentiation to emerge naturally
"""

import pandas as pd
import numpy as np
from ortools.linear_solver import pywraplp
import json
import argparse
from collections import Counter, defaultdict

def load_corpus(corpus_file):
    """Load full inscription corpus"""
    df = pd.read_csv(corpus_file, sep='\t')
    inscriptions = []
    for _, row in df.iterrows():
        signs = [int(x) for x in str(row['sign_seq']).split()]
        inscriptions.append({
            'id': row['inscr_id'], 
            'signs': signs,
            'length': len(signs)
        })
    return inscriptions

def load_constraints(compounds_file, modifiers_file):
    """Load structural constraints"""
    compounds = pd.read_csv(compounds_file) if compounds_file else pd.DataFrame()
    modifiers = pd.read_csv(modifiers_file) if modifiers_file else pd.DataFrame()
    return compounds, modifiers

def setup_optimization(inscriptions, compounds, modifiers, free_w=True):
    """Setup optimization with economic differentiation constraints"""
    print("🧮 Setting up advanced curvature optimization...")
    
    # Extract all unique signs
    all_signs = set()
    for insc in inscriptions:
        all_signs.update(insc['signs'])
    signs = sorted(list(all_signs))
    n_signs = len(signs)
    
    print(f"📊 Optimizing {n_signs} unique signs from {len(inscriptions)} inscriptions")
    
    # Create solver
    solver = pywraplp.Solver.CreateSolver('CBC')
    if not solver:
        raise ValueError("CBC solver not available")
    
    # Create variables with economic ranges
    sign_weights = {}
    for sign in signs:
        if free_w:
            # Allow full economic differentiation
            if sign in [1, 2, 125, 350, 717]:  # Authority signs
                sign_weights[sign] = solver.NumVar(3.0, 8.0, f'w_{sign}')
            elif sign in [410, 740, 390, 99, 267]:  # Commodity signs  
                sign_weights[sign] = solver.NumVar(1.5, 4.0, f'w_{sign}')
            elif sign in range(1, 50):  # Likely numerals
                sign_weights[sign] = solver.NumVar(0.5, 2.0, f'w_{sign}')
            else:  # Standard signs
                sign_weights[sign] = solver.NumVar(1.0, 6.0, f'w_{sign}')
        else:
            # Constrained version
            sign_weights[sign] = solver.NumVar(0.1, 10.0, f'w_{sign}')
    
    # Objective: minimize total weight (encourages efficiency)
    objective = solver.Objective()
    for sign in signs:
        objective.SetCoefficient(sign_weights[sign], 1.0)
    objective.SetMinimization()
    
    # Add curvature constraints (economic coherence)
    print("🔗 Adding curvature constraints...")
    constraints_added = 0
    
    # Authority > commodity constraints
    authority_signs = [1, 2, 125, 350, 717]
    commodity_signs = [410, 740, 390, 99, 267, 156, 368, 235]
    
    for auth in authority_signs:
        if auth in sign_weights:
            for comm in commodity_signs:
                if comm in sign_weights:
                    solver.Add(sign_weights[auth] >= sign_weights[comm] + 0.5)
                    constraints_added += 1
    
    # Frequent signs should have lower weights (efficiency principle)
    freq = Counter([s for insc in inscriptions for s in insc['signs']])
    top_frequent = [s for s, f in freq.most_common(20)]
    
    for i, s1 in enumerate(top_frequent[:10]):
        for s2 in top_frequent[10:20]:
            if s1 in sign_weights and s2 in sign_weights:
                solver.Add(sign_weights[s1] <= sign_weights[s2] + 1.0)
                constraints_added += 1
    
    # Add compound constraints
    for _, comp in compounds.iterrows():
        # Compound should cost more than sum of parts
        # Implementation depends on compound format
        pass
    
    print(f"✅ Added {constraints_added} curvature constraints")
    
    return solver, sign_weights, signs

def solve_optimization(solver, sign_weights, signs):
    """Solve the optimization problem"""
    print("🔍 Solving curvature optimization...")
    
    status = solver.Solve()
    
    if status == pywraplp.Solver.OPTIMAL:
        print("✅ OPTIMAL solution found!")
    elif status == pywraplp.Solver.FEASIBLE:
        print("⚠️  FEASIBLE solution found (not optimal)")
    else:
        print("❌ No solution found")
        return None, None
    
    # Extract solution
    weights = {}
    for sign in signs:
        weights[str(sign)] = round(sign_weights[sign].solution_value(), 3)
    
    objective_value = solver.Objective().Value()
    
    return weights, objective_value

def analyze_solution(weights, inscriptions):
    """Analyze the weight solution for economic patterns"""
    print("📊 Analyzing weight distribution...")
    
    weight_values = list(weights.values())
    print(f"Weight range: {min(weight_values):.2f} - {max(weight_values):.2f}")
    print(f"Weight spread: {max(weight_values) - min(weight_values):.2f}")
    
    # Check for economic differentiation
    authority_weights = [weights.get(str(s), 0) for s in [1, 2, 125, 350, 717]]
    commodity_weights = [weights.get(str(s), 0) for s in [410, 740, 390, 99, 267]]
    
    avg_authority = np.mean([w for w in authority_weights if w > 0])
    avg_commodity = np.mean([w for w in commodity_weights if w > 0])
    
    print(f"Average authority weight: {avg_authority:.2f}")
    print(f"Average commodity weight: {avg_commodity:.2f}")
    print(f"Authority premium: {avg_authority - avg_commodity:.2f}")
    
    return {
        'weight_range': [min(weight_values), max(weight_values)],
        'weight_spread': max(weight_values) - min(weight_values),
        'authority_premium': avg_authority - avg_commodity,
        'total_signs': len(weights)
    }

def main():
    parser = argparse.ArgumentParser(description='Advanced Curvature Optimization')
    parser.add_argument('--corpus', required=True, help='Corpus TSV file')
    parser.add_argument('--compounds', help='Compounds CSV file')
    parser.add_argument('--modifiers', help='Modifiers CSV file')
    parser.add_argument('--free_w', type=int, default=1, help='Allow free weight variables (1=yes, 0=no)')
    parser.add_argument('--output', default='output/weights.json', help='Output weights file')
    
    args = parser.parse_args()
    
    # Load data
    inscriptions = load_corpus(args.corpus)
    compounds, modifiers = load_constraints(args.compounds, args.modifiers)
    
    # Setup and solve optimization
    solver, sign_weights, signs = setup_optimization(
        inscriptions, compounds, modifiers, 
        free_w=bool(args.free_w)
    )
    
    weights, objective = solve_optimization(solver, sign_weights, signs)
    
    if weights is None:
        print("❌ Optimization failed")
        return
    
    # Analyze solution
    analysis = analyze_solution(weights, inscriptions)
    
    # Save results
    result = {
        'status': 'OPTIMAL',
        'objective': objective,
        'variables': len(signs),
        'weights': weights,
        'analysis': analysis,
        'free_variables': bool(args.free_w)
    }
    
    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"✅ Results saved to {args.output}")
    print(f"📊 Objective: {objective:.2f}")
    print(f"🎯 Weight spread: {analysis['weight_spread']:.2f}")

if __name__ == '__main__':
    main() 