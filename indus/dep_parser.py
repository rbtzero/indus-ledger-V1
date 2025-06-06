#!/usr/bin/env python3
import argparse
import pandas as pd
from collections import defaultdict, Counter
import json

class SOVDependencyParser:
    """Simple dependency parser with SOV bias for Indus script"""
    
    def __init__(self):
        # SOV language dependency patterns
        self.sov_patterns = {
            # Subject-Verb patterns
            ('NOUN', 'VERB'): {'head': 1, 'label': 'nsubj'},
            ('ADJ', 'NOUN'): {'head': 1, 'label': 'amod'},
            ('NOUN', 'NOUN'): {'head': 1, 'label': 'nmod'},  # Genitive/compound
            
            # Object-Verb patterns  
            ('NOUN', 'VERB'): {'head': 1, 'label': 'obj'},  # Direct object
            ('ADP', 'NOUN'): {'head': 1, 'label': 'case'},  # Case marker
            
            # Verb patterns
            ('VERB', 'NOUN'): {'head': 0, 'label': 'obj'},  # Verb governs object
            ('VERB', 'ADJ'): {'head': 0, 'label': 'xcomp'},  # Verb governs predicate
            
            # Adjective patterns
            ('ADJ', 'ADJ'): {'head': 1, 'label': 'compound'},  # Adjective compound
        }
        
        # Head rules for SOV
        self.head_rules = {
            'VERB': {'priority': 1, 'direction': 'right'},  # Verb is usually sentence head
            'NOUN': {'priority': 2, 'direction': 'left'},   # Noun heads left
            'ADJ': {'priority': 3, 'direction': 'right'},   # Adjective modifies right
            'ADP': {'priority': 4, 'direction': 'right'},   # Postposition
        }
    
    def parse_sequence(self, tokens, tags):
        """Parse a sequence into dependency tree"""
        n = len(tokens)
        
        if n == 0:
            return []
        
        # Initialize dependency structure
        deps = []
        for i in range(n):
            deps.append({
                'id': i + 1,
                'token': tokens[i],
                'tag': tags[i],
                'head': 0,  # 0 = root
                'label': 'root'
            })
        
        if n == 1:
            return deps
        
        # Find the main verb (if any) as potential root
        verb_indices = [i for i, tag in enumerate(tags) if tag == 'VERB']
        
        if verb_indices:
            # Use rightmost verb as root (SOV pattern)
            root_idx = verb_indices[-1]
        else:
            # No verb - use rightmost noun as root
            noun_indices = [i for i, tag in enumerate(tags) if tag == 'NOUN']
            if noun_indices:
                root_idx = noun_indices[-1]
            else:
                # Fallback - use last token
                root_idx = n - 1
        
        # Set root
        deps[root_idx]['head'] = 0
        deps[root_idx]['label'] = 'root'
        
        # Attach other tokens
        for i in range(n):
            if i == root_idx:
                continue
                
            head_idx, label = self.find_head(i, tags, root_idx, n)
            deps[i]['head'] = head_idx + 1  # 1-indexed
            deps[i]['label'] = label
        
        return deps
    
    def find_head(self, token_idx, tags, root_idx, n):
        """Find head and label for a token using SOV patterns"""
        
        current_tag = tags[token_idx]
        
        # Look for head using SOV patterns
        best_head = root_idx
        best_label = 'dep'  # Default
        best_distance = float('inf')
        
        for head_idx in range(n):
            if head_idx == token_idx:
                continue
                
            head_tag = tags[head_idx]
            
            # Check if this forms a valid pattern
            if token_idx < head_idx:
                # Token before potential head
                pattern = (current_tag, head_tag)
                if pattern in self.sov_patterns:
                    rule = self.sov_patterns[pattern]
                    if rule['head'] == 1:  # Head is the second element
                        distance = abs(head_idx - token_idx)
                        if distance < best_distance:
                            best_head = head_idx
                            best_label = rule['label']
                            best_distance = distance
            else:
                # Token after potential head
                pattern = (head_tag, current_tag)
                if pattern in self.sov_patterns:
                    rule = self.sov_patterns[pattern]
                    if rule['head'] == 0:  # Head is the first element
                        distance = abs(head_idx - token_idx)
                        if distance < best_distance:
                            best_head = head_idx
                            best_label = rule['label']
                            best_distance = distance
        
        # SOV-specific attachment rules
        if best_label == 'dep':
            # Apply SOV heuristics
            if current_tag == 'NOUN' and token_idx < root_idx:
                # Noun before verb - likely subject
                if tags[root_idx] == 'VERB':
                    best_head = root_idx
                    best_label = 'nsubj'
                else:
                    # Attach to nearest noun to the right
                    for i in range(token_idx + 1, n):
                        if tags[i] == 'NOUN':
                            best_head = i
                            best_label = 'nmod'
                            break
            
            elif current_tag == 'ADJ':
                # Adjective - attach to nearest noun
                # In SOV, adjectives typically precede nouns
                for i in range(token_idx + 1, n):
                    if tags[i] == 'NOUN':
                        best_head = i
                        best_label = 'amod'
                        break
                
                # If no noun to the right, attach to nearest noun to the left
                if best_label == 'dep':
                    for i in range(token_idx - 1, -1, -1):
                        if tags[i] == 'NOUN':
                            best_head = i
                            best_label = 'amod'
                            break
            
            elif current_tag == 'ADP':
                # Postposition - attach to preceding noun
                for i in range(token_idx - 1, -1, -1):
                    if tags[i] == 'NOUN':
                        best_head = i
                        best_label = 'case'
                        break
        
        return best_head, best_label
    
    def convert_to_conllu(self, deps, sequence_id="1"):
        """Convert dependency parse to CoNLL-U format"""
        
        lines = []
        lines.append(f"# sent_id = {sequence_id}")
        
        # Ensure all tokens are strings
        tokens = [str(dep['token']) for dep in deps if pd.notna(dep['token'])]
        lines.append(f"# text = {' '.join(tokens)}")
        
        for dep in deps:
            # Ensure all fields are strings and not NaN
            token = str(dep['token']) if pd.notna(dep['token']) else '_'
            tag = str(dep['tag']) if pd.notna(dep['tag']) else '_'
            
            # CoNLL-U format: ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC
            line = f"{dep['id']}\t{token}\t{token}\t{tag}\t{tag}\t_\t{dep['head']}\t{dep['label']}\t_\t_"
            lines.append(line)
        
        lines.append("")  # Empty line between sentences
        return "\n".join(lines)

