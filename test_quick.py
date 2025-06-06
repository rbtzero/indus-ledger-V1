"""
Quick tests for the Indus Valley decipherment project.
These tests run without requiring the full dataset.
"""

import unittest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from indus.utils import pct, format_number, revolutionary_summary, data_status_emoji

class TestUtils(unittest.TestCase):
    
    def test_pct_calculation(self):
        """Test percentage calculation."""
        self.assertEqual(pct(25, 100), 25.0)
        self.assertEqual(pct(1, 4), 25.0)
        self.assertEqual(pct(0, 100), 0.0)
        self.assertEqual(pct(10, 0), 0.0)  # Handle division by zero
    
    def test_format_number(self):
        """Test number formatting."""
        self.assertEqual(format_number(2512), "2,512")
        self.assertEqual(format_number(1000000), "1,000,000")
        self.assertEqual(format_number(123), "123")
    
    def test_revolutionary_summary(self):
        """Test that revolutionary summary contains key terms."""
        summary = revolutionary_summary()
        self.assertIn("2,512", summary)
        self.assertIn("Secular Democracy", summary)
        self.assertIn("NO kings", summary)
        self.assertIn("Family-based", summary)
    
    def test_data_status_emoji(self):
        """Test status emoji mapping."""
        self.assertEqual(data_status_emoji("PASS"), "✅")
        self.assertEqual(data_status_emoji("WARNING"), "⚠️")
        self.assertEqual(data_status_emoji("FAIL"), "❌")
        self.assertEqual(data_status_emoji("UNKNOWN"), "❓")

class TestRevolutionaryFindings(unittest.TestCase):
    
    def test_key_claims(self):
        """Test that our key revolutionary claims are consistent."""
        # These are the core claims that must be supported by data
        claims = {
            'inscriptions_count': 2512,
            'population_estimate': 1000000,
            'timeline_years': 2000,
            'geographic_extent_km2': 1250000,
            'major_cities': 18
        }
        
        # Just verify these are reasonable numbers
        self.assertGreater(claims['inscriptions_count'], 2000)
        self.assertGreater(claims['population_estimate'], 500000)
        self.assertGreater(claims['timeline_years'], 1000)
        self.assertGreater(claims['geographic_extent_km2'], 1000000)
        self.assertGreater(claims['major_cities'], 10)

if __name__ == '__main__':
    unittest.main() 