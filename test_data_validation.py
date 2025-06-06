"""
Data validation tests for the Indus Valley decipherment project.
These tests require the actual data files to be present.
"""

import unittest
import sys
import os
import pandas as pd

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestDataIntegrity(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.translations_path = "output/corrected_translations.tsv"
        self.weights_path = "data/weights.json"
        self.corpus_path = "data/corpus.tsv"
    
    def test_translations_file_exists(self):
        """Test that the main translations file exists."""
        self.assertTrue(os.path.exists(self.translations_path),
                       f"Main translations file missing: {self.translations_path}")
    
    def test_translations_count(self):
        """Test that we have exactly 2,512 translations."""
        if not os.path.exists(self.translations_path):
            self.skipTest("Translations file not found")
            
        df = pd.read_csv(self.translations_path, sep='\t')
        self.assertEqual(len(df), 2512, "Should have exactly 2,512 translations")
    
    def test_translations_columns(self):
        """Test that translations file has required columns."""
        if not os.path.exists(self.translations_path):
            self.skipTest("Translations file not found")
            
        df = pd.read_csv(self.translations_path, sep='\t')
        required_columns = ['english_translation', 'sign_sequence']
        
        for col in required_columns:
            self.assertIn(col, df.columns, f"Missing required column: {col}")
    
    def test_no_empty_translations(self):
        """Test that we don't have empty translations."""
        if not os.path.exists(self.translations_path):
            self.skipTest("Translations file not found")
            
        df = pd.read_csv(self.translations_path, sep='\t')
        empty_translations = df['english_translation'].isna().sum()
        
        # Allow up to 1% empty translations  
        max_empty = len(df) * 0.01
        self.assertLessEqual(empty_translations, max_empty,
                           f"Too many empty translations: {empty_translations}")

class TestRevolutionaryFindings(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        self.translations_path = "output/corrected_translations.tsv"
    
    def test_family_authority_ratio(self):
        """Test that family references dominate authority references."""
        if not os.path.exists(self.translations_path):
            self.skipTest("Translations file not found")
            
        from indus.analysis import analyze_vocabulary, load_translations
        
        translations = load_translations(self.translations_path)
        vocab = analyze_vocabulary(translations)
        
        family_auth_ratio = vocab.get('family_authority_ratio', 0)
        self.assertGreater(family_auth_ratio, 3.0,
                          f"Family-authority ratio too low: {family_auth_ratio}")
    
    def test_secular_society(self):
        """Test that religious content is minimal (secular society)."""
        if not os.path.exists(self.translations_path):
            self.skipTest("Translations file not found")
            
        from indus.analysis import analyze_vocabulary, load_translations
        
        translations = load_translations(self.translations_path)
        vocab = analyze_vocabulary(translations)
        
        religious_pct = vocab.get('religious_percentage', 100)
        self.assertLess(religious_pct, 2.0,
                       f"Religious content too high: {religious_pct}%")
    
    def test_father_most_common(self):
        """Test that 'father' is the most common word."""
        if not os.path.exists(self.translations_path):
            self.skipTest("Translations file not found")
            
        from indus.analysis import analyze_vocabulary, load_translations
        
        translations = load_translations(self.translations_path)
        vocab = analyze_vocabulary(translations)
        
        word_freq = vocab.get('word_frequency', {})
        if word_freq:
            most_common_word = list(word_freq.keys())[0]
            self.assertEqual(most_common_word, 'father',
                           f"Expected 'father' to be most common, got '{most_common_word}'")

if __name__ == '__main__':
    unittest.main() 