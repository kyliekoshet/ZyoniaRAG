import pytest
import numpy as np
from pathlib import Path
from airz.embeddings import get_embedding_model
from airz.loaders import load_any, split_docs

def cosine_similarity(v1, v2):
    """Calculate cosine similarity between two vectors."""
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    return dot_product / (norm1 * norm2)

def test_embedding_model():
    """Test that the embedding model works correctly."""
    model = get_embedding_model()
    
    # Test single text embedding
    text = "This is a test document about retrieval augmented generation."
    embeddings = model.embed_query(text)
    
    # Basic checks
    assert embeddings is not None
    assert isinstance(embeddings, list)
    assert len(embeddings) > 0  # Should return a non-empty vector
    assert all(isinstance(x, float) for x in embeddings)  # Should be float values
    print("\nEmbedding vector length:", len(embeddings))
    print("First few values:", embeddings[:5])

def test_semantic_similarity():
    """Test that semantically similar texts have similar embeddings."""
    model = get_embedding_model()
    
    # Test pairs of semantically similar and dissimilar texts
    test_pairs = [
        # Similar pairs (should have high similarity)
        {
            "text1": "Document loading is important for RAG",
            "text2": "Loading documents is crucial for retrieval augmented generation",
            "expected": "high"
        },
        {
            "text1": "Vector stores help with similarity search",
            "text2": "Using vector databases for finding similar content",
            "expected": "high"
        },
        # Dissimilar pairs (should have lower similarity)
        {
            "text1": "Document loading is important for RAG",
            "text2": "The weather is nice today",
            "expected": "low"
        }
    ]
    
    for pair in test_pairs:
        emb1 = model.embed_query(pair["text1"])
        emb2 = model.embed_query(pair["text2"])
        
        # Calculate similarity
        similarity = cosine_similarity(emb1, emb2)
        
        print(f"\nTesting similarity for:")
        print(f"Text 1: {pair['text1']}")
        print(f"Text 2: {pair['text2']}")
        print(f"Similarity score: {similarity:.4f}")
        
        # Check if similarity matches expectation
        if pair["expected"] == "high":
            assert similarity > 0.7, f"Expected high similarity, got {similarity:.4f}"
        else:
            assert similarity < 0.7, f"Expected low similarity, got {similarity:.4f}"

def test_document_embeddings():
    """Test embedding generation for actual documents."""
    model = get_embedding_model()
    
    # Load and split a test document
    doc_path = Path("testing_docs/LangchainRetrieval.txt")
    docs = load_any(doc_path)
    chunks = split_docs(docs, chunk_size=300, overlap=20)
    
    # Get embeddings for each chunk
    embeddings = [model.embed_query(chunk.page_content) for chunk in chunks]
    
    # Basic checks
    assert len(embeddings) == len(chunks)
    assert all(len(emb) == len(embeddings[0]) for emb in embeddings)
    
    # Print some stats
    print(f"\nNumber of chunks: {len(chunks)}")
    print(f"Embedding dimension: {len(embeddings[0])}")
    
    # Test similarity between consecutive chunks (should be somewhat similar)
    for i in range(len(embeddings) - 1):
        similarity = cosine_similarity(embeddings[i], embeddings[i + 1])
        print(f"Similarity between chunks {i} and {i+1}: {similarity:.4f}")
        # Consecutive chunks should have some similarity due to overlap
        assert similarity > 0.4, f"Consecutive chunks should be somewhat similar" 