#!/usr/bin/env python3
"""
PHASE 1: Extract authoritative sign & inscription tables from Mahadevan 77 PDF
Extracts real archaeological data - no synthetic generation
"""

import pandas as pd
import camelot
import tabula
import numpy as np
import json
import os
from pathlib import Path

def extract_sign_list_tables(pdf_path, output_dir):
    """Extract sign list tables using camelot for better table detection"""
    print("🔍 Extracting sign list tables with camelot...")
    
    try:
        # Extract all tables from the PDF
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
        print(f"✓ Found {len(tables)} potential tables")
        
        sign_tables = []
        for i, table in enumerate(tables):
            df = table.df
            
            # Look for tables that contain sign data
            if df.shape[1] >= 3 and df.shape[0] > 5:
                # Check if it contains numeric sign IDs and descriptions
                first_col = df.iloc[:, 0].astype(str)
                if any(first_col.str.match(r'^\d+$')):
                    print(f"✓ Found sign table {i} with {df.shape[0]} rows, {df.shape[1]} cols")
                    
                    # Clean and standardize the table
                    df.columns = [f'col_{j}' for j in range(df.shape[1])]
                    df['table_id'] = i
                    df['confidence'] = table.accuracy
                    sign_tables.append(df)
        
        if sign_tables:
            # Combine all sign tables
            all_signs = pd.concat(sign_tables, ignore_index=True)
            sign_output = output_dir / 'mahadevan_sign_list.csv'
            all_signs.to_csv(sign_output, index=False)
            print(f"✓ Saved {len(all_signs)} sign entries to {sign_output}")
            return all_signs
        else:
            print("⚠ No sign tables found")
            return None
            
    except Exception as e:
        print(f"❌ Camelot extraction failed: {e}")
        return None

def extract_concordance_tables(pdf_path, output_dir):
    """Extract concordance/inscription tables"""
    print("🔍 Extracting concordance tables with tabula...")
    
    try:
        # Use tabula for better text extraction
        all_tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
        print(f"✓ Found {len(all_tables)} tables with tabula")
        
        concordance_tables = []
        for i, df in enumerate(all_tables):
            if df.shape[1] >= 2 and df.shape[0] > 3:
                # Look for tables with inscription numbers and sequences
                first_col = df.iloc[:, 0].astype(str)
                if any(first_col.str.contains(r'\d+', na=False)):
                    print(f"✓ Found concordance table {i} with {df.shape[0]} rows")
                    df['table_source'] = f'tabula_{i}'
                    concordance_tables.append(df)
        
        if concordance_tables:
            all_concordance = pd.concat(concordance_tables, ignore_index=True)
            conc_output = output_dir / 'mahadevan_concordance.csv'
            all_concordance.to_csv(conc_output, index=False)
            print(f"✓ Saved {len(all_concordance)} concordance entries to {conc_output}")
            return all_concordance
        else:
            print("⚠ No concordance tables found")
            return None
            
    except Exception as e:
        print(f"❌ Tabula extraction failed: {e}")
        return None

def main():
    """Main extraction pipeline"""
    print("🚀 PHASE 1: MAHADEVAN 77 TABLE EXTRACTION")
    print("=========================================")
    
    # Set up paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / 'data'
    output_dir = project_root / 'output'
    output_dir.mkdir(exist_ok=True)
    
    pdf_path = data_dir / 'mahadevan77_original.pdf'
    
    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    print(f"📖 Processing: {pdf_path}")
    print(f"📁 Output directory: {output_dir}")
    
    # Extract different types of tables
    sign_data = extract_sign_list_tables(str(pdf_path), output_dir)
    concordance_data = extract_concordance_tables(str(pdf_path), output_dir)
    
    # Create summary
    summary = {
        'extraction_timestamp': pd.Timestamp.now().isoformat(),
        'source_document': 'Mahadevan 1977 - The Indus Script: Texts, Concordance and Tables',
        'extraction_method': 'camelot + tabula',
        'data_quality': 'archaeological_primary_source',
        'sign_list': {
            'extracted': sign_data is not None,
            'count': len(sign_data) if sign_data is not None else 0
        },
        'concordance': {
            'extracted': concordance_data is not None,
            'count': len(concordance_data) if concordance_data is not None else 0
        }
    }
    
    summary_path = output_dir / 'extraction_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print("\n📊 EXTRACTION COMPLETE")
    print("======================")
    print(f"Signs extracted: {summary['sign_list']['count']}")
    print(f"Concordance entries: {summary['concordance']['count']}")
    
    if any([sign_data is not None, concordance_data is not None]):
        print("✅ Phase 1 successful - Real archaeological data extracted!")
    else:
        print("❌ Phase 1 failed - No valid tables extracted")

if __name__ == "__main__":
    main() 