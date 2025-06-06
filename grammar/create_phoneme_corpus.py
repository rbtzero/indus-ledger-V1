#!/usr/bin/env python3
import pandas as pd
import re
import pathlib

print("🔤 CREATING PHONEME CORPUS FOR GRAMMAR ANALYSIS")
print("=" * 48)

# Load our actual data
phoneme_df = pd.read_csv('output/phase_a_expanded_phoneme_table.csv')
ledger_df = pd.read_csv('data/ledger_en.tsv', sep='\t')
corpus_df = pd.read_csv('data/corpus.tsv', sep='\t')
real_corpus_df = pd.read_csv('output/indus_proper_name_candidates.csv')

print(f"✓ Loaded {len(phoneme_df)} phoneme mappings")
print(f"✓ Loaded {len(ledger_df)} ledger inscriptions")
print(f"✓ Loaded {len(real_corpus_df)} archaeological inscriptions")

# Create phoneme dictionary
unified_phoneme_dict = {}
for _, row in phoneme_df.iterrows():
    if row['probability'] >= 0.7:
        sign_id = int(row['sign_id'])
        phoneme = str(row['phoneme'])
        unified_phoneme_dict[sign_id] = phoneme

print(f"✓ Created phoneme dictionary: {len(unified_phoneme_dict)} mappings")

def extract_sign_id(sign_string):
    """Extract sign ID from various formats"""
    if ' ' not in str(sign_string):
        clean = re.sub(r'[^0-9]', '', str(sign_string))
        if clean.isdigit():
            return int(clean)
    return None

def signs_to_phonemes(signs_string):
    """Convert sign sequence to phoneme sequence"""
    signs = str(signs_string).split()
    phonemes = []
    
    for sign in signs:
        sign_id = extract_sign_id(sign)
        if sign_id and sign_id in unified_phoneme_dict:
            phoneme = unified_phoneme_dict[sign_id]
            # Clean phoneme for grammar analysis
            clean_phoneme = re.sub(r'[^a-zŋɲɳɽʈāīūēōàìùèò ]', '', phoneme.lower())
            if clean_phoneme.strip():
                phonemes.append(clean_phoneme.strip())
    
    return ' '.join(phonemes)

# Process all inscription sources
all_phoneme_sequences = []

# Process ledger data
print("\n📚 Processing ledger inscriptions...")
ledger_count = 0
for _, row in ledger_df.iterrows():
    phoneme_seq = signs_to_phonemes(row['sign_string'])
    if phoneme_seq.strip():
        all_phoneme_sequences.append(phoneme_seq)
        ledger_count += 1

# Process archaeological data
print("📚 Processing archaeological inscriptions...")
arch_count = 0
for _, row in real_corpus_df.iterrows():
    phoneme_seq = signs_to_phonemes(row['sign_sequence'])
    if phoneme_seq.strip():
        all_phoneme_sequences.append(phoneme_seq)
        arch_count += 1

# Process core corpus
print("📚 Processing core corpus...")
core_count = 0
for _, row in corpus_df.iterrows():
    phoneme_seq = signs_to_phonemes(row['signs'])
    if phoneme_seq.strip():
        all_phoneme_sequences.append(phoneme_seq)
        core_count += 1

print(f"\n✓ Processed {ledger_count} ledger sequences")
print(f"✓ Processed {arch_count} archaeological sequences")
print(f"✓ Processed {core_count} core sequences")
print(f"✓ Total phoneme sequences: {len(all_phoneme_sequences)}")

# Write phoneme corpus
pathlib.Path('grammar').mkdir(exist_ok=True)
with open('grammar/phon_seq.txt', 'w') as f:
    for seq in all_phoneme_sequences:
        f.write(seq + '\n')

print(f"✓ Written phoneme corpus to grammar/phon_seq.txt")

# Show sample sequences
print(f"\n🔍 SAMPLE PHONEME SEQUENCES:")
for i, seq in enumerate(all_phoneme_sequences[:10]):
    print(f"  {i+1}. {seq}")

print(f"\n✅ PHONEME CORPUS READY FOR GRAMMAR ANALYSIS") 