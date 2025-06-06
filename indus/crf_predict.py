#!/usr/bin/env python3
import argparse
import pandas as pd
import pickle
from collections import defaultdict, Counter

class SimpleCRF:
    """CRF model for prediction (simplified version)"""
    
    def __init__(self):
        self.feature_weights = defaultdict(float)
        self.label_vocab = set()
        self.feature_vocab = set()
        
    def extract_features(self, sequence, position):
        """Extract features for a token at given position"""
        features = []
        
        # Current token features
        token = sequence[position]
        features.append(f"token={token}")
        features.append(f"token_len={len(token)}")
        features.append(f"token_starts_with={token[0] if token else ''}")
        features.append(f"token_ends_with={token[-1] if token else ''}")
        
        # Positional features
        features.append(f"position={position}")
        features.append(f"relative_pos={position/len(sequence):.2f}")
        
        # Context features
        if position > 0:
            prev_token = sequence[position-1]
            features.append(f"prev_token={prev_token}")
            features.append(f"bigram={prev_token}_{token}")
        else:
            features.append("BOS")
            
        if position < len(sequence) - 1:
            next_token = sequence[position+1]
            features.append(f"next_token={next_token}")
            features.append(f"bigram={token}_{next_token}")
        else:
            features.append("EOS")
            
        # Window features
        if position > 1:
            features.append(f"prev2_token={sequence[position-2]}")
        if position < len(sequence) - 2:
            features.append(f"next2_token={sequence[position+2]}")
            
        # Morphological features
        if len(token) <= 2:
            features.append("short_token")
        if len(token) >= 4:
            features.append("long_token")
            
        # Pattern features
        if token in ['na', 'nan']:
            features.append("water_related")
        if token in ['pa', 'ma', 'ra']:
            features.append("person_related")
        if token in ['sa', 'cha']:
            features.append("sacred_related")
            
        return features
    
    def predict_sequence(self, sequence):
        """Predict labels for a sequence"""
        predictions = []
        
        for i in range(len(sequence)):
            features = self.extract_features(sequence, i)
            
            # Score each possible label
            label_scores = defaultdict(float)
            
            for label in self.label_vocab:
                for feature in features:
                    feature_key = f"{feature}_{label}"
                    label_scores[label] += self.feature_weights[feature_key]
            
            # Choose best label
            if label_scores:
                best_label = max(label_scores.items(), key=lambda x: x[1])[0]
            else:
                best_label = 'NOUN'  # Default fallback
                
            predictions.append(best_label)
        
        return predictions

def load_model(filepath):
    """Load trained CRF model"""
    print(f"📖 LOADING CRF MODEL:")
    
    with open(filepath, 'rb') as f:
        model_data = pickle.load(f)
    
    crf = SimpleCRF()
    crf.feature_weights = defaultdict(float, model_data['feature_weights'])
    crf.label_vocab = set(model_data['label_vocab'])
    crf.feature_vocab = set(model_data['feature_vocab'])
    
    print(f"✓ Loaded model with {len(crf.feature_weights)} feature weights")
    print(f"✓ Label vocabulary: {len(crf.label_vocab)} labels")
    print(f"✓ Labels: {', '.join(sorted(crf.label_vocab))}")
    
    return crf

def load_corpus(filepath):
    """Load corpus for prediction"""
    print(f"\n📚 LOADING CORPUS:")
    
    sequences = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                # Split into morphemes and filter out empty ones
                morphemes = [m for m in line.split() if m]
                if morphemes:
                    sequences.append(morphemes)
    
    print(f"✓ Loaded {len(sequences)} sequences")
    print(f"✓ Total tokens: {sum(len(seq) for seq in sequences)}")
    
    return sequences

def predict_corpus(crf, sequences):
    """Apply CRF to predict tags for entire corpus"""
    print(f"\n🔮 PREDICTING TAGS:")
    
    tagged_sequences = []
    tag_stats = Counter()
    
    for i, sequence in enumerate(sequences):
        if i % 500 == 0:
            print(f"  Processing sequence {i+1}/{len(sequences)}")
        
        predictions = crf.predict_sequence(sequence)
        
        tagged_sequence = {
            'sequence_id': f"seq_{i}",
            'morphemes': sequence,
            'tags': predictions,
            'original_sequence': ' '.join(sequence)
        }
        
        tagged_sequences.append(tagged_sequence)
        tag_stats.update(predictions)
    
    print(f"✓ Predicted tags for {len(tagged_sequences)} sequences")
    
    # Show tag distribution
    total_tokens = sum(tag_stats.values())
    print(f"\n📊 PREDICTED TAG DISTRIBUTION:")
    for tag, count in tag_stats.most_common():
        percentage = count / total_tokens * 100
        print(f"  {tag}: {count} ({percentage:.1f}%)")
    
    return tagged_sequences, tag_stats

