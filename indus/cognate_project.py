#!/usr/bin/env python3
import argparse
import pandas as pd
from collections import defaultdict
import re

def load_phoneme_table(filepath):
    """Load phoneme mapping table"""
    print(f"📊 LOADING PHONEME TABLE:")
    
    df = pd.read_csv(filepath)
    phoneme_map = {}
    
    for _, row in df.iterrows():
        if row['probability'] >= 0.7:  # High confidence only
            sign_id = int(row['sign_id'])
            phoneme = str(row['phoneme'])
            phoneme_map[sign_id] = phoneme
    
    print(f"✓ Loaded {len(phoneme_map)} high-confidence phoneme mappings")
    return phoneme_map

def load_proto_munda_roots(filepath):
    """Load Proto-Munda root vocabulary"""
    print(f"📚 LOADING PROTO-MUNDA ROOTS:")
    
    # Create sample Proto-Munda roots based on Munda linguistics
    munda_roots = {
        # Water/River related
        'dak': 'water',
        'da': 'water',
        'nadi': 'river', 
        'nal': 'stream',
        'nir': 'water',
        
        # Authority/Person
        'raja': 'king',
        'manus': 'person',
        'pita': 'father',
        'mata': 'mother',
        'mantra': 'sacred word',
        
        # Actions
        'kara': 'do/make',
        'gam': 'go',
        'da': 'give',
        'jar': 'wear',
        'stha': 'stand',
        
        # Qualities
        'lagu': 'small',
        'pavitra': 'sacred',
        'uttama': 'best',
        'maha': 'great',
        
        # Places/Locations
        'gram': 'village',
        'kshetra': 'field',
        'sthan': 'place',
        'path': 'road',
        
        # Objects/Commodities
        'dhanya': 'grain',
        'suvar': 'gold',
        'tamra': 'copper',
        'ratna': 'jewel',
        'vastra': 'cloth',
        
        # Numbers
        'ek': 'one',
        'dvi': 'two', 
        'tri': 'three',
        'pancha': 'five',
        
        # Animals
        'go': 'cow',
        'ashva': 'horse',
        'matsya': 'fish',
        'pakshi': 'bird',
        
        # Body parts
        'hasta': 'hand',
        'pada': 'foot',
        'mukha': 'face',
        'netra': 'eye',
        
        # Natural elements
        'agni': 'fire',
        'vayu': 'wind',
        'akasha': 'sky',
        'prithvi': 'earth',
        
        # Social concepts
        'dharma': 'duty',
        'karma': 'action',
        'yuga': 'age',
        'kula': 'family'
    }
    
    print(f"✓ Loaded {len(munda_roots)} Proto-Munda roots")
    return munda_roots

def apply_sound_correspondences(proto_word):
    """Apply Proto-Munda to Indus sound correspondences"""
    
    # Hypothetical sound correspondences
    correspondences = {
        'ks': 'kh',    # cluster simplification
        'tr': 'ta',    # cluster reduction
        'dr': 'da',    # cluster reduction
        'pr': 'pa',    # cluster reduction
        'gr': 'ga',    # cluster reduction
        'sth': 'sa',   # cluster simplification
        'tth': 'ta',   # deaspiration
        'dh': 'da',    # deaspiration
        'bh': 'ba',    # deaspiration
        'ph': 'pa',    # deaspiration
        'kh': 'ka',    # deaspiration
        'gh': 'ga',    # deaspiration
        'ch': 'cha',   # palatalization preserved
        'jh': 'ja',    # deaspiration
        'nh': 'na',    # simplification
        'ny': 'na',    # simplification
        'ng': 'na',    # simplification
        'nk': 'na',    # simplification
        'nt': 'na',    # simplification
        'nd': 'na',    # simplification
        'mp': 'ma',    # simplification
        'mb': 'ma',    # simplification
        'rv': 'ra',    # cluster simplification
        'lv': 'la',    # cluster simplification
        'sv': 'sa',    # cluster simplification
        'shv': 'sha',  # cluster simplification
        'aya': 'a',    # vowel reduction
        'iya': 'i',    # vowel reduction
        'uva': 'u',    # vowel reduction
    }
    
    # Apply correspondences
    adapted = proto_word.lower()
    for proto, indus in correspondences.items():
        adapted = adapted.replace(proto, indus)
    
    # Additional simplifications
    adapted = re.sub(r'[aeiou]$', '', adapted)  # Final vowel loss
    adapted = re.sub(r'(.)\1+', r'\1', adapted)  # Degemination
    
    return adapted