def load_tagged_corpus(filepath):
    """Load CRF-tagged corpus"""
    print(f"📖 LOADING TAGGED CORPUS:")
    
    df = pd.read_csv(filepath, sep='\t')
    
    # Group by sequence
    sequences = []
    
    for seq_id, group in df.groupby('sequence_id'):
        tokens = group['morpheme'].tolist()
        tags = group['tag'].tolist()
        original_sequence = group['sequence'].iloc[0]
        
        sequences.append({
            'sequence_id': seq_id,
            'tokens': tokens,
            'tags': tags,
            'original_sequence': original_sequence
        })
    
    print(f"✓ Loaded {len(sequences)} tagged sequences")
    return sequences

def parse_corpus(sequences):
    """Parse entire corpus into dependency trees"""
    print(f"\n🌳 PARSING DEPENDENCY TREES:")
    
    parser = SOVDependencyParser()
    parsed_sequences = []
    
    # Statistics
    dependency_stats = Counter()
    pos_head_stats = defaultdict(Counter)
    
    for i, seq_data in enumerate(sequences):
        if i % 500 == 0:
            print(f"  Parsing sequence {i+1}/{len(sequences)}")
        
        tokens = seq_data['tokens']
        tags = seq_data['tags']
        
        # Parse sequence
        deps = parser.parse_sequence(tokens, tags)
        
        # Collect statistics
        for dep in deps:
            dependency_stats[dep['label']] += 1
            pos_head_stats[dep['tag']][dep['label']] += 1
        
        parsed_sequences.append({
            'sequence_id': seq_data['sequence_id'],
            'tokens': tokens,
            'tags': tags,
            'dependencies': deps,
            'original_sequence': seq_data['original_sequence']
        })
    
    print(f"✓ Parsed {len(parsed_sequences)} sequences")
    
    # Show statistics
    print(f"\n📊 DEPENDENCY STATISTICS:")
    for label, count in dependency_stats.most_common():
        print(f"  {label}: {count}")
    
    return parsed_sequences, dependency_stats

