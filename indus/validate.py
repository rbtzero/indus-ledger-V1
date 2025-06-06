"""
Data validation functions for the Indus Valley decipherment project.
"""

import os
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple

def validate_data() -> Dict:
    """
    Validate all core data files and return validation results.
    
    Returns:
        Dictionary with validation status for each component
    """
    results = {}
    
    # Check translations file (most important)
    translations_path = "output/corrected_translations.tsv"
    if os.path.exists(translations_path):
        try:
            df = pd.read_csv(translations_path, sep='\t')
            expected_count = 2512
            actual_count = len(df)
            
            results['translations'] = {
                'status': 'PASS' if actual_count == expected_count else 'WARNING',
                'expected_inscriptions': expected_count,
                'actual_inscriptions': actual_count,
                'columns': list(df.columns),
                'required_columns': ['english_translation', 'sign_sequence']
            }
        except Exception as e:
            results['translations'] = {
                'status': 'FAIL',
                'error': str(e)
            }
    else:
        results['translations'] = {
            'status': 'FAIL',
            'error': f'File not found: {translations_path}'
        }
    
    # Check weights file
    weights_path = "data/weights.json"
    if os.path.exists(weights_path):
        try:
            import json
            with open(weights_path, 'r') as f:
                weights = json.load(f)
            results['weights'] = {
                'status': 'PASS',
                'sign_count': len(weights),
                'expected_signs': 75
            }
        except Exception as e:
            results['weights'] = {
                'status': 'FAIL',
                'error': str(e)
            }
    else:
        results['weights'] = {
            'status': 'WARNING',
            'error': f'File not found: {weights_path}'
        }
    
    # Check corpus file
    corpus_path = "data/corpus.tsv"
    if os.path.exists(corpus_path):
        try:
            df = pd.read_csv(corpus_path, sep='\t')
            results['corpus'] = {
                'status': 'PASS',
                'inscription_count': len(df),
                'columns': list(df.columns)
            }
        except Exception as e:
            results['corpus'] = {
                'status': 'FAIL',
                'error': str(e)
            }
    else:
        results['corpus'] = {
            'status': 'WARNING',
            'error': f'File not found: {corpus_path}'
        }
    
    # Overall status
    statuses = [r.get('status', 'FAIL') for r in results.values()]
    if 'FAIL' in statuses:
        overall_status = 'FAIL'
    elif 'WARNING' in statuses:
        overall_status = 'WARNING'
    else:
        overall_status = 'PASS'
    
    results['overall'] = {'status': overall_status}
    
    return results

def check_revolutionary_findings() -> bool:
    """
    Verify that the revolutionary findings are reproducible from the data.
    
    Returns:
        True if findings can be reproduced, False otherwise
    """
    try:
        from .analysis import load_translations, analyze_vocabulary
        
        # Load translations
        translations = load_translations()
        
        # Verify key findings
        vocab = analyze_vocabulary(translations)
        
        # Check family-authority ratio (should be > 3.0)
        family_auth_ratio = vocab.get('family_authority_ratio', 0)
        
        # Check religious content (should be < 2%)
        religious_pct = vocab.get('religious_percentage', 100)
        
        # Check inscription count (should be 2,512)
        inscription_count = len(translations)
        
        findings_validated = (
            family_auth_ratio > 3.0 and
            religious_pct < 2.0 and
            inscription_count == 2512
        )
        
        return findings_validated
        
    except Exception:
        return False 