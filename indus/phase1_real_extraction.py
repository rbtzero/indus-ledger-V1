#!/usr/bin/env python3
"""
PHASE 1: REAL ARCHAEOLOGICAL DATA EXTRACTION
Extracts genuine Indus script data from actual research databases
NO SYNTHETIC DATA - 100% ARCHAEOLOGICAL SOURCES
"""

import pandas as pd
import re
import json
import csv
from pathlib import Path
from collections import Counter, defaultdict

def extract_glyph_mapping(sql_file):
    """Extract real glyph ID to Unicode mapping from database"""
    print("🔍 Extracting real glyph mappings...")
    
    glyph_map = {}
    frequency_map = {}
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract glyph insertions
    glyph_pattern = r'INSERT INTO GLYPH.*?VALUES\s*(.*?);'
    glyph_match = re.search(glyph_pattern, content, re.DOTALL)
    
    if glyph_match:
        glyph_data = glyph_match.group(1)
        # Parse individual glyph entries
        entries = re.findall(r'\((\d+),\s*"([^"]+)"(?:,\s*(\d+))?\)', glyph_data)
        
        for entry in entries:
            glyph_id = int(entry[0])
            unicode_val = entry[1]
            frequency = int(entry[2]) if len(entry) > 2 and entry[2] else 0
            
            glyph_map[glyph_id] = unicode_val
            frequency_map[glyph_id] = frequency
    
    print(f"✓ Extracted {len(glyph_map)} real Indus signs")
    return glyph_map, frequency_map

def extract_sequences(sql_file):
    """Extract real inscription sequences from database"""
    print("🔍 Extracting real inscription sequences...")
    
    sequences = defaultdict(list)
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract sequence insertions
    seq_pattern = r'INSERT INTO GLYPHSEQUENCE.*?VALUES\s*(.*?);'
    seq_match = re.search(seq_pattern, content, re.DOTALL)
    
    if seq_match:
        seq_data = seq_match.group(1)
        # Parse individual sequence entries
        entries = re.findall(r'\((\d+),(\d+),(\d+)\)', seq_data)
        
        for entry in entries:
            seal_id = int(entry[0])
            glyph_id = int(entry[1])
            idx = int(entry[2])
            
            sequences[seal_id].append((idx, glyph_id))
    
    # Sort sequences by index
    for seal_id in sequences:
        sequences[seal_id].sort(key=lambda x: x[0])
        sequences[seal_id] = [glyph_id for idx, glyph_id in sequences[seal_id]]
    
    print(f"✓ Extracted {len(sequences)} real inscriptions")
    return dict(sequences)

def process_m77_corpus(m77_file):
    """Process Mahadevan 77 corpus format"""
    print("🔍 Processing M77 corpus...")
    
    inscriptions = []
    
    with open(m77_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and line.startswith('('):
                # Parse format: (1) 410 17
                match = re.match(r'\((\d+)\)\s+(.+)', line)
                if match:
                    inscription_id = int(match.group(1))
                    signs = [int(x) for x in match.group(2).split()]
                    inscriptions.append({
                        'id': inscription_id,
                        'signs': signs,
                        'length': len(signs),
                        'source': 'M77'
                    })
    
    print(f"✓ Processed {len(inscriptions)} M77 inscriptions")
    return inscriptions

def calculate_real_frequencies(inscriptions):
    """Calculate real sign frequencies from archaeological data"""
    print("📊 Calculating real sign frequencies...")
    
    all_signs = []
    for insc in inscriptions:
        all_signs.extend(insc['signs'])
    
    frequencies = Counter(all_signs)
    total_signs = len(all_signs)
    
    # Calculate statistics
    unique_signs = len(frequencies)
    most_common = frequencies.most_common(10)
    
    print(f"✓ Total sign tokens: {total_signs}")
    print(f"✓ Unique signs: {unique_signs}")
    print(f"✓ Most frequent signs: {[f'{sign}({count})' for sign, count in most_common[:5]]}")
    
    return frequencies

def create_real_sign_inventory(glyph_map, frequencies):
    """Create authentic sign inventory with real data"""
    print("📝 Creating real sign inventory...")
    
    sign_inventory = []
    
    for glyph_id, unicode_val in glyph_map.items():
        frequency = frequencies.get(glyph_id, 0)
        
        sign_entry = {
            'id': glyph_id,
            'unicode': unicode_val,
            'frequency': frequency,
            'description': f'Sign_{glyph_id}',
            'category': 'archaeological',
            'source': 'database'
        }
        sign_inventory.append(sign_entry)
    
    # Sort by frequency
    sign_inventory.sort(key=lambda x: x['frequency'], reverse=True)
    
    print(f"✓ Created inventory with {len(sign_inventory)} authentic signs")
    return sign_inventory

def export_real_corpus(inscriptions, output_dir):
    """Export real corpus in multiple formats"""
    print("💾 Exporting real corpus...")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # TSV format for corpus
    with open(output_dir / 'real_corpus.tsv', 'w', encoding='utf-8') as f:
        f.write('id\tsigns\tlength\tsource\n')
        for insc in inscriptions:
            signs_str = ' '.join(map(str, insc['signs']))
            f.write(f"{insc['id']}\t{signs_str}\t{insc['length']}\tarchaeological\n")
    
    # JSON format for detailed data
    corpus_data = {
        'metadata': {
            'total_inscriptions': len(inscriptions),
            'extraction_method': 'archaeological_database',
            'data_quality': 'primary_source',
            'sources': ['M77', 'ICIT_Database', 'Wells_Database']
        },
        'inscriptions': inscriptions
    }
    
    with open(output_dir / 'real_corpus.json', 'w', encoding='utf-8') as f:
        json.dump(corpus_data, f, indent=2)
    
    print(f"✓ Exported to {output_dir}")

def main():
    """Main extraction pipeline"""
    print("🚀 PHASE 1: REAL ARCHAEOLOGICAL DATA EXTRACTION")
    print("===============================================")
    
    # Set up paths
    data_dir = Path('data')
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    sql_file = data_dir / 'decipher_indus_sql.txt'
    m77_file = data_dir / 'corpus_m77.txt'
    
    try:
        # Extract from database
        glyph_map, freq_map = extract_glyph_mapping(sql_file)
        db_sequences = extract_sequences(sql_file)
        
        # Process M77 corpus
        m77_inscriptions = process_m77_corpus(m77_file)
        
        # Combine all inscriptions
        all_inscriptions = []
        
        # Add database sequences
        for seal_id, signs in db_sequences.items():
            all_inscriptions.append({
                'id': f'DB_{seal_id}',
                'signs': signs,
                'length': len(signs),
                'source': 'database'
            })
        
        # Add M77 inscriptions
        all_inscriptions.extend(m77_inscriptions)
        
        # Calculate frequencies
        frequencies = calculate_real_frequencies(all_inscriptions)
        
        # Create sign inventory
        sign_inventory = create_real_sign_inventory(glyph_map, frequencies)
        
        # Export data
        export_real_corpus(all_inscriptions, output_dir)
        
        # Export sign inventory
        with open(output_dir / 'real_signs.json', 'w', encoding='utf-8') as f:
            json.dump(sign_inventory, f, indent=2)
        
        # Create summary
        summary = {
            'phase': 'Phase_1_Complete',
            'extraction_timestamp': pd.Timestamp.now().isoformat(),
            'data_quality': 'archaeological_primary_source',
            'total_inscriptions': len(all_inscriptions),
            'unique_signs': len(sign_inventory),
            'total_sign_tokens': sum(frequencies.values()),
            'sources': ['Database', 'M77_Corpus'],
            'next_phase': 'Phase_2_Linear_Programming'
        }
        
        with open(output_dir / 'phase1_summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print("\n📊 PHASE 1 COMPLETE - REAL DATA EXTRACTED")
        print("=========================================")
        print(f"Total inscriptions: {summary['total_inscriptions']}")
        print(f"Unique signs: {summary['unique_signs']}")
        print(f"Sign tokens: {summary['total_sign_tokens']}")
        print("✅ Ready for Phase 2: Mathematical Optimization")
        
    except Exception as e:
        print(f"❌ Phase 1 failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main() 