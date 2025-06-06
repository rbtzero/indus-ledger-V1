#!/usr/bin/env python3
from collections import Counter

print("🔤 EXTRACTING AFFIX CANDIDATES")
print("=" * 31)

# Read morfessor output and extract affixes
aff = Counter()
try:
    for line in open('grammar/morph.txt'):
        parts = line.strip().split()
        for m in parts:
            if len(m) > 2 and m.startswith('+'):
                aff[m[1:]] += 1
except FileNotFoundError:
    print("❌ No morph.txt found - checking for alternative morpheme patterns")
    # Alternative: analyze phoneme sequences directly for recurring endings
    aff = Counter()
    for line in open('grammar/phon_seq.txt'):
        words = line.strip().split()
        for word in words:
            if len(word) > 2:
                # Check for potential suffixes (last 2-3 characters)
                if len(word) >= 3:
                    aff[word[-2:]] += 1
                    aff[word[-3:]] += 1

# Filter for significant affixes
threshold = max(5, len(aff) // 20)  # Adaptive threshold
out = [a for a, c in aff.items() if c >= threshold]

print(f"✓ Found {len(aff)} total morpheme patterns")
print(f"✓ Found {len(out)} significant affix candidates (≥{threshold} occurrences)")

# Save affix candidates
with open('grammar/affix_candidates.txt', 'w') as f:
    f.write('\n'.join(out))

print(f"\n🏷️ TOP AFFIX CANDIDATES:")
for i, (a, count) in enumerate(aff.most_common(15)):
    print(f"  {i+1:2d}. +{a} ({count} occurrences)")

print(f"\n✅ Saved {len(out)} affix candidates to grammar/affix_candidates.txt") 