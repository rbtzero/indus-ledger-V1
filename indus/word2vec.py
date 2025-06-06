#!/usr/bin/env python3
import argparse
import logging
from gensim.models import Word2Vec
from gensim.models.callbacks import CallbackAny2Vec
import numpy as np

class EpochLogger(CallbackAny2Vec):
    def __init__(self):
        self.epoch = 0

    def on_epoch_end(self, model):
        self.epoch += 1
        print(f"  Epoch {self.epoch} completed")

def load_corpus(filepath):
    """Load phoneme sequences as sentences for Word2Vec"""
    sentences = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                # Split into morphemes
                morphemes = line.split()
                if len(morphemes) >= 2:  # Need at least 2 morphemes for context
                    sentences.append(morphemes)
    
    print(f"✓ Loaded {len(sentences)} sequences for training")
    return sentences

def train_word2vec(sentences, size=100, window=2, min_count=3, epochs=10):
    """Train Word2Vec model on Indus morpheme sequences"""
    print(f"\n🧠 TRAINING WORD2VEC MODEL:")
    print(f"✓ Vector size: {size}")
    print(f"✓ Context window: {window}")
    print(f"✓ Min count: {min_count}")
    print(f"✓ Epochs: {epochs}")
    
    # Count vocabulary first
    vocab_count = {}
    for sentence in sentences:
        for word in sentence:
            vocab_count[word] = vocab_count.get(word, 0) + 1
    
    valid_vocab = {word: count for word, count in vocab_count.items() if count >= min_count}
    print(f"✓ Vocabulary: {len(valid_vocab)} morphemes (min_count >= {min_count})")
    
    # Train model
    model = Word2Vec(
        sentences=sentences,
        vector_size=size,
        window=window,
        min_count=min_count,
        workers=4,
        epochs=epochs,
        callbacks=[EpochLogger()],
        sg=0,  # CBOW
        seed=42
    )
    
    print(f"✓ Training completed!")
    print(f"✓ Final vocabulary size: {len(model.wv.key_to_index)}")
    
    return model

def save_embeddings(model, output_path):
    """Save word embeddings in standard format"""
    print(f"\n💾 SAVING EMBEDDINGS:")
    
    with open(output_path, 'w') as f:
        # Header
        vocab_size = len(model.wv.key_to_index)
        vector_size = model.wv.vector_size
        f.write(f"{vocab_size} {vector_size}\n")
        
        # Embeddings
        for word in model.wv.key_to_index:
            vector = model.wv[word]
            vector_str = ' '.join([f"{x:.6f}" for x in vector])
            f.write(f"{word} {vector_str}\n")
    
    print(f"✓ Saved {vocab_size} embeddings to {output_path}")
    
    # Show some similar words as examples
    print(f"\n🔍 SIMILARITY EXAMPLES:")
    example_words = ['nan', 'pa', 'ra', 'sa', 'ka']
    
    for word in example_words:
        if word in model.wv.key_to_index:
            try:
                similar = model.wv.most_similar(word, topn=5)
                similar_words = [f"{w}({s:.3f})" for w, s in similar]
                print(f"  {word}: {', '.join(similar_words)}")
            except:
                print(f"  {word}: insufficient context")

def main():
    parser = argparse.ArgumentParser(description="Train Word2Vec on Indus morpheme sequences")
    parser.add_argument('--corpus', required=True, help="Input corpus file (phoneme sequences)")
    parser.add_argument('--size', type=int, default=100, help="Vector dimensionality")
    parser.add_argument('--window', type=int, default=2, help="Context window size")
    parser.add_argument('--min_count', type=int, default=3, help="Minimum word frequency")
    parser.add_argument('--epochs', type=int, default=10, help="Training epochs")
    parser.add_argument('--out', required=True, help="Output embeddings file")
    
    args = parser.parse_args()
    
    print("🔤 INDUS WORD2VEC TRAINING")
    print("=" * 26)
    
    # Load corpus
    sentences = load_corpus(args.corpus)
    
    if len(sentences) < 10:
        print("❌ ERROR: Too few sentences for meaningful training")
        return
    
    # Train model
    model = train_word2vec(
        sentences, 
        size=args.size, 
        window=args.window, 
        min_count=args.min_count,
        epochs=args.epochs
    )
    
    # Save embeddings
    save_embeddings(model, args.out)
    
    print(f"\n✅ WORD2VEC TRAINING COMPLETE!")

if __name__ == "__main__":
    main() 