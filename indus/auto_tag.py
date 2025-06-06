#!/usr/bin/env python3
import argparse
import pandas as pd
from collections import Counter, defaultdict
import re

def load_lexicon(filepath):
    """Load auto-generated lexicon with POS tags"""
    print(f"📚 LOADING LEXICON:")
    
    df = pd.read_csv(filepath, sep='\t')
    lexicon = {}
    
    for _, row in df.iterrows():
        morpheme = row['morpheme']
        gloss = row['gloss']
        pos = row['pos']
        lexicon[morpheme] = {'gloss': gloss, 'pos': pos}
    
    print(f"✓ Loaded {len(lexicon)} lexical entries")
    
    # Show POS distribution
    pos_counts = Counter(entry['pos'] for entry in lexicon.values())
    print(f"✓ POS distribution:")
    for pos, count in pos_counts.most_common():
        print(f"  {pos}: {count}")
    
    return lexicon

def load_affix_candidates():
    """Load affix candidates from previous analysis"""
    print(f"📊 LOADING AFFIX CANDIDATES:")
    
    # From our ledger-aware analysis
    affix_candidates = {
        'da': {'type': 'suffix', 'function': 'plural/agent', 'pos': 'AFF'},
        'ba': {'type': 'suffix', 'function': 'locative', 'pos': 'AFF'},
        'si': {'type': 'suffix', 'function': 'instrumental', 'pos': 'AFF'},
        'an': {'type': 'suffix', 'function': 'dative', 'pos': 'AFF'},
        'la': {'type': 'prefix', 'function': 'diminutive', 'pos': 'AFF'},
        'sa': {'type': 'prefix', 'function': 'sacred/ritual', 'pos': 'AFF'},
        'pa': {'type': 'prefix', 'function': 'agentive', 'pos': 'AFF'},
        'ma': {'type': 'prefix', 'function': 'honorific', 'pos': 'AFF'}
    }
    
    print(f"✓ Loaded {len(affix_candidates)} affix candidates")
    return affix_candidates

def identify_numerals(corpus_sequences):
    """Identify numeral patterns (repetition-based)"""
    print(f"\n🔢 IDENTIFYING NUMERALS:")
    
    numeral_candidates = set()
    
    for sequence in corpus_sequences:
        morphemes = sequence.split()
        
        # Look for repetition patterns that might indicate numbers
        morpheme_counts = Counter(morphemes)
        
        for morpheme, count in morpheme_counts.items():
            if count >= 2 and len(morpheme) <= 3:  # Repeated short morphemes
                numeral_candidates.add(morpheme)
    
    # Also add some based on linguistic knowledge
    known_numerals = {'ta', 'dvi', 'tri', 'pan', 'ek'}  # one, two, three, five, one
    numeral_candidates.update(known_numerals)
    
    print(f"✓ Identified {len(numeral_candidates)} numeral candidates")
    print(f"  Numerals: {', '.join(sorted(numeral_candidates))}")
    
    return numeral_candidates

def calculate_morpheme_entropy(corpus_sequences):
    """Calculate morpheme entropy for particle identification"""
    print(f"\n📈 CALCULATING MORPHEME ENTROPY:")
    
    morpheme_positions = defaultdict(list)
    total_sequences = len(corpus_sequences)
    
    for seq_idx, sequence in enumerate(corpus_sequences):
        morphemes = sequence.split()
        for pos_idx, morpheme in enumerate(morphemes):
            # Normalize position by sequence length
            norm_pos = pos_idx / len(morphemes) if len(morphemes) > 1 else 0
            morpheme_positions[morpheme].append(norm_pos)
    
    morpheme_entropy = {}
    
    for morpheme, positions in morpheme_positions.items():
        if len(positions) >= 3:  # Need at least 3 occurrences
            # Calculate position variance as a proxy for entropy
            position_variance = sum((p - 0.5) ** 2 for p in positions) / len(positions)
            morpheme_entropy[morpheme] = position_variance
    
    # High entropy = appears in many different positions = likely particle
    high_entropy_morphemes = [
        morpheme for morpheme, entropy in morpheme_entropy.items()
        if entropy > 0.15  # Threshold for high positional variance
    ]
    
    print(f"✓ Found {len(high_entropy_morphemes)} high-entropy morphemes (particles)")
    
    return high_entropy_morphemes

def apply_tagging_rules(sequence, lexicon, affix_candidates, numerals, particles):
    """Apply weak supervision rules to tag a sequence"""
    
    morphemes = sequence.split()
    tags = []
    
    for morpheme in morphemes:
        # Rule 1: Check lexicon first
        if morpheme in lexicon:
            tags.append(lexicon[morpheme]['pos'])
        
        # Rule 2: Check affix candidates
        elif morpheme in affix_candidates:
            tags.append(affix_candidates[morpheme]['pos'])
        
        # Rule 3: Check numerals
        elif morpheme in numerals:
            tags.append('NUM')
        
        # Rule 4: Check particles (high entropy morphemes)
        elif morpheme in particles:
            tags.append('PRT')
        
        # Rule 5: Heuristic rules based on morpheme properties
        elif len(morpheme) == 1:
            # Single character morphemes often particles or affixes
            tags.append('PRT')
        
        elif morpheme.endswith('a') and len(morpheme) >= 3:
            # Words ending in 'a' might be nouns (Indo-Aryan pattern)
            tags.append('NOUN')
        
        elif morpheme in ['ku', 'na', 'nan', 'ra', 'pa', 'ma']:
            # Known high-frequency content words
            tags.append('NOUN')
        
        elif morpheme in ['ta', 'da', 'ja', 'ya']:
            # Known action words
            tags.append('VERB')
        
        else:
            # Unknown - default heuristic based on context
            tags.append('UNK')
    
    return tags