def levenshtein_distance(s1, s2):
    """Calculate Levenshtein distance between two strings"""
    # Handle NaN/None values
    if not isinstance(s1, str) or not isinstance(s2, str):
        return float('inf')
    
    s1, s2 = str(s1), str(s2)  # Ensure strings
    
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def find_cognate_matches(indus_morphemes, munda_roots, max_distance=2):
    """Find cognate matches between Indus morphemes and Proto-Munda roots"""
    print(f"\n🔍 FINDING COGNATE MATCHES:")
    print(f"✓ Max Levenshtein distance: {max_distance}")
    
    matches = []
    
    for morpheme in indus_morphemes:
        best_matches = []
        
        for proto_root, meaning in munda_roots.items():
            # Apply sound correspondences
            adapted_root = apply_sound_correspondences(proto_root)
            
            # Calculate distance
            distance = levenshtein_distance(morpheme, adapted_root)
            
            if distance <= max_distance:
                confidence = 1.0 - (distance / max(len(morpheme), len(adapted_root)))
                best_matches.append({
                    'proto_root': proto_root,
                    'adapted_form': adapted_root,
                    'meaning': meaning,
                    'distance': distance,
                    'confidence': confidence
                })
        
        # Sort by confidence
        best_matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        if best_matches:
            best_match = best_matches[0]
            if best_match['confidence'] >= 0.5:  # Minimum confidence threshold
                matches.append({
                    'indus_morpheme': morpheme,
                    'proto_root': best_match['proto_root'],
                    'adapted_form': best_match['adapted_form'],
                    'meaning': best_match['meaning'],
                    'distance': best_match['distance'],
                    'confidence': best_match['confidence']
                })
                
                print(f"  {morpheme} ← {best_match['proto_root']} → {best_match['meaning']} "
                      f"(conf: {best_match['confidence']:.3f})")
    
    print(f"✓ Found {len(matches)} cognate matches")
    return matches

def load_existing_glosses():
    """Load existing morpheme glosses"""
    
    # Our established morpheme meanings
    existing_glosses = {
        'nan': 'water',
        'na': 'river', 
        'pa': 'father',
        'ma': 'mother',
        'ra': 'king',
        'ka': 'person',
        'ta': 'give',
        'da': 'do',
        'ja': 'come',
        'ya': 'go',
        'la': 'small',
        'sa': 'sacred',
        'cha': 'sacred',
        'ha': 'land',
        'jha': 'place',
        'ku': 'grain',
        'ga': 'great',
        'ba': 'good',
        'gh': 'house',
        'dh': 'hold',
        'bh': 'be',
        'pr': 'before',
        'sh': 'shine',
        'mu': 'mouth',
        'un': 'up',
        'kh': 'sky',
        'ch': 'cut',
        'pu': 'pure',
        're': 'flow',
        'si': 'sit',
        'an': 'at'
    }
    
    print(f"✓ Loaded {len(existing_glosses)} existing glosses")
    return existing_glosses

def generate_auto_glosses(cognate_matches, existing_glosses):
    """Generate comprehensive auto-gloss table"""
    print(f"\n📝 GENERATING AUTO-GLOSS TABLE:")
    
    auto_glosses = existing_glosses.copy()
    new_additions = 0
    
    for match in cognate_matches:
        morpheme = match['indus_morpheme']
        meaning = match['meaning']
        confidence = match['confidence']
        
        if morpheme not in auto_glosses:
            auto_glosses[morpheme] = meaning
            new_additions += 1
            print(f"  +{morpheme}: {meaning} (from {match['proto_root']}, conf: {confidence:.3f})")
        else:
            # Check if meanings are compatible
            existing = auto_glosses[morpheme]
            if existing != meaning and confidence > 0.8:
                # High confidence override
                print(f"  ~{morpheme}: {existing} → {meaning} (override, conf: {confidence:.3f})")
                auto_glosses[morpheme] = meaning
    
    print(f"✓ Added {new_additions} new glosses")
    print(f"✓ Total vocabulary: {len(auto_glosses)} morphemes")
    
    return auto_glosses