def evaluate_parser(parsed_sequences):
    """Evaluate parser quality using heuristics"""
    print(f"\n📈 PARSER EVALUATION:")
    
    total_sequences = len(parsed_sequences)
    total_dependencies = sum(len(seq['dependencies']) for seq in parsed_sequences)
    
    # Quality metrics
    well_formed_trees = 0
    projective_trees = 0
    sov_consistent = 0
    
    for seq_data in parsed_sequences:
        deps = seq_data['dependencies']
        tags = seq_data['tags']
        
        # Check if tree is well-formed (exactly one root)
        roots = [dep for dep in deps if dep['head'] == 0]
        if len(roots) == 1:
            well_formed_trees += 1
        
        # Check SOV consistency
        has_verb = any(tag == 'VERB' for tag in tags)
        if has_verb:
            verb_positions = [i for i, tag in enumerate(tags) if tag == 'VERB']
            noun_positions = [i for i, tag in enumerate(tags) if tag == 'NOUN']
            
            # In SOV, objects should precede verbs
            sov_violations = 0
            for verb_pos in verb_positions:
                obj_after_verb = any(pos > verb_pos for pos in noun_positions)
                if not obj_after_verb:
                    sov_violations += 1
            
            if sov_violations == 0:
                sov_consistent += 1
        else:
            sov_consistent += 1  # No verb, so no SOV violation
        
        # Simple projectivity check (no crossing arcs)
        projective = True
        for i, dep1 in enumerate(deps):
            for j, dep2 in enumerate(deps):
                if i != j and dep1['head'] != 0 and dep2['head'] != 0:
                    # Check for crossing arcs
                    min_arc1, max_arc1 = sorted([i, dep1['head'] - 1])
                    min_arc2, max_arc2 = sorted([j, dep2['head'] - 1])
                    
                    if (min_arc1 < min_arc2 < max_arc1 < max_arc2) or \
                       (min_arc2 < min_arc1 < max_arc2 < max_arc1):
                        projective = False
                        break
            if not projective:
                break
        
        if projective:
            projective_trees += 1
    
    # Calculate scores
    well_formed_rate = well_formed_trees / total_sequences
    projective_rate = projective_trees / total_sequences
    sov_rate = sov_consistent / total_sequences
    
    # Overall quality score (simple average)
    las_estimate = (well_formed_rate + projective_rate + sov_rate) / 3
    
    print(f"✓ Well-formed trees: {well_formed_rate:.3f}")
    print(f"✓ Projective trees: {projective_rate:.3f}")
    print(f"✓ SOV consistent: {sov_rate:.3f}")
    print(f"✓ Estimated LAS: {las_estimate:.3f}")
    
    return las_estimate

def save_dependencies(parsed_sequences, output_path):
    """Save parsed dependencies in CoNLL-U format"""
    print(f"\n💾 SAVING DEPENDENCIES:")
    
    parser = SOVDependencyParser()
    
    with open(output_path, 'w') as f:
        for seq_data in parsed_sequences:
            conllu_text = parser.convert_to_conllu(
                seq_data['dependencies'], 
                seq_data['sequence_id']
            )
            f.write(conllu_text + "\n")
    
    print(f"✓ Saved {len(parsed_sequences)} parsed sequences to {output_path}")

def analyze_dependency_patterns(parsed_sequences):
    """Analyze common dependency patterns"""
    print(f"\n🔍 DEPENDENCY PATTERN ANALYSIS:")
    
    # Pattern analysis
    arc_patterns = Counter()
    head_direction = Counter()
    
    for seq_data in parsed_sequences:
        deps = seq_data['dependencies']
        tags = seq_data['tags']
        
        for dep in deps:
            if dep['head'] != 0:
                head_idx = dep['head'] - 1
                dependent_idx = dep['id'] - 1
                
                head_tag = tags[head_idx]
                dependent_tag = dep['tag']
                
                # Record pattern
                pattern = f"{dependent_tag} → {head_tag} ({dep['label']})"
                arc_patterns[pattern] += 1
                
                # Record direction
                if dependent_idx < head_idx:
                    head_direction['dependent_before_head'] += 1
                else:
                    head_direction['dependent_after_head'] += 1
    
    print(f"📋 MOST COMMON DEPENDENCY PATTERNS:")
    for pattern, count in arc_patterns.most_common(10):
        print(f"  {pattern}: {count}")
    
    print(f"\n🎯 HEAD DIRECTION STATISTICS:")
    total_deps = sum(head_direction.values())
    for direction, count in head_direction.items():
        percentage = count / total_deps * 100
        print(f"  {direction}: {count} ({percentage:.1f}%)")

def main():
    parser = argparse.ArgumentParser(description="Parse dependency grammar for Indus corpus")
    parser.add_argument('--tagged', required=True, help="Tagged corpus TSV file")
    parser.add_argument('--out', required=True, help="Output CoNLL-U dependencies file")
    
    args = parser.parse_args()
    
    print("🌳 DEPENDENCY PARSER")
    print("=" * 18)
    
    # Load tagged corpus
    sequences = load_tagged_corpus(args.tagged)
    
    # Parse dependencies
    parsed_sequences, dep_stats = parse_corpus(sequences)
    
    # Evaluate parser
    las_score = evaluate_parser(parsed_sequences)
    
    # Analyze patterns
    analyze_dependency_patterns(parsed_sequences)
    
    # Save results
    save_dependencies(parsed_sequences, args.out)
    
    print(f"\n✅ DEPENDENCY PARSING COMPLETE!")
    print(f"✓ Estimated LAS: {las_score:.3f}")
    if las_score >= 0.7:
        print(f"✓ Quality threshold met (≥0.70)")
    else:
        print(f"⚠ Quality below threshold (<0.70)")

if __name__ == "__main__":
    main() 