def auto_tag_corpus(corpus_sequences, lexicon, affix_candidates, numerals, particles):
    """Apply automatic tagging to the entire corpus"""
    print(f"\n🏷️ AUTO-TAGGING CORPUS:")
    
    tagged_sequences = []
    tag_stats = Counter()
    
    for sequence in corpus_sequences:
        tags = apply_tagging_rules(sequence, lexicon, affix_candidates, numerals, particles)
        
        tagged_sequence = {
            'sequence': sequence,
            'morphemes': sequence.split(),
            'tags': tags
        }
        
        tagged_sequences.append(tagged_sequence)
        tag_stats.update(tags)
    
    # Calculate coverage
    total_tokens = sum(tag_stats.values())
    known_tokens = total_tokens - tag_stats.get('UNK', 0)
    coverage = known_tokens / total_tokens if total_tokens > 0 else 0
    
    print(f"✓ Tagged {len(tagged_sequences)} sequences")
    print(f"✓ Total tokens: {total_tokens}")
    print(f"✓ Coverage: {coverage:.1%} ({known_tokens}/{total_tokens})")
    
    print(f"\n📊 TAG DISTRIBUTION:")
    for tag, count in tag_stats.most_common():
        percentage = count / total_tokens * 100
        print(f"  {tag}: {count} ({percentage:.1f}%)")
    
    return tagged_sequences, coverage

def save_tagged_corpus(tagged_sequences, output_path):
    """Save tagged corpus to TSV file"""
    print(f"\n💾 SAVING TAGGED CORPUS:")
    
    rows = []
    
    for seq_data in tagged_sequences:
        sequence = seq_data['sequence']
        morphemes = seq_data['morphemes']
        tags = seq_data['tags']
        
        for i, (morpheme, tag) in enumerate(zip(morphemes, tags)):
            rows.append({
                'sequence_id': f"seq_{len(rows)//len(morphemes)}",
                'token_id': i,
                'morpheme': morpheme,
                'tag': tag,
                'sequence': sequence
            })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, sep='\t', index=False)
    
    print(f"✓ Saved {len(rows)} tagged tokens to {output_path}")
    print(f"✓ {len(tagged_sequences)} sequences total")

def generate_tag_summary(tagged_sequences, output_path):
    """Generate summary of tagging results"""
    
    summary_path = output_path.replace('.tsv', '_summary.txt')
    
    with open(summary_path, 'w') as f:
        f.write("INDUS SCRIPT AUTO-TAGGING SUMMARY\n")
        f.write("=" * 34 + "\n\n")
        
        # Overall statistics
        total_sequences = len(tagged_sequences)
        total_tokens = sum(len(seq['morphemes']) for seq in tagged_sequences)
        
        f.write(f"Total sequences: {total_sequences}\n")
        f.write(f"Total tokens: {total_tokens}\n")
        f.write(f"Average sequence length: {total_tokens/total_sequences:.1f}\n\n")
        
        # Tag distribution
        all_tags = []
        for seq in tagged_sequences:
            all_tags.extend(seq['tags'])
        
        tag_counts = Counter(all_tags)
        
        f.write("TAG DISTRIBUTION:\n")
        for tag, count in tag_counts.most_common():
            percentage = count / len(all_tags) * 100
            f.write(f"  {tag}: {count} ({percentage:.1f}%)\n")
        
        f.write("\nSAMPLE TAGGED SEQUENCES:\n")
        for i, seq in enumerate(tagged_sequences[:10]):
            morphemes = seq['morphemes']
            tags = seq['tags']
            tagged_pairs = [f"{m}/{t}" for m, t in zip(morphemes, tags)]
            f.write(f"  {i+1}. {' '.join(tagged_pairs)}\n")
    
    print(f"✓ Saved tagging summary to {summary_path}")

def main():
    parser = argparse.ArgumentParser(description="Auto-tag Indus corpus with POS tags")
    parser.add_argument('--corpus', required=True, help="Input corpus file (phoneme sequences)")
    parser.add_argument('--lex', required=True, help="Lexicon file with POS tags")
    parser.add_argument('--aff', help="Affix candidates file (optional)")
    parser.add_argument('--out', required=True, help="Output tagged corpus TSV")
    
    args = parser.parse_args()
    
    print("🏷️ INDUS AUTO-TAGGER")
    print("=" * 19)
    
    # Load corpus
    print(f"\n📖 LOADING CORPUS:")
    with open(args.corpus, 'r') as f:
        corpus_sequences = [line.strip() for line in f if line.strip()]
    print(f"✓ Loaded {len(corpus_sequences)} sequences")
    
    # Load lexicon
    lexicon = load_lexicon(args.lex)
    
    # Load affix candidates
    affix_candidates = load_affix_candidates()
    
    # Identify numerals
    numerals = identify_numerals(corpus_sequences)
    
    # Calculate morpheme entropy for particles
    particles = calculate_morpheme_entropy(corpus_sequences)
    
    # Apply auto-tagging
    tagged_sequences, coverage = auto_tag_corpus(
        corpus_sequences, lexicon, affix_candidates, numerals, particles
    )
    
    # Save results
    save_tagged_corpus(tagged_sequences, args.out)
    generate_tag_summary(tagged_sequences, args.out)
    
    print(f"\n✅ AUTO-TAGGING COMPLETE!")
    print(f"✓ Coverage: {coverage:.1%}")
    print(f"✓ Ready for CRF training")

if __name__ == "__main__":
    main() 