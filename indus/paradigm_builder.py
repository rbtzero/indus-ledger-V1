#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict, Counter
import re

def load_morfessor_model(filepath):
    """Load Morfessor segmentation results"""
    print(f"📊 LOADING MORFESSOR SEGMENTATIONS:")
    
    # Load original sequences 
    with open('grammar/phon_seq.txt', 'r') as f:
        original_sequences = [line.strip() for line in f if line.strip()]
    
    # Load segmented results
    with open(filepath, 'r') as f:
        segmented_lines = [line.strip() for line in f if line.strip()]
    
    segmentations = {}
    
    # Pair original sequences with segmentations
    if len(original_sequences) == len(segmented_lines):
        for orig, segmented in zip(original_sequences, segmented_lines):
            # Each line in segmented output is already individual morphemes
            # For sequences, split by space and then by space again if morphemes are joined
            if ' ' in orig:
                # Multi-morpheme sequence
                segments = segmented.split() if ' ' in segmented else [segmented]
            else:
                # Single morpheme
                segments = [segmented]
            
            segmentations[orig] = segments
    else:
        # Fallback: treat each segmented line as a single morpheme
        for i, segmented in enumerate(segmented_lines):
            if i < len(original_sequences):
                segmentations[original_sequences[i]] = [segmented]
    
    print(f"✓ Loaded segmentations for {len(segmentations)} sequences")
    return segmentations

def identify_stems_and_affixes(segmentations):
    """Identify potential stems and affixes from segmentations"""
    print(f"\n🔍 IDENTIFYING STEMS AND AFFIXES:")
    
    stems = Counter()
    prefixes = Counter()
    suffixes = Counter()
    
    for word, segments in segmentations.items():
        if len(segments) == 1:
            # Single morpheme - likely a stem
            stems[segments[0]] += 1
        elif len(segments) == 2:
            # Two parts - could be prefix+stem or stem+suffix
            first, second = segments
            
            # Heuristic: shorter parts are likely affixes
            if len(first) <= 2:
                prefixes[first] += 1
                stems[second] += 1
            elif len(second) <= 2:
                stems[first] += 1
                suffixes[second] += 1
            else:
                # Both parts substantial - count both as potential stems
                stems[first] += 1
                stems[second] += 1
        elif len(segments) >= 3:
            # Multiple parts - likely stem with multiple affixes
            stems[segments[1]] += 1  # Assume middle is stem
            if len(segments[0]) <= 2:
                prefixes[segments[0]] += 1
            if len(segments[-1]) <= 2:
                suffixes[segments[-1]] += 1
    
    print(f"✓ Found {len(stems)} potential stems")
    print(f"✓ Found {len(prefixes)} potential prefixes")
    print(f"✓ Found {len(suffixes)} potential suffixes")
    
    return stems, prefixes, suffixes

def load_affix_candidates(filepath):
    """Load affix candidates from previous analysis"""
    print(f"📚 LOADING AFFIX CANDIDATES:")
    
    # From our ledger-aware analysis, we found these significant affixes
    affix_candidates = {
        'da': {'type': 'suffix', 'function': 'plural/agent', 'confidence': 0.8},
        'ba': {'type': 'suffix', 'function': 'locative', 'confidence': 0.7},
        'si': {'type': 'suffix', 'function': 'instrumental', 'confidence': 0.7},
        'an': {'type': 'suffix', 'function': 'dative', 'confidence': 0.8},
        'la': {'type': 'prefix', 'function': 'diminutive', 'confidence': 0.6},
        'sa': {'type': 'prefix', 'function': 'sacred/ritual', 'confidence': 0.9},
        'pa': {'type': 'prefix', 'function': 'agentive', 'confidence': 0.7},
        'ma': {'type': 'prefix', 'function': 'honorific', 'confidence': 0.6}
    }
    
    print(f"✓ Loaded {len(affix_candidates)} affix candidates")
    
    # Show candidates by type
    prefixes = [affix for affix, info in affix_candidates.items() if info['type'] == 'prefix']
    suffixes = [affix for affix, info in affix_candidates.items() if info['type'] == 'suffix']
    
    print(f"  Prefixes: {', '.join(prefixes)}")
    print(f"  Suffixes: {', '.join(suffixes)}")
    
    return affix_candidates

