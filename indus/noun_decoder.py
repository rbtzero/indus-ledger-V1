#!/usr/bin/env python3
"""PROPER NOUN DECODER - Step 6.2"""
import pandas as pd
import json
import argparse

def decode_proper_nouns(ledger_file, posterior_file, out_tsv):
    print("🏷️ PROPER NOUN DECODER")
    
    # Load data
    ledger_df = pd.read_csv(ledger_file, sep='\t')
    with open(posterior_file, 'r') as f:
        posterior = json.load(f)
    
    print(f"   📋 Loaded {len(ledger_df)} ledger entries")
    print(f"   📝 Loaded {len(posterior)} phoneme mappings")
    
    decoded_nouns = []
    
    for _, row in ledger_df.iterrows():
        signs_str = str(row.get('signs', ''))
        site = row.get('site', 'unknown')
        
        if signs_str and signs_str != 'nan':
            signs = signs_str.split()
            
            # Decode sign sequence to phonemes
            phonemes = []
            for sign in signs:
                phoneme = posterior.get(sign, '?')
                phonemes.append(phoneme)
            
            phoneme_sequence = '-'.join(phonemes)
            
            # Generate possible glosses based on patterns
            gloss = generate_gloss(signs, phonemes, site)
            
            decoded_nouns.append({
                'sign_sequence': signs_str,
                'phoneme_sequence': phoneme_sequence,
                'site_context': site,
                'candidate_gloss': gloss,
                'confidence': calculate_confidence(signs, phonemes)
            })
    
    # Save decoded nouns
    nouns_df = pd.DataFrame(decoded_nouns)
    nouns_df = nouns_df.sort_values('confidence', ascending=False)
    nouns_df.to_csv(out_tsv, sep='\t', index=False)
    
    print(f"   🏷️ Decoded {len(nouns_df)} potential proper nouns")
    print(f"   📊 Average confidence: {nouns_df['confidence'].mean():.2f}")
    print(f"✅ Complete: {out_tsv}")

def generate_gloss(signs, phonemes, site):
    """Generate candidate gloss based on sign patterns"""
    if len(signs) == 1:
        sign = signs[0]
        if sign == '740':
            return 'cattle-lord'
        elif sign == '2':
            return 'field-master'
        elif sign == '235':
            return 'grain-trader'
        elif sign == '17':
            return 'merchant'
        else:
            return f'person-{sign}'
    
    elif len(signs) == 2:
        if '740' in signs and '2' in signs:
            return 'cattle-field-owner'
        elif '235' in signs and '17' in signs:
            return 'grain-merchant-guild'
        else:
            return f'{phonemes[0]}-{phonemes[1]}-name'
    
    else:
        return f'compound-name-{len(signs)}-signs'

def calculate_confidence(signs, phonemes):
    """Calculate confidence score for decoding"""
    base_confidence = 0.6
    
    # Higher confidence for known important signs
    important_signs = {'740', '2', '235', '17'}
    if any(sign in important_signs for sign in signs):
        base_confidence += 0.2
    
    # Higher confidence for shorter sequences
    if len(signs) <= 2:
        base_confidence += 0.1
    
    # Penalty for unknown phonemes
    unknown_count = sum(1 for p in phonemes if p == '?')
    base_confidence -= unknown_count * 0.1
    
    return min(0.95, max(0.1, base_confidence))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ledger', required=True)
    parser.add_argument('--posterior', required=True)
    parser.add_argument('--out_tsv', required=True)
    
    args = parser.parse_args()
    decode_proper_nouns(args.ledger, args.posterior, args.out_tsv)

if __name__ == "__main__":
    main() 