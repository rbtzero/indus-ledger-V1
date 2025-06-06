#!/usr/bin/env python3
import pandas as pd
from collections import Counter, defaultdict
import json

print("📐 WORD ORDER ANALYSIS (SOV vs SVO vs OTHER)")
print("=" * 42)

# Load our data
original_sequences = []
with open('grammar/phon_seq.txt', 'r') as f:
    original_sequences = [line.strip() for line in f if line.strip()]

print(f"✓ Loaded {len(original_sequences)} sequences for analysis")

# Define semantic categories based on our translations
semantic_categories = {
    # Verbs/Actions
    'VERB': ['ta', 'da', 'ja', 'ya', 'ba'],  # give, do, come, go, be
    
    # Agents/Subjects (people, authority)
    'AGENT': ['ra', 'ka', 'pa', 'ma'],  # king, person, father, mother
    
    # Objects/Themes (things, places)
    'OBJECT': ['na', 'ku', 'ha', 'jha'],  # river, grain, land, place
    
    # Modifiers
    'MODIFIER': ['la', 'sa', 'cha'],  # small, sacred, sacred
    
    # Determiners/Particles
    'PARTICLE': ['nan']  # water (often used as determiner)
}

# Create reverse mapping
morpheme_to_category = {}
for category, morphemes in semantic_categories.items():
    for morpheme in morphemes:
        morpheme_to_category[morpheme] = category

print(f"✓ Categorized {len(morpheme_to_category)} morphemes into semantic roles")

# Analyze sequences for grammatical patterns
word_order_patterns = defaultdict(int)
svo_count = 0
sov_count = 0
vso_count = 0
ovs_count = 0
osv_count = 0
vos_count = 0

agent_verb_object_sequences = []

for seq in original_sequences:
    morphemes = seq.split()
    if len(morphemes) >= 3:
        # Categorize each morpheme
        categories = [morpheme_to_category.get(m, 'UNK') for m in morphemes]
        
        # Look for Agent-Verb-Object patterns in any order
        agent_pos = next((i for i, cat in enumerate(categories) if cat == 'AGENT'), -1)
        verb_pos = next((i for i, cat in enumerate(categories) if cat == 'VERB'), -1)
        object_pos = next((i for i, cat in enumerate(categories) if cat == 'OBJECT'), -1)
        
        if agent_pos != -1 and verb_pos != -1 and object_pos != -1:
            # We have all three components
            positions = [(agent_pos, 'S'), (verb_pos, 'V'), (object_pos, 'O')]
            positions.sort()
            order = ''.join([p[1] for p in positions])
            
            agent_verb_object_sequences.append({
                'sequence': seq,
                'morphemes': morphemes,
                'order': order,
                'agent': morphemes[agent_pos],
                'verb': morphemes[verb_pos],
                'object': morphemes[object_pos]
            })
            
            # Count word orders
            if order == 'SVO':
                svo_count += 1
            elif order == 'SOV':
                sov_count += 1
            elif order == 'VSO':
                vso_count += 1
            elif order == 'VOS':
                vos_count += 1
            elif order == 'OSV':
                osv_count += 1
            elif order == 'OVS':
                ovs_count += 1

# Analyze two-morpheme patterns for basic word order
two_morpheme_patterns = defaultdict(int)
for seq in original_sequences:
    morphemes = seq.split()
    if len(morphemes) == 2:
        cat1 = morpheme_to_category.get(morphemes[0], 'UNK')
        cat2 = morpheme_to_category.get(morphemes[1], 'UNK')
        if 'UNK' not in [cat1, cat2]:
            pattern = f"{cat1}-{cat2}"
            two_morpheme_patterns[pattern] += 1

print(f"\n📊 WORD ORDER ANALYSIS RESULTS:")
print(f"=" * 32)