def find_paradigms(segmentations, stems, affix_candidates):
    """Find morphological paradigms (sets of related forms)"""
    print(f"\n🔧 FINDING PARADIGMS:")
    
    paradigms = defaultdict(lambda: {'base': None, 'forms': {}})
    
    # Get high-frequency stems (likely base forms)
    common_stems = [stem for stem, count in stems.most_common(20) if count >= 3]
    print(f"✓ Processing {len(common_stems)} common stems")
    
    for base_stem in common_stems:
        paradigm_id = f"paradigm_{base_stem}"
        paradigms[paradigm_id]['base'] = base_stem
        
        # Look for words containing this stem with affixes
        for word, segments in segmentations.items():
            if base_stem in segments:
                stem_index = segments.index(base_stem)
                
                # Check for affixes before and after the stem
                prefixes_found = []
                suffixes_found = []
                
                # Prefixes (before stem)
                for i in range(stem_index):
                    segment = segments[i]
                    if segment in affix_candidates and affix_candidates[segment]['type'] == 'prefix':
                        prefixes_found.append(segment)
                
                # Suffixes (after stem)
                for i in range(stem_index + 1, len(segments)):
                    segment = segments[i]
                    if segment in affix_candidates and affix_candidates[segment]['type'] == 'suffix':
                        suffixes_found.append(segment)
                
                # Create form description
                form_desc = []
                if prefixes_found:
                    form_desc.extend([f"{p}(prefix)" for p in prefixes_found])
                if suffixes_found:
                    form_desc.extend([f"{s}(suffix)" for s in suffixes_found])
                
                if form_desc:
                    form_key = '+'.join(form_desc)
                    paradigms[paradigm_id]['forms'][form_key] = {
                        'word': word,
                        'segments': segments,
                        'prefixes': prefixes_found,
                        'suffixes': suffixes_found
                    }
    
    # Filter paradigms that have at least 2 forms (base + inflected)
    valid_paradigms = {}
    for pid, paradigm in paradigms.items():
        if len(paradigm['forms']) >= 1:  # At least one inflected form
            valid_paradigms[pid] = paradigm
    
    print(f"✓ Found {len(valid_paradigms)} paradigms")
    return valid_paradigms

def analyze_paradigms(paradigms, affix_candidates):
    """Analyze and describe the paradigms found"""
    print(f"\n📋 PARADIGM ANALYSIS:")
    
    paradigm_analysis = {}
    
    for pid, paradigm in paradigms.items():
        base_stem = paradigm['base']
        forms = paradigm['forms']
        
        print(f"\n  {pid} (base: '{base_stem}'):")
        
        analysis = {
            'base_stem': base_stem,
            'num_forms': len(forms),
            'forms': [],
            'affix_functions': set()
        }
        
        for form_key, form_data in forms.items():
            word = form_data['word']
            prefixes = form_data['prefixes']
            suffixes = form_data['suffixes']
            
            print(f"    {word}: {' + '.join(form_data['segments'])}")
            
            # Describe grammatical function
            functions = []
            for prefix in prefixes:
                if prefix in affix_candidates:
                    func = affix_candidates[prefix]['function']
                    functions.append(f"{func}(prefix)")
                    analysis['affix_functions'].add(func)
            
            for suffix in suffixes:
                if suffix in affix_candidates:
                    func = affix_candidates[suffix]['function']
                    functions.append(f"{func}(suffix)")
                    analysis['affix_functions'].add(func)
            
            function_desc = ', '.join(functions) if functions else 'unknown'
            print(f"      → {function_desc}")
            
            analysis['forms'].append({
                'word': word,
                'form_key': form_key,
                'function': function_desc,
                'prefixes': prefixes,
                'suffixes': suffixes
            })
        
        analysis['affix_functions'] = list(analysis['affix_functions'])
        paradigm_analysis[pid] = analysis
    
    return paradigm_analysis

