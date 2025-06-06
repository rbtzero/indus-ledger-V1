#!/usr/bin/env python3
import argparse
import pandas as pd
import pickle
from collections import defaultdict, Counter
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import numpy as np

# Simple CRF implementation using feature templates
class SimpleCRF:
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
    
    def extract_sequence_features(self, sequence, labels=None):
        """Extract features for entire sequence"""
        sequence_features = []
        
        for i in range(len(sequence)):
            token_features = self.extract_features(sequence, i)
            
            # Add label transition features if training
            if labels:
                current_label = labels[i]
                if i > 0:
                    prev_label = labels[i-1]
                    token_features.append(f"transition={prev_label}_{current_label}")
                else:
                    token_features.append(f"start_label={current_label}")
                    
                if i == len(sequence) - 1:
                    token_features.append(f"end_label={current_label}")
            
            sequence_features.append(token_features)
            
        return sequence_features
    
    def train(self, sequences, label_sequences, epochs=10, learning_rate=0.01):
        """Train CRF using perceptron-like algorithm"""
        print(f"🧠 TRAINING CRF:")
        print(f"✓ Sequences: {len(sequences)}")
        print(f"✓ Epochs: {epochs}")
        print(f"✓ Learning rate: {learning_rate}")
        
        # Build vocabularies
        for labels in label_sequences:
            self.label_vocab.update(labels)
            
        for seq, labels in zip(sequences, label_sequences):
            features = self.extract_sequence_features(seq, labels)
            for token_features in features:
                self.feature_vocab.update(token_features)
        
        print(f"✓ Label vocabulary: {len(self.label_vocab)} labels")
        print(f"✓ Feature vocabulary: {len(self.feature_vocab)} features")
        
        # Training loop
        for epoch in range(epochs):
            total_loss = 0
            correct_predictions = 0
            total_predictions = 0
            
            for seq, true_labels in zip(sequences, label_sequences):
                # Predict with current weights
                predicted_labels = self.predict_sequence(seq)
                
                # Update weights for incorrect predictions
                for i, (true_label, pred_label) in enumerate(zip(true_labels, predicted_labels)):
                    features = self.extract_features(seq, i)
                    
                    if true_label != pred_label:
                        # Increase weight for true label features
                        for feature in features:
                            self.feature_weights[f"{feature}_{true_label}"] += learning_rate
                            
                        # Decrease weight for predicted label features
                        for feature in features:
                            self.feature_weights[f"{feature}_{pred_label}"] -= learning_rate
                        
                        total_loss += 1
                    else:
                        correct_predictions += 1
                    
                    total_predictions += 1
            
            accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
            print(f"  Epoch {epoch+1}: accuracy={accuracy:.3f}, loss={total_loss}")
        
        print(f"✓ Training completed!")
        
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

def load_tagged_data(filepath):
    """Load tagged corpus data"""
    print(f"📖 LOADING TAGGED DATA:")
    
    df = pd.read_csv(filepath, sep='\t')
    
    # Drop rows with NaN values
    df = df.dropna(subset=['morpheme', 'tag'])
    
    # Group by sequence
    sequences = []
    label_sequences = []
    
    for seq_id, group in df.groupby('sequence_id'):
        sequence = [str(token) for token in group['morpheme'].tolist() if pd.notna(token)]
        labels = [str(label) for label in group['tag'].tolist() if pd.notna(label)]
        
        # Only add sequences where lengths match
        if len(sequence) == len(labels) and len(sequence) > 0:
            sequences.append(sequence)
            label_sequences.append(labels)
    
    print(f"✓ Loaded {len(sequences)} sequences")
    print(f"✓ Total tokens: {sum(len(seq) for seq in sequences)}")
    
    return sequences, label_sequences

