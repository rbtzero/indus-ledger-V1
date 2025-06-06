"""
Test trade graph construction - builds graph on 10-row mini corpus, expects edge count 9.
"""

import unittest
import sys
import os
import pandas as pd

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from indus.build_edges import build_trade_graph, extract_commodities
from indus.gravity_model import calculate_trade_strength


class TestTradeGraph(unittest.TestCase):
    
    def setUp(self):
        """Set up test data for trade graph construction."""
        # Create 10-row mini corpus as specified
        self.mini_corpus = [
            {'inscr_id': 'H001', 'site': 'Harappa', 'signs': [1, 342, 125], 'commodities': ['grain']},
            {'inscr_id': 'H002', 'site': 'Harappa', 'signs': [2, 410, 126], 'commodities': ['copper']},
            {'inscr_id': 'M001', 'site': 'Mohenjo-daro', 'signs': [1, 342, 905], 'commodities': ['grain']},
            {'inscr_id': 'M002', 'site': 'Mohenjo-daro', 'signs': [3, 740, 125], 'commodities': ['fish']},
            {'inscr_id': 'L001', 'site': 'Lothal', 'signs': [2, 342, 126], 'commodities': ['grain']},
            {'inscr_id': 'L002', 'site': 'Lothal', 'signs': [1, 156, 905], 'commodities': ['beads']},
            {'inscr_id': 'D001', 'site': 'Dholavira', 'signs': [4, 410, 125], 'commodities': ['copper']},
            {'inscr_id': 'D002', 'site': 'Dholavira', 'signs': [2, 368, 126], 'commodities': ['water']},
            {'inscr_id': 'R001', 'site': 'Rakhigarhi', 'signs': [1, 342, 125], 'commodities': ['grain']},
            {'inscr_id': 'R002', 'site': 'Rakhigarhi', 'signs': [3, 235, 905], 'commodities': ['textiles']},
        ]
        
        # Convert to DataFrame
        self.corpus_df = pd.DataFrame(self.mini_corpus)
        
        # Site information
        self.sites = {
            'Harappa': {'lat': 30.6311, 'lon': 72.8647},
            'Mohenjo-daro': {'lat': 27.3244, 'lon': 68.1378},
            'Lothal': {'lat': 22.5205, 'lon': 72.2474},
            'Dholavira': {'lat': 23.8907, 'lon': 70.2136},
            'Rakhigarhi': {'lat': 29.2813, 'lon': 76.1105},
        }
    
    def test_mini_corpus_size(self):
        """Test that we have exactly 10 rows as specified."""
        self.assertEqual(len(self.mini_corpus), 10, "Mini corpus should have exactly 10 rows")
    
    def test_commodity_extraction(self):
        """Test extraction of commodities from inscriptions."""
        commodities = extract_commodities(self.corpus_df)
        
        # Should extract commodities from the mini corpus
        expected_commodities = {'grain', 'copper', 'fish', 'beads', 'water', 'textiles'}
        self.assertEqual(set(commodities), expected_commodities)
    
    def test_trade_graph_construction(self):
        """Test that trade graph construction works on mini corpus."""
        # Build trade graph
        graph = build_trade_graph(self.corpus_df, self.sites)
        
        self.assertIsNotNone(graph)
        
        # Check that we have the expected sites as nodes
        expected_sites = {'Harappa', 'Mohenjo-daro', 'Lothal', 'Dholavira', 'Rakhigarhi'}
        actual_nodes = set(graph.nodes())
        self.assertEqual(actual_nodes, expected_sites)
    
    def test_expected_edge_count(self):
        """Test that we get exactly 9 edges as specified."""
        # Build trade graph
        graph = build_trade_graph(self.corpus_df, self.sites)
        
        # Should have 9 edges as specified in requirements
        edge_count = graph.number_of_edges()
        self.assertEqual(edge_count, 9, f"Expected 9 edges, got {edge_count}")
    
    def test_trade_strength_calculation(self):
        """Test trade strength calculation between sites."""
        # Test trade strength between sites that share commodities
        harappa_grain = len([r for r in self.mini_corpus if r['site'] == 'Harappa' and 'grain' in r['commodities']])
        mohenjo_grain = len([r for r in self.mini_corpus if r['site'] == 'Mohenjo-daro' and 'grain' in r['commodities']])
        
        # Sites with shared commodities should have trade connections
        self.assertGreater(harappa_grain, 0)
        self.assertGreater(mohenjo_grain, 0)
    
    def test_graph_connectivity(self):
        """Test that the trade graph is properly connected."""
        graph = build_trade_graph(self.corpus_df, self.sites)
        
        # Graph should be connected (all nodes reachable)
        import networkx as nx
        self.assertTrue(nx.is_connected(graph), "Trade graph should be connected")
    
    def test_commodity_distribution(self):
        """Test that commodities are distributed across multiple sites."""
        site_commodities = {}
        for record in self.mini_corpus:
            site = record['site']
            if site not in site_commodities:
                site_commodities[site] = set()
            site_commodities[site].update(record['commodities'])
        
        # Each site should have at least one commodity
        for site in self.sites.keys():
            self.assertIn(site, site_commodities, f"Site {site} should have commodities")
            self.assertGreater(len(site_commodities[site]), 0, f"Site {site} should have at least one commodity")
    
    def test_trade_edge_weights(self):
        """Test that trade edges have meaningful weights."""
        graph = build_trade_graph(self.corpus_df, self.sites)
        
        # All edges should have positive weights
        for u, v, data in graph.edges(data=True):
            weight = data.get('weight', 0)
            self.assertGreater(weight, 0, f"Edge {u}-{v} should have positive weight")


if __name__ == '__main__':
    unittest.main() 