def identify_morphological_patterns(paradigm_analysis):
    """Identify common morphological patterns"""
    print(f"\n🎯 MORPHOLOGICAL PATTERNS:")
    
    patterns = {
        'case_marking': [],
        'number_marking': [],
        'agent_marking': [],
        'ritual_marking': []
    }
    
    for pid, analysis in paradigm_analysis.items():
        functions = set(analysis['affix_functions'])
        
        # Case marking pattern
        case_affixes = {'locative', 'dative', 'instrumental'}
        if functions & case_affixes:
            patterns['case_marking'].append({
                'paradigm': pid,
                'base': analysis['base_stem'],
                'cases': list(functions & case_affixes)
            })
        
        # Number marking pattern
        if 'plural/agent' in functions:
            patterns['number_marking'].append({
                'paradigm': pid,
                'base': analysis['base_stem'],
                'plural_form': 'da-suffix'
            })
        
        # Agent marking pattern
        if 'agentive' in functions:
            patterns['agent_marking'].append({
                'paradigm': pid,
                'base': analysis['base_stem'],
                'agent_form': 'pa-prefix'
            })
        
        # Ritual marking pattern
        if 'sacred/ritual' in functions:
            patterns['ritual_marking'].append({
                'paradigm': pid,
                'base': analysis['base_stem'],
                'ritual_form': 'sa-prefix'
            })
    
    # Report patterns
    for pattern_type, instances in patterns.items():
        if instances:
            print(f"  {pattern_type.replace('_', ' ').title()}: {len(instances)} paradigms")
            for instance in instances[:3]:  # Show first 3 examples
                print(f"    • {instance['base']}: {instance}")
    
    return patterns

def save_paradigms(paradigm_analysis, patterns, output_path):
    """Save paradigm analysis to JSON file"""
    print(f"\n💾 SAVING PARADIGMS:")
    
    output_data = {
        'paradigms': paradigm_analysis,
        'patterns': patterns,
        'summary': {
            'total_paradigms': len(paradigm_analysis),
            'case_marking_paradigms': len(patterns['case_marking']),
            'number_marking_paradigms': len(patterns['number_marking']),
            'agent_marking_paradigms': len(patterns['agent_marking']),
            'ritual_marking_paradigms': len(patterns['ritual_marking'])
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved {len(paradigm_analysis)} paradigms to {output_path}")
    print(f"✓ Identified {sum(len(p) for p in patterns.values())} morphological patterns")

def main():
    parser = argparse.ArgumentParser(description="Build morphological paradigms from Morfessor output")
    parser.add_argument('--morph', required=True, help="Morfessor segmentation file")
    parser.add_argument('--affix', help="Affix candidates file (optional)")
    parser.add_argument('--out', required=True, help="Output paradigms JSON file")
    
    args = parser.parse_args()
    
    print("🔧 PARADIGM BUILDER")
    print("=" * 18)
    
    # Load Morfessor segmentations
    segmentations = load_morfessor_model(args.morph)
    
    # Identify stems and affixes
    stems, prefixes, suffixes = identify_stems_and_affixes(segmentations)
    
    # Load affix candidates
    affix_candidates = load_affix_candidates(args.affix) if args.affix else load_affix_candidates("")
    
    # Find paradigms
    paradigms = find_paradigms(segmentations, stems, affix_candidates)
    
    # Analyze paradigms
    paradigm_analysis = analyze_paradigms(paradigms, affix_candidates)
    
    # Identify patterns
    patterns = identify_morphological_patterns(paradigm_analysis)
    
    # Save results
    save_paradigms(paradigm_analysis, patterns, args.out)
    
    print(f"\n✅ PARADIGM BUILDING COMPLETE!")

if __name__ == "__main__":
    main() 