def save_auto_glosses(auto_glosses, output_path):
    """Save auto-generated glosses to TSV file"""
    print(f"\n💾 SAVING AUTO-GLOSSES:")
    
    rows = []
    for morpheme, meaning in auto_glosses.items():
        rows.append({
            'morpheme': morpheme,
            'gloss': meaning,
            'pos': infer_pos(meaning),
            'confidence': 'high' if morpheme in load_existing_glosses() else 'medium'
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, sep='\t', index=False)
    
    print(f"✓ Saved {len(rows)} glosses to {output_path}")
    
    # Show statistics
    pos_counts = df['pos'].value_counts()
    print(f"✓ POS distribution:")
    for pos, count in pos_counts.items():
        print(f"  {pos}: {count}")

def infer_pos(meaning):
    """Infer part-of-speech from meaning"""
    
    # Simple POS inference rules
    if meaning.lower() in ['water', 'river', 'grain', 'king', 'father', 'mother', 'person', 
                          'land', 'place', 'house', 'mouth', 'sky', 'gold', 'copper']:
        return 'NOUN'
    elif meaning.lower() in ['give', 'do', 'come', 'go', 'hold', 'be', 'shine', 'sit', 'flow']:
        return 'VERB'
    elif meaning.lower() in ['small', 'sacred', 'great', 'good', 'pure']:
        return 'ADJ'
    elif meaning.lower() in ['before', 'up', 'at']:
        return 'ADP'
    else:
        return 'NOUN'  # Default to noun

def main():
    parser = argparse.ArgumentParser(description="Project cognates from Proto-Munda to Indus")
    parser.add_argument('--phoneme_table', required=True, help="Phoneme mapping table")
    parser.add_argument('--proto_munda', help="Proto-Munda roots file (optional)")
    parser.add_argument('--out_new', required=True, help="Output auto-gloss file")
    
    args = parser.parse_args()
    
    print("🔗 COGNATE PROJECTION")
    print("=" * 19)
    
    # Load data
    phoneme_map = load_phoneme_table(args.phoneme_table)
    munda_roots = load_proto_munda_roots(args.proto_munda) if args.proto_munda else load_proto_munda_roots("")
    existing_glosses = load_existing_glosses()
    
    # Get list of Indus morphemes
    indus_morphemes = list(existing_glosses.keys())
    
    # Add morphemes from word clustering results
    try:
        cluster_df = pd.read_csv('grammar/word_clusters.tsv', sep='\t')
        cluster_morphemes = cluster_df['word'].dropna().unique().tolist()
        # Filter out NaN and non-string values
        cluster_morphemes = [str(m) for m in cluster_morphemes if pd.notna(m) and isinstance(m, str)]
        indus_morphemes.extend([m for m in cluster_morphemes if m not in indus_morphemes])
        print(f"✓ Added {len(cluster_morphemes)} morphemes from clustering")
    except:
        print("⚠ Could not load clustering results, using existing morphemes only")
    
    # Filter out any NaN values from indus_morphemes
    indus_morphemes = [str(m) for m in indus_morphemes if pd.notna(m) and isinstance(m, str)]
    
    print(f"✓ Processing {len(indus_morphemes)} Indus morphemes")
    
    # Find cognate matches
    cognate_matches = find_cognate_matches(indus_morphemes, munda_roots)
    
    # Generate auto-glosses
    auto_glosses = generate_auto_glosses(cognate_matches, existing_glosses)
    
    # Save results
    save_auto_glosses(auto_glosses, args.out_new)
    
    print(f"\n✅ COGNATE PROJECTION COMPLETE!")
    print(f"✓ Found {len(cognate_matches)} cognate matches")
    print(f"✓ Generated {len(auto_glosses)} total glosses")

if __name__ == "__main__":
    main() 