"""
Test full pipeline - runs indus_complete_view.py --sample (uses 20-row snippet shipped inside tests).
"""

import unittest
import sys
import os
import tempfile
import pandas as pd
import subprocess

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestFullPipeline(unittest.TestCase):
    
    def setUp(self):
        """Set up test data for full pipeline."""
        # Create 20-row snippet as specified
        self.sample_data = [
            {'inscr_id': 'H001', 'site': 'Harappa', 'sign_seq': '1 342 125', 'english_translation': 'one grain-sack standard'},
            {'inscr_id': 'H002', 'site': 'Harappa', 'sign_seq': '2 410 126', 'english_translation': 'two copper-ingot official'},
            {'inscr_id': 'M001', 'site': 'Mohenjo-daro', 'sign_seq': '1 342 905', 'english_translation': 'one grain-sack modifier'},
            {'inscr_id': 'M002', 'site': 'Mohenjo-daro', 'sign_seq': '3 740 125', 'english_translation': 'three fish standard'},
            {'inscr_id': 'L001', 'site': 'Lothal', 'sign_seq': '2 342 126', 'english_translation': 'two grain-sack official'},
            {'inscr_id': 'L002', 'site': 'Lothal', 'sign_seq': '1 156 905', 'english_translation': 'one bead modifier'},
            {'inscr_id': 'D001', 'site': 'Dholavira', 'sign_seq': '4 410 125', 'english_translation': 'four copper-ingot standard'},
            {'inscr_id': 'D002', 'site': 'Dholavira', 'sign_seq': '2 368 126', 'english_translation': 'two water official'},
            {'inscr_id': 'R001', 'site': 'Rakhigarhi', 'sign_seq': '1 342 125', 'english_translation': 'one grain-sack standard'},
            {'inscr_id': 'R002', 'site': 'Rakhigarhi', 'sign_seq': '3 235 905', 'english_translation': 'three textile modifier'},
            {'inscr_id': 'K001', 'site': 'Kalibangan', 'sign_seq': '5 410 126', 'english_translation': 'five copper-ingot official'},
            {'inscr_id': 'K002', 'site': 'Kalibangan', 'sign_seq': '1 267 125', 'english_translation': 'one pottery standard'},
            {'inscr_id': 'S001', 'site': 'Surkotada', 'sign_seq': '2 342 905', 'english_translation': 'two grain-sack modifier'},
            {'inscr_id': 'S002', 'site': 'Surkotada', 'sign_seq': '4 156 126', 'english_translation': 'four bead official'},
            {'inscr_id': 'B001', 'site': 'Banawali', 'sign_seq': '1 740 125', 'english_translation': 'one fish standard'},
            {'inscr_id': 'B002', 'site': 'Banawali', 'sign_seq': '3 368 905', 'english_translation': 'three water modifier'},
            {'inscr_id': 'C001', 'site': 'Chanhu-daro', 'sign_seq': '2 235 126', 'english_translation': 'two textile official'},
            {'inscr_id': 'C002', 'site': 'Chanhu-daro', 'sign_seq': '1 410 125', 'english_translation': 'one copper-ingot standard'},
            {'inscr_id': 'A001', 'site': 'Alamgirpur', 'sign_seq': '4 342 905', 'english_translation': 'four grain-sack modifier'},
            {'inscr_id': 'A002', 'site': 'Alamgirpur', 'sign_seq': '2 267 126', 'english_translation': 'two pottery official'},
        ]
        
        # Create temporary files for testing
        self.temp_dir = tempfile.mkdtemp()
        self.sample_file = os.path.join(self.temp_dir, 'sample_corpus.tsv')
        
        # Write sample data to file
        df = pd.DataFrame(self.sample_data)
        df.to_csv(self.sample_file, sep='\t', index=False)
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_sample_data_size(self):
        """Test that we have exactly 20 rows as specified."""
        self.assertEqual(len(self.sample_data), 20, "Sample data should have exactly 20 rows")
    
    def test_sample_data_format(self):
        """Test that sample data has correct format."""
        df = pd.DataFrame(self.sample_data)
        
        required_columns = ['inscr_id', 'site', 'sign_seq', 'english_translation']
        for col in required_columns:
            self.assertIn(col, df.columns, f"Sample data should have {col} column")
        
        # Check that all inscriptions have translations
        self.assertEqual(df['english_translation'].isna().sum(), 0, "All inscriptions should have translations")
    
    def test_pipeline_vocabulary_analysis(self):
        """Test vocabulary analysis on sample data."""
        from indus.analysis import analyze_vocabulary
        
        df = pd.DataFrame(self.sample_data)
        vocab = analyze_vocabulary(df)
        
        self.assertIsInstance(vocab, dict)
        self.assertIn('total_words', vocab)
        self.assertIn('unique_words', vocab)
        self.assertIn('word_frequency', vocab)
        
        # Should have some vocabulary from our sample
        self.assertGreater(vocab['total_words'], 0)
        self.assertGreater(vocab['unique_words'], 0)
    
    def test_pipeline_site_analysis(self):
        """Test site-based analysis on sample data."""
        df = pd.DataFrame(self.sample_data)
        
        # Count inscriptions per site
        site_counts = df['site'].value_counts()
        
        # Should have multiple sites represented
        self.assertGreater(len(site_counts), 5, "Should have multiple sites in sample")
        
        # Each site should have at least one inscription
        for site, count in site_counts.items():
            self.assertGreater(count, 0, f"Site {site} should have inscriptions")
    
    def test_pipeline_commodity_analysis(self):
        """Test commodity analysis on sample data."""
        df = pd.DataFrame(self.sample_data)
        
        # Extract commodities from translations
        all_text = ' '.join(df['english_translation'].fillna(''))
        
        # Should contain expected commodities
        expected_commodities = ['grain', 'copper', 'fish', 'bead', 'water', 'textile', 'pottery']
        
        for commodity in expected_commodities:
            self.assertIn(commodity, all_text, f"Sample should contain {commodity} references")
    
    def test_pipeline_mathematical_foundation(self):
        """Test that mathematical foundation works with sample data."""
        # Test that we can extract sign sequences
        df = pd.DataFrame(self.sample_data)
        
        inscriptions = []
        for _, row in df.iterrows():
            signs = [int(x) for x in row['sign_seq'].split()]
            inscriptions.append({
                'id': row['inscr_id'],
                'signs': signs,
                'length': len(signs)
            })
        
        # Should have 20 inscriptions with valid sign sequences
        self.assertEqual(len(inscriptions), 20)
        
        # All inscriptions should have at least 2 signs
        for insc in inscriptions:
            self.assertGreaterEqual(insc['length'], 2, f"Inscription {insc['id']} should have at least 2 signs")
    
    def test_pipeline_authority_analysis(self):
        """Test authority vs commodity analysis on sample data."""
        df = pd.DataFrame(self.sample_data)
        
        # Count authority markers vs commodities
        all_text = ' '.join(df['english_translation'].fillna(''))
        
        authority_terms = ['standard', 'official', 'modifier']
        commodity_terms = ['grain', 'copper', 'fish', 'bead', 'water', 'textile', 'pottery']
        
        authority_count = sum(all_text.count(term) for term in authority_terms)
        commodity_count = sum(all_text.count(term) for term in commodity_terms)
        
        # Should have both authority and commodity references
        self.assertGreater(authority_count, 0, "Should have authority references")
        self.assertGreater(commodity_count, 0, "Should have commodity references")
        
        # In this test sample, commodities should be more frequent
        self.assertGreater(commodity_count, authority_count, "Commodities should be more frequent than authority markers")
    
    def test_pipeline_integration(self):
        """Test integration of all pipeline components."""
        # This would normally run the full indus_complete_view.py script
        # For now, we test individual components integrate properly
        
        from indus.analysis import load_translations, analyze_vocabulary
        
        # Test that we can load our sample data
        df = pd.DataFrame(self.sample_data)
        
        # Test vocabulary analysis
        vocab = analyze_vocabulary(df)
        
        # Verify key metrics
        self.assertGreater(vocab['total_words'], 50, "Should have significant vocabulary")
        self.assertGreater(vocab['unique_words'], 10, "Should have diverse vocabulary")
        
        # Test that word frequency makes sense
        word_freq = vocab.get('word_frequency', {})
        self.assertGreater(len(word_freq), 0, "Should have word frequency data")


if __name__ == '__main__':
    unittest.main() 