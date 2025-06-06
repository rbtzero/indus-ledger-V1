#!/usr/bin/env python3
import pandas as pd
from collections import Counter, defaultdict
import re

print("🔤 COMPREHENSIVE MORPHEME & AFFIX ANALYSIS")
print("=" * 43)

# Load segmented data
segmented_lines = []
with open('grammar/segmented.txt', 'r') as f:
    segmented_lines = [line.strip() for line in f if line.strip()]

# Load original phoneme sequences
original_sequences = []
with open('grammar/phon_seq.txt', 'r') as f:
    original_sequences = [line.strip() for line in f if line.strip()]

print(f"✓ Loaded {len(segmented_lines)} segmented morphemes")
print(f"✓ Loaded {len(original_sequences)} original sequences")

# Analyze morpheme frequency
morpheme_freq = Counter(segmented_lines)
print(f"✓ Found {len(morpheme_freq)} unique morphemes")

# Find potential affixes by analyzing sequence positions
print(f"\n🔍 POSITIONAL ANALYSIS:")

# Track morphemes by position in sequences
position_analysis = defaultdict(lambda: {'start': 0, 'middle': 0, 'end': 0, 'total': 0})

for seq in original_sequences:
    morphemes = seq.split()
    if len(morphemes) == 1:
        position_analysis[morphemes[0]]['start'] += 1
        position_analysis[morphemes[0]]['end'] += 1
    elif len(morphemes) > 1:
        # First position
        position_analysis[morphemes[0]]['start'] += 1
        # Last position
        position_analysis[morphemes[-1]]['end'] += 1
        # Middle positions
        for m in morphemes[1:-1]:
            position_analysis[m]['middle'] += 1
    
    for m in morphemes:
        position_analysis[m]['total'] += 1

# Identify potential function words/particles (high frequency, flexible position)
function_words = []
content_words = []
potential_affixes = []

for morpheme, positions in position_analysis.items():
    total = positions['total']
    if total >= 10:  # Minimum frequency threshold
        # Function words: appear in multiple positions
        position_ratio = (positions['start'] > 0) + (positions['middle'] > 0) + (positions['end'] > 0)
        
        if position_ratio >= 2 and total >= 20:
            function_words.append((morpheme, total, positions))
        elif positions['end'] > positions['start'] * 2:  # Strongly prefer final position
            potential_affixes.append((morpheme, total, positions))
        else:
            content_words.append((morpheme, total, positions))

print(f"\n🏷️ MORPHEME CLASSIFICATION:")
print(f"✓ Function words (flexible position): {len(function_words)}")
print(f"✓ Potential suffixes (end-preferring): {len(potential_affixes)}")
print(f"✓ Content words: {len(content_words)}")

# Show top function words
print(f"\n🔗 TOP FUNCTION WORDS/PARTICLES:")
for i, (morpheme, freq, pos) in enumerate(sorted(function_words, key=lambda x: x[1], reverse=True)[:10]):
    start_pct = pos['start'] / freq * 100
    end_pct = pos['end'] / freq * 100
    middle_pct = pos['middle'] / freq * 100
    print(f"  {i+1:2d}. '{morpheme}' ({freq} times) - Start:{start_pct:.0f}% Mid:{middle_pct:.0f}% End:{end_pct:.0f}%")

# Show potential suffixes
print(f"\n📎 POTENTIAL SUFFIXES:")
for i, (morpheme, freq, pos) in enumerate(sorted(potential_affixes, key=lambda x: x[1], reverse=True)[:10]):
    end_ratio = pos['end'] / pos['total'] * 100
    print(f"  {i+1:2d}. '+{morpheme}' ({freq} times) - End position: {end_ratio:.0f}%")

# Analyze frequent two-morpheme combinations for compound patterns
print(f"\n🔗 COMPOUND PATTERN ANALYSIS:")
two_morpheme_seqs = [seq for seq in original_sequences if len(seq.split()) == 2]
compound_patterns = Counter(two_morpheme_seqs)

print(f"✓ Found {len(two_morpheme_seqs)} two-morpheme sequences")
print(f"✓ Top compound patterns:")
for i, (pattern, freq) in enumerate(compound_patterns.most_common(10)):
    parts = pattern.split()
    print(f"  {i+1:2d}. '{parts[0]} + {parts[1]}' ({freq} times)")

# Analyze three-morpheme patterns for potential grammatical structures
print(f"\n📐 THREE-MORPHEME GRAMMATICAL PATTERNS:")
three_morpheme_seqs = [seq for seq in original_sequences if len(seq.split()) == 3]
three_patterns = Counter(three_morpheme_seqs)

print(f"✓ Found {len(three_morpheme_seqs)} three-morpheme sequences")
print(f"✓ Top three-morpheme patterns:")
for i, (pattern, freq) in enumerate(three_patterns.most_common(8)):
    parts = pattern.split()
    print(f"  {i+1:2d}. '{parts[0]} + {parts[1]} + {parts[2]}' ({freq} times)")

# Create word order analysis
print(f"\n📊 WORD ORDER ANALYSIS:")

# Load our English translations to identify word types
ledger_df = pd.read_csv('data/ledger_en.tsv', sep='\t')
translation_dict = {
    'na': 'river', 'ma': 'mother', 'sa': 'sacred', 'pa': 'father',
    'cha': 'sacred', 'jha': 'place', 'la': 'small', 'ra': 'king',
    'ka': 'person', 'ta': 'give', 'da': 'tree', 'ha': 'land',
    'ku': 'grain', 'ba': 'be', 'ja': 'come', 'ya': 'go'
}

# Analyze sequences with known word types
word_order_patterns = defaultdict(int)
for seq in original_sequences:
    morphemes = seq.split()
    if len(morphemes) >= 2:
        # Try to identify patterns
        translated = [translation_dict.get(m, 'UNK') for m in morphemes]
        if 'UNK' not in translated[:2]:  # Only analyze if we know the first two words
            pattern = f"{translated[0]}-{translated[1]}"
            word_order_patterns[pattern] += 1

print(f"✓ Word order patterns (semantic):")
for i, (pattern, freq) in enumerate(sorted(word_order_patterns.items(), key=lambda x: x[1], reverse=True)[:10]):
    print(f"  {i+1:2d}. {pattern} ({freq} times)")

# Save results
results = {
    'function_words': function_words,
    'potential_suffixes': potential_affixes,
    'content_words': content_words[:20],  # Top 20
    'compound_patterns': compound_patterns.most_common(20),
    'three_morpheme_patterns': three_patterns.most_common(15),
    'word_order_patterns': dict(word_order_patterns)
}

# Save affix candidates for next steps
affix_candidates = [morpheme for morpheme, freq, pos in potential_affixes]
with open('grammar/affix_candidates.txt', 'w') as f:
    f.write('\n'.join(affix_candidates))

# Save function words/particles
particles = [morpheme for morpheme, freq, pos in function_words]
with open('grammar/particles.txt', 'w') as f:
    f.write('\n'.join(particles))

print(f"\n✅ ANALYSIS COMPLETE:")
print(f"✓ Saved {len(affix_candidates)} affix candidates to grammar/affix_candidates.txt")
print(f"✓ Saved {len(particles)} function words to grammar/particles.txt")
print(f"✅ Ready for next phase: grammatical role analysis") 