def save_tagged_corpus(tagged_sequences, output_path):
    """Save CRF-tagged corpus to TSV file"""
    print(f"\n💾 SAVING TAGGED CORPUS:")
    
    rows = []
    
    for seq_data in tagged_sequences:
        sequence_id = seq_data['sequence_id']
        morphemes = seq_data['morphemes']
        tags = seq_data['tags']
        original_sequence = seq_data['original_sequence']
        
        for i, (morpheme, tag) in enumerate(zip(morphemes, tags)):
            rows.append({
                'sequence_id': sequence_id,
                'token_id': i,
                'morpheme': morpheme,
                'tag': tag,
                'sequence': original_sequence
            })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, sep='\t', index=False)
    
    print(f"✓ Saved {len(rows)} tagged tokens to {output_path}")
    print(f"✓ {len(tagged_sequences)} sequences total")

def analyze_predictions(tagged_sequences):
    """Analyze CRF prediction results"""
    print(f"\n🔍 PREDICTION ANALYSIS:")
    
    # Analyze sequence patterns
    sequence_patterns = defaultdict(int)
    tag_transitions = defaultdict(int)
    
    for seq_data in tagged_sequences:
        tags = seq_data['tags']
        
        # Count tag patterns
        pattern = ' '.join(tags)
        sequence_patterns[pattern] += 1
        
        # Count tag transitions
        for i in range(len(tags) - 1):
            transition = f"{tags[i]} → {tags[i+1]}"
            tag_transitions[transition] += 1
    
    # Show most common patterns
    print(f"📋 MOST COMMON TAG PATTERNS:")
    pattern_counter = Counter(sequence_patterns)
    for pattern, count in pattern_counter.most_common(10):
        print(f"  {pattern}: {count} sequences")
    
    print(f"\n🔄 MOST COMMON TAG TRANSITIONS:")
    transition_counter = Counter(tag_transitions)
    for transition, count in transition_counter.most_common(10):
        print(f"  {transition}: {count} times")
    
    # Show sample tagged sequences
    print(f"\n📜 SAMPLE TAGGED SEQUENCES:")
    for i, seq_data in enumerate(tagged_sequences[:10]):
        morphemes = seq_data['morphemes']
        tags = seq_data['tags']
        tagged_pairs = [f"{m}/{t}" for m, t in zip(morphemes, tags)]
        print(f"  {i+1}. {' '.join(tagged_pairs)}")

def generate_prediction_summary(tagged_sequences, tag_stats, output_path):
    """Generate detailed summary of CRF predictions"""
    
    summary_path = output_path.replace('.tsv', '_crf_summary.txt')
    
    with open(summary_path, 'w') as f:
        f.write("INDUS SCRIPT CRF PREDICTION SUMMARY\n")
        f.write("=" * 36 + "\n\n")
        
        # Overall statistics
        total_sequences = len(tagged_sequences)
        total_tokens = sum(tag_stats.values())
        
        f.write(f"Total sequences: {total_sequences}\n")
        f.write(f"Total tokens: {total_tokens}\n")
        f.write(f"Average sequence length: {total_tokens/total_sequences:.1f}\n\n")
        
        # Tag distribution
        f.write("CRF PREDICTED TAG DISTRIBUTION:\n")
        for tag, count in tag_stats.most_common():
            percentage = count / total_tokens * 100
            f.write(f"  {tag}: {count} ({percentage:.1f}%)\n")
        
        # Sample predictions
        f.write("\nSAMPLE CRF PREDICTIONS:\n")
        for i, seq in enumerate(tagged_sequences[:20]):
            morphemes = seq['morphemes']
            tags = seq['tags']
            tagged_pairs = [f"{m}/{t}" for m, t in zip(morphemes, tags)]
            f.write(f"  {i+1}. {' '.join(tagged_pairs)}\n")
    
    print(f"✓ Saved prediction summary to {summary_path}")

def main():
    parser = argparse.ArgumentParser(description="Apply trained CRF model to predict POS tags")
    parser.add_argument('--model', required=True, help="Trained CRF model file")
    parser.add_argument('--corpus', required=True, help="Input corpus file (phoneme sequences)")
    parser.add_argument('--out', required=True, help="Output tagged corpus TSV")
    
    args = parser.parse_args()
    
    print("🔮 CRF PREDICTOR")
    print("=" * 15)
    
    # Load trained model
    crf = load_model(args.model)
    
    # Load corpus
    sequences = load_corpus(args.corpus)
    
    # Apply predictions
    tagged_sequences, tag_stats = predict_corpus(crf, sequences)
    
    # Analyze results
    analyze_predictions(tagged_sequences)
    
    # Save results
    save_tagged_corpus(tagged_sequences, args.out)
    generate_prediction_summary(tagged_sequences, tag_stats, args.out)
    
    print(f"\n✅ CRF PREDICTION COMPLETE!")
    print(f"✓ Coverage: 100.0% (CRF-based)")
    print(f"✓ Ready for dependency parsing")

if __name__ == "__main__":
    main() 