def evaluate_model(crf, test_sequences, test_labels):
    """Evaluate CRF model performance"""
    print(f"\n📊 EVALUATING MODEL:")
    
    all_true_labels = []
    all_pred_labels = []
    
    correct_sequences = 0
    total_sequences = len(test_sequences)
    
    for seq, true_labels in zip(test_sequences, test_labels):
        pred_labels = crf.predict_sequence(seq)
        
        all_true_labels.extend(true_labels)
        all_pred_labels.extend(pred_labels)
        
        if pred_labels == true_labels:
            correct_sequences += 1
    
    # Calculate metrics
    token_accuracy = accuracy_score(all_true_labels, all_pred_labels)
    sequence_accuracy = correct_sequences / total_sequences
    
    print(f"✓ Token accuracy: {token_accuracy:.3f}")
    print(f"✓ Sequence accuracy: {sequence_accuracy:.3f}")
    
    # Detailed classification report
    print(f"\n📋 CLASSIFICATION REPORT:")
    report = classification_report(all_true_labels, all_pred_labels, zero_division=0)
    print(report)
    
    return token_accuracy, sequence_accuracy

def save_model(crf, filepath):
    """Save trained CRF model"""
    print(f"\n💾 SAVING MODEL:")
    
    model_data = {
        'feature_weights': dict(crf.feature_weights),
        'label_vocab': list(crf.label_vocab),
        'feature_vocab': list(crf.feature_vocab)
    }
    
    with open(filepath, 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"✓ Saved CRF model to {filepath}")
    print(f"✓ Feature weights: {len(crf.feature_weights)}")
    print(f"✓ Label vocabulary: {len(crf.label_vocab)}")

def analyze_feature_weights(crf):
    """Analyze learned feature weights"""
    print(f"\n🔍 FEATURE WEIGHT ANALYSIS:")
    
    # Group features by label
    label_features = defaultdict(list)
    
    for feature_label, weight in crf.feature_weights.items():
        if '_' in feature_label:
            # Split feature and label
            parts = feature_label.rsplit('_', 1)
            if len(parts) == 2:
                feature, label = parts
                label_features[label].append((feature, weight))
    
    # Show top features for each label
    for label in sorted(crf.label_vocab):
        if label in label_features:
            # Sort by absolute weight
            features = sorted(label_features[label], key=lambda x: abs(x[1]), reverse=True)
            print(f"\n  {label} (top features):")
            for feature, weight in features[:5]:
                print(f"    {feature}: {weight:.3f}")

def main():
    parser = argparse.ArgumentParser(description="Train CRF model for POS tagging")
    parser.add_argument('--tagged', required=True, help="Tagged corpus TSV file")
    parser.add_argument('--out', required=True, help="Output model file")
    parser.add_argument('--epochs', type=int, default=10, help="Training epochs")
    parser.add_argument('--test_split', type=float, default=0.1, help="Test set proportion")
    
    args = parser.parse_args()
    
    print("🤖 CRF TRAINER")
    print("=" * 13)
    
    # Load data
    sequences, label_sequences = load_tagged_data(args.tagged)
    
    # Split train/test
    train_seqs, test_seqs, train_labels, test_labels = train_test_split(
        sequences, label_sequences, test_size=args.test_split, random_state=42
    )
    
    print(f"\n📊 DATA SPLIT:")
    print(f"✓ Training sequences: {len(train_seqs)}")
    print(f"✓ Test sequences: {len(test_seqs)}")
    
    # Create and train CRF
    crf = SimpleCRF()
    crf.train(train_seqs, train_labels, epochs=args.epochs)
    
    # Evaluate model
    token_acc, seq_acc = evaluate_model(crf, test_seqs, test_labels)
    
    # Analyze learned features
    analyze_feature_weights(crf)
    
    # Save model
    save_model(crf, args.out)
    
    print(f"\n✅ CRF TRAINING COMPLETE!")
    print(f"✓ Token accuracy: {token_acc:.3f}")
    print(f"✓ Sequence accuracy: {seq_acc:.3f}")

if __name__ == "__main__":
    main() 