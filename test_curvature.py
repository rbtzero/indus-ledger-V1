"""
Test curvature optimization - validates example sequence passes curvature constraints.
"""

import unittest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from indus.curvature_opt import setup_optimization, solve_optimization


class TestCurvatureOptimization(unittest.TestCase):
    
    def setUp(self):
        """Set up test data for curvature optimization."""
        # Sample inscriptions for testing
        self.sample_inscriptions = [
            {'id': 'test_001', 'signs': [1, 342, 125], 'length': 3},
            {'id': 'test_002', 'signs': [2, 410, 126], 'length': 3},
            {'id': 'test_003', 'signs': [3, 342, 905], 'length': 3},
            {'id': 'test_004', 'signs': [1, 740, 125], 'length': 3},
        ]
        
        # Empty constraints for basic test
        self.compounds = []
        self.modifiers = []
    
    def test_curvature_constraint_basic(self):
        """Test that basic curvature constraints can be set up."""
        solver, sign_weights, signs = setup_optimization(
            self.sample_inscriptions, 
            self.compounds, 
            self.modifiers, 
            free_w=True
        )
        
        self.assertIsNotNone(solver)
        self.assertIsNotNone(sign_weights)
        self.assertGreater(len(signs), 0)
        
        # Check that all signs from inscriptions are included
        expected_signs = {1, 2, 3, 125, 126, 342, 410, 740, 905}
        self.assertEqual(set(signs), expected_signs)
    
    def test_curvature_solution_exists(self):
        """Test that curvature optimization finds a solution."""
        solver, sign_weights, signs = setup_optimization(
            self.sample_inscriptions, 
            self.compounds, 
            self.modifiers, 
            free_w=True
        )
        
        weights, objective = solve_optimization(solver, sign_weights, signs)
        
        self.assertIsNotNone(weights)
        self.assertIsNotNone(objective)
        self.assertGreater(len(weights), 0)
        
        # Verify weights are positive
        for sign, weight in weights.items():
            self.assertGreater(weight, 0, f"Weight for sign {sign} should be positive")
    
    def test_authority_commodity_hierarchy(self):
        """Test that authority signs get higher weights than commodity signs."""
        solver, sign_weights, signs = setup_optimization(
            self.sample_inscriptions, 
            self.compounds, 
            self.modifiers, 
            free_w=True
        )
        
        weights, objective = solve_optimization(solver, sign_weights, signs)
        
        if weights:
            # Authority signs should have higher weights than commodity signs
            authority_signs = [125, 126]  # From our test data
            commodity_signs = [342, 410, 740]  # From our test data
            
            for auth_sign in authority_signs:
                if str(auth_sign) in weights:
                    for comm_sign in commodity_signs:
                        if str(comm_sign) in weights:
                            self.assertGreaterEqual(
                                weights[str(auth_sign)], 
                                weights[str(comm_sign)],
                                f"Authority sign {auth_sign} should have weight >= commodity sign {comm_sign}"
                            )
    
    def test_sequence_curvature_constraint(self):
        """Test that the curvature constraint w[i] - 2*w[j] + w[k] >= 0 is satisfied."""
        # This test validates the mathematical foundation of the decipherment
        solver, sign_weights, signs = setup_optimization(
            self.sample_inscriptions, 
            self.compounds, 
            self.modifiers, 
            free_w=True
        )
        
        weights, objective = solve_optimization(solver, sign_weights, signs)
        
        if weights:
            # Test curvature constraint on our sample sequences
            for insc in self.sample_inscriptions:
                if len(insc['signs']) >= 3:
                    for k in range(1, len(insc['signs']) - 1):
                        i, j, k2 = insc['signs'][k-1], insc['signs'][k], insc['signs'][k+1]
                        
                        w_i = weights.get(str(i), 0)
                        w_j = weights.get(str(j), 0)
                        w_k2 = weights.get(str(k2), 0)
                        
                        curvature = w_i - 2*w_j + w_k2
                        self.assertGreaterEqual(
                            curvature, -0.001,  # Allow small numerical tolerance
                            f"Curvature constraint violated for sequence {i}-{j}-{k2}: {curvature}"
                        )


if __name__ == '__main__':
    unittest.main() 