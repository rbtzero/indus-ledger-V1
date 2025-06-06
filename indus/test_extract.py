#!/usr/bin/env python3
"""
Test script to diagnose PDF extraction issues
"""

import pandas as pd
import camelot
import tabula
from pathlib import Path
import time

def test_camelot():
    """Test camelot extraction on a few pages"""
    print("🔍 Testing camelot extraction...")
    pdf_path = "data/mahadevan77_original.pdf"
    
    try:
        start_time = time.time()
        # Test on just first 5 pages
        tables = camelot.read_pdf(pdf_path, pages='1-5', flavor='lattice')
        end_time = time.time()
        
        print(f"✓ Camelot processed 5 pages in {end_time - start_time:.2f} seconds")
        print(f"✓ Found {len(tables)} tables")
        
        for i, table in enumerate(tables):
            print(f"  Table {i}: {table.df.shape[0]} rows × {table.df.shape[1]} cols")
            
        return len(tables) > 0
        
    except Exception as e:
        print(f"❌ Camelot failed: {e}")
        return False

def test_tabula():
    """Test tabula extraction on a few pages"""
    print("🔍 Testing tabula extraction...")
    pdf_path = "data/mahadevan77_original.pdf"
    
    try:
        start_time = time.time()
        # Test on just first 5 pages
        tables = tabula.read_pdf(pdf_path, pages='1-5', multiple_tables=True)
        end_time = time.time()
        
        print(f"✓ Tabula processed 5 pages in {end_time - start_time:.2f} seconds")
        print(f"✓ Found {len(tables)} tables")
        
        for i, df in enumerate(tables):
            print(f"  Table {i}: {df.shape[0]} rows × {df.shape[1]} cols")
            
        return len(tables) > 0
        
    except Exception as e:
        print(f"❌ Tabula failed: {e}")
        return False

def main():
    print("🚀 TESTING PDF EXTRACTION")
    print("==========================")
    
    # Test both extraction methods
    camelot_works = test_camelot()
    print()
    tabula_works = test_tabula()
    
    print("\n📊 TEST RESULTS")
    print("================")
    print(f"Camelot: {'✅ Working' if camelot_works else '❌ Failed'}")
    print(f"Tabula: {'✅ Working' if tabula_works else '❌ Failed'}")
    
    if camelot_works or tabula_works:
        print("✅ At least one extraction method works!")
        print("⏱ Full extraction will take much longer on all pages")
    else:
        print("❌ Both extraction methods failed")

if __name__ == "__main__":
    main() 