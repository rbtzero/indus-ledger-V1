#!/usr/bin/env python3
"""
Final English Translation Generator
Converts inscriptions to fluent English using propagated glosses and weight optimization
"""

import pandas as pd
import json
import argparse
import sys
from collections import defaultdict

def load_data(corpus_file, gloss_file, weights_file):
    """Load all required data files"""
    
    # Load corpus
    corpus_df = pd.read_csv(corpus_file, sep='\t')
    
    # Load full glosses
    if gloss_file.endswith('.json'):
        with open(gloss_file, 'r') as f:
            gloss_data = json.load(f)
        if 'extended_glosses' in gloss_data:
            glosses = gloss_data['extended_glosses']
        else:
            glosses = gloss_data
    else:
        # CSV format
        gloss_df = pd.read_csv(gloss_file)
        glosses = {str(row['id']): row['english_word'] for _, row in gloss_df.iterrows()}
    
    # Load weights
    with open(weights_file, 'r') as f:
        weights_data = json.load(f)
    weights = weights_data.get('weights', weights_data)
    
    return corpus_df, glosses, weights

def enhance_translation_quality(signs, glosses, weights):
    """Enhance translation quality using weights and context"""
    
    enhanced_phrase = []
    
    for i, sign in enumerate(signs):
        sign_str = str(sign)
        base_word = glosses.get(sign_str, f'unknown_{sign}')
        weight = weights.get(sign_str, 1.0)
        
        # Weight-based enhancement
        if weight > 5.0:  # High authority
            if i == 0:  # Sentence start
                enhanced_word = f"Authority_{base_word}".replace('_', ' ')
            else:
                enhanced_word = f"Chief_{base_word}".replace('_', ' ')
        elif weight > 3.0:  # Medium importance
            if 'grain' in base_word or 'cattle' in base_word:
                enhanced_word = f"Premium_{base_word}".replace('_', ' ')
            else:
                enhanced_word = base_word.replace('_', ' ')
        elif weight < 1.0:  # Low weight (numerals/modifiers)
            if i == len(signs) - 1:  # End position
                enhanced_word = f"quantity_{base_word}".replace('_', ' ')
            else:
                enhanced_word = base_word.replace('_', ' ')
        else:
            enhanced_word = base_word.replace('_', ' ')
        
        # Position-based enhancement
        if i == 0 and 'authority' not in enhanced_word.lower():
            enhanced_word = enhanced_word.capitalize()
        
        enhanced_phrase.append(enhanced_word)
    
    return enhanced_phrase

def generate_fluent_translations(corpus_df, glosses, weights):
    """Generate fluent English translations for all inscriptions"""
    
    translations = []
    
    for _, row in corpus_df.iterrows():
        inscr_id = row['inscr_id']
        signs = [int(x) for x in str(row['sign_seq']).split()]
        
        # Get enhanced translation
        enhanced_words = enhance_translation_quality(signs, glosses, weights)
        
        # Create fluent phrase
        if len(enhanced_words) == 1:
            fluent = enhanced_words[0]
        elif len(enhanced_words) == 2:
            fluent = f"{enhanced_words[0]} {enhanced_words[1]}"
        else:
            # For longer sequences, add structure
            if any('authority' in w.lower() for w in enhanced_words[:2]):
                # Authority record format
                fluent = f"{enhanced_words[0]} records {' '.join(enhanced_words[1:])}"
            elif any('grain' in w.lower() or 'cattle' in w.lower() for w in enhanced_words):
                # Commodity record format  
                commodities = [w for w in enhanced_words if any(c in w.lower() for c in ['grain', 'cattle', 'fish', 'copper'])]
                others = [w for w in enhanced_words if w not in commodities]
                if commodities and others:
                    fluent = f"{' '.join(others)} of {' '.join(commodities)}"
                else:
                    fluent = ' '.join(enhanced_words)
            else:
                # Standard format
                fluent = ' '.join(enhanced_words)
        
        # Clean up the translation
        fluent = fluent.replace('_', ' ').replace('  ', ' ').strip()
        
        translations.append({
            'inscr_id': inscr_id,
            'english_phrase': fluent,
            'signs': signs,
            'weight_total': sum(weights.get(str(s), 1.0) for s in signs)
        })
    
    return translations

def calculate_final_coverage(translations, glosses):
    """Calculate final coverage statistics"""
    
    total_tokens = sum(len(t['signs']) for t in translations)
    covered_tokens = sum(1 for t in translations for s in t['signs'] 
                        if str(s) in glosses and not glosses[str(s)].startswith('unknown_'))
    
    coverage = covered_tokens / total_tokens if total_tokens > 0 else 0
    
    # Count sign_XXX remaining
    sign_xxx_count = sum(1 for t in translations if 'unknown_' in t['english_phrase'])
    
    return {
        'coverage': coverage,
        'total_tokens': total_tokens,
        'covered_tokens': covered_tokens,
        'unknown_remaining': sign_xxx_count,
        'total_translations': len(translations)
    }

def main():
    parser = argparse.ArgumentParser(description='Generate Final English Translations')
    parser.add_argument('--corpus', required=True, help='Corpus TSV file')
    parser.add_argument('--gloss', required=True, help='Full glosses file (JSON or CSV)')
    parser.add_argument('--weights', required=True, help='Weights JSON file')
    parser.add_argument('--output', help='Output file (default: stdout)')
    
    args = parser.parse_args()
    
    # Load data
    corpus_df, glosses, weights = load_data(args.corpus, args.gloss, args.weights)
    
    print(f"📖 Loaded {len(corpus_df)} inscriptions", file=sys.stderr)
    print(f"🌱 Using {len(glosses)} glosses", file=sys.stderr)
    print(f"⚖️  Using weights for {len(weights)} signs", file=sys.stderr)
    
    # Generate translations
    translations = generate_fluent_translations(corpus_df, glosses, weights)
    
    # Calculate coverage
    stats = calculate_final_coverage(translations, glosses)
    
    print(f"✅ Generated {stats['total_translations']} translations", file=sys.stderr)
    print(f"📊 Final coverage: {stats['coverage']:.1%}", file=sys.stderr)
    print(f"🔍 Unknown tokens remaining: {stats['unknown_remaining']}", file=sys.stderr)
    
    # Output translations
    output_file = sys.stdout if not args.output else open(args.output, 'w')
    
    output_file.write("inscr_id\tenglish_phrase\n")
    for t in translations:
        output_file.write(f"{t['inscr_id']}\t{t['english_phrase']}\n")
    
    if args.output:
        output_file.close()
        print(f"💾 Saved to {args.output}", file=sys.stderr)

if __name__ == '__main__':
    main() 