total_avo_sequences = len(agent_verb_object_sequences)
if total_avo_sequences > 0:
    print(f"✓ Found {total_avo_sequences} sequences with Agent-Verb-Object")
    print(f"\n🎯 WORD ORDER FREQUENCIES:")
    print(f"  SOV (Subject-Object-Verb): {sov_count} ({sov_count/total_avo_sequences*100:.1f}%)")
    print(f"  SVO (Subject-Verb-Object): {svo_count} ({svo_count/total_avo_sequences*100:.1f}%)")
    print(f"  VSO (Verb-Subject-Object): {vso_count} ({vso_count/total_avo_sequences*100:.1f}%)")
    print(f"  VOS (Verb-Object-Subject): {vos_count} ({vos_count/total_avo_sequences*100:.1f}%)")
    print(f"  OSV (Object-Subject-Verb): {osv_count} ({osv_count/total_avo_sequences*100:.1f}%)")
    print(f"  OVS (Object-Verb-Subject): {ovs_count} ({ovs_count/total_avo_sequences*100:.1f}%)")
    
    # Determine dominant order
    orders = [
        ('SOV', sov_count), ('SVO', svo_count), ('VSO', vso_count),
        ('VOS', vos_count), ('OSV', osv_count), ('OVS', ovs_count)
    ]
    dominant_order = max(orders, key=lambda x: x[1])
    
    print(f"\n🏆 DOMINANT WORD ORDER: {dominant_order[0]} ({dominant_order[1]}/{total_avo_sequences})")
    
    # Chi-square test simulation
    expected = total_avo_sequences / 6  # Expected if random
    dominant_significance = dominant_order[1] / expected
    
    if dominant_significance >= 2.0:
        print(f"✅ SIGNIFICANT: {dominant_order[0]} is {dominant_significance:.1f}x more frequent than random")
    else:
        print(f"⚠️ INCONCLUSIVE: No clear word order preference detected")
else:
    print(f"❌ No complete Agent-Verb-Object sequences found")

print(f"\n📐 TWO-MORPHEME PATTERNS:")
print(f"✓ Most common semantic patterns:")
for i, (pattern, freq) in enumerate(sorted(two_morpheme_patterns.items(), key=lambda x: x[1], reverse=True)[:10]):
    print(f"  {i+1:2d}. {pattern}: {freq} times")

# Analyze modifier-noun order
modifier_noun_patterns = defaultdict(int)
noun_modifier_patterns = defaultdict(int)

for seq in original_sequences:
    morphemes = seq.split()
    if len(morphemes) == 2:
        cat1 = morpheme_to_category.get(morphemes[0], 'UNK')
        cat2 = morpheme_to_category.get(morphemes[1], 'UNK')
        
        if cat1 == 'MODIFIER' and cat2 in ['AGENT', 'OBJECT']:
            modifier_noun_patterns[f"{morphemes[0]}-{morphemes[1]}"] += 1
        elif cat2 == 'MODIFIER' and cat1 in ['AGENT', 'OBJECT']:
            noun_modifier_patterns[f"{morphemes[0]}-{morphemes[1]}"] += 1

modifier_first = sum(modifier_noun_patterns.values())
noun_first = sum(noun_modifier_patterns.values())

print(f"\n🏷️ MODIFIER-NOUN ORDER:")
if modifier_first + noun_first > 0:
    mod_first_pct = modifier_first / (modifier_first + noun_first) * 100
    noun_first_pct = noun_first / (modifier_first + noun_first) * 100
    print(f"  Modifier-Noun: {modifier_first} ({mod_first_pct:.1f}%)")
    print(f"  Noun-Modifier: {noun_first} ({noun_first_pct:.1f}%)")
    
    if mod_first_pct > 70:
        print(f"✅ PREFERENCE: Modifier-Noun order (like English)")
    elif noun_first_pct > 70:
        print(f"✅ PREFERENCE: Noun-Modifier order (like many SOV languages)")
    else:
        print(f"⚠️ MIXED: No clear modifier order preference")

# Save results
word_order_stats = {
    'total_sequences': total_avo_sequences,
    'word_orders': {
        'SOV': sov_count, 'SVO': svo_count, 'VSO': vso_count,
        'VOS': vos_count, 'OSV': osv_count, 'OVS': ovs_count
    },
    'dominant_order': dominant_order[0] if total_avo_sequences > 0 else 'UNKNOWN',
    'dominant_frequency': dominant_order[1] if total_avo_sequences > 0 else 0,
    'significance': dominant_significance if total_avo_sequences > 0 else 0,
    'modifier_order': {
        'modifier_first': modifier_first,
        'noun_first': noun_first
    },
    'two_morpheme_patterns': dict(two_morpheme_patterns),
    'sample_sequences': agent_verb_object_sequences[:5]
}

with open('grammar/wordorder_stats.json', 'w') as f:
    json.dump(word_order_stats, f, indent=2)

print(f"\n✅ WORD ORDER ANALYSIS COMPLETE:")
print(f"✓ Saved results to grammar/wordorder_stats.json")

if total_avo_sequences > 0:
    proto_munda_consistency = "✅ CONSISTENT" if dominant_order[0] == 'SOV' else "⚠️ DIFFERENT"
    print(f"✓ Proto-Munda expectation (SOV): {proto_munda_consistency}")
else:
    print(f"⚠️ Need more complex sequences for definitive word order analysis") 