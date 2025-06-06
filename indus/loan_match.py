#!/usr/bin/env python3
"""
Phase 3: Fuzzy match Indus strings with external names
Using consonant skeleton matching for robust comparison
"""
from fuzzywuzzy import fuzz
import pandas as pd
import re
import itertools

def cons_only(s):
    """Extract consonant skeleton by removing vowels"""
    return re.sub(r'[aeiouāīūṛḷeoAEIOU]', '', s.lower())

def fuzzy_match_names():
    """Perform fuzzy matching between Indus sequences and external names"""
    
    print("📋 Loading Indus candidates and external names...")
    
    # Load Indus proper noun candidates
    try:
        indus = pd.read_csv('output/proper_candidates.tsv', sep='\t')
        print(f"   Loaded {len(indus)} Indus candidates")
    except FileNotFoundError:
        print("❌ proper_candidates.tsv not found!")
        return
    
    # Load external name corpora
    try:
        meso = pd.read_csv('data/meso_names.tsv', sep='\t')['name']
        munda = pd.read_csv('data/munda_roots.tsv', sep='\t')['modern_cognate']
        drav = pd.read_csv('data/drav_roots.tsv', sep='\t')['modern_cognate']
        vedic = pd.read_csv('data/vedic_roots.tsv', sep='\t')['modern_cognate']
        
        print(f"   Loaded {len(meso)} Mesopotamian names")
        print(f"   Loaded {len(munda)} Munda roots")
        print(f"   Loaded {len(drav)} Dravidian roots")
        print(f"   Loaded {len(vedic)} Vedic roots")
    except FileNotFoundError as e:
        print(f"❌ Missing corpus file: {e}")
        return
    
    # Combine all external names
    external_names = list(meso) + list(munda) + list(drav) + list(vedic)
    external_names = [str(name) for name in external_names if pd.notna(name)]
    
    print(f"🔍 Starting fuzzy matching with {len(external_names)} external names...")
    
    hits = []
    threshold = 70  # Minimum similarity score
    
    for _, row in indus.iterrows():
        # Convert Indus sequence to consonant skeleton
        # For now, treat sign numbers as placeholder consonants
        indus_seq = row['seq'].replace(' ', '')
        indus_cons = cons_only(indus_seq)
        
        # Try matching against external names
        for ext_name in external_names:
            ext_cons = cons_only(str(ext_name))
            
            # Skip very short names
            if len(ext_cons) < 2 or len(indus_cons) < 2:
                continue
                
            # Calculate similarity
            ratio = fuzz.ratio(indus_cons, ext_cons)
            partial_ratio = fuzz.partial_ratio(indus_cons, ext_cons)
            
            # Use best of the two ratios
            best_ratio = max(ratio, partial_ratio)
            
            if best_ratio >= threshold:
                hits.append({
                    'indus_seq': row['seq'],
                    'external_name': ext_name,
                    'indus_cons': indus_cons,
                    'external_cons': ext_cons,
                    'similarity': best_ratio,
                    'match_type': 'ratio' if ratio >= partial_ratio else 'partial'
                })
    
    print(f"📊 Found {len(hits)} matches with similarity ≥ {threshold}%")
    
    if hits:
        # Sort by similarity score
        hits_df = pd.DataFrame(hits)
        hits_df = hits_df.sort_values('similarity', ascending=False)
        
        # Save results
        hits_df.to_csv('output/loan_hits.tsv', sep='\t', index=False)
        
        print(f"✅ Saved {len(hits_df)} matches to output/loan_hits.tsv")
        print("\n📝 Top matches:")
        for _, hit in hits_df.head(10).iterrows():
            print(f"   {hit['indus_seq']} ↔ {hit['external_name']} ({hit['similarity']}%)")
            print(f"      Consonants: {hit['indus_cons']} ↔ {hit['external_cons']}")
    else:
        print("❌ No matches found above threshold")
        # Create empty file
        pd.DataFrame(columns=['indus_seq', 'external_name', 'similarity']).to_csv(
            'output/loan_hits.tsv', sep='\t', index=False)
    
    return len(hits)

if __name__ == "__main__":
    match_count = fuzzy_match_names()
    print(f"\n🎯 Phase 3 Complete: {match_count} fuzzy matches found") 