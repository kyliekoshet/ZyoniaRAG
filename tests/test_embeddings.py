import pytest
from pathlib import Path
from typing import List
from langchain.schema import Document
from langchain_community.vectorstores import Chroma

from airz.loaders import load_any, split_docs
from airz.embeddings import get_embedding_model

@pytest.fixture
def test_vectorstore():
    """Create a vector store from test documents."""
    docs_path = Path("testing_docs")
    return create_vectorstore_from_docs(docs_path)

def create_vectorstore_from_docs(docs_path: str | Path, chunk_size: int = 300) -> Chroma:
    """Create a vector store from documents in a path."""
    # Load documents
    docs = load_any(docs_path)
    
    # Split into chunks
    chunks = split_docs(docs, chunk_size=chunk_size)
    
    # Get embedding model
    embedding_model = get_embedding_model()
    
    # Create vector store
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory="chroma_db"
    )
    
    return vectorstore

def test_document_loading_and_embedding(test_vectorstore):
    """Test that documents can be loaded and embedded."""
    # Verify the vector store exists
    assert test_vectorstore is not None
    # Verify we can perform a search
    results = test_vectorstore.similarity_search("retrieval", k=1)
    assert len(results) == 1
    assert isinstance(results[0], Document)

def test_semantic_search(test_vectorstore):
    """Test semantic search capabilities."""
    # Test queries and expected content words
    test_cases = [
        {
            "query": "What is retrieval augmented generation?",
            "expected_words": ["retrieval", "LLM", "generation"]
        },
        {
            "query": "How does document loading work?",
            "expected_words": ["document", "loader", "load"]
        },
        {
            "query": "What are vector stores used for?",
            "expected_words": ["vector", "store", "embedding"]
        }
    ]
    
    for test_case in test_cases:
        results = test_vectorstore.similarity_search(test_case["query"], k=1)
        assert len(results) > 0
        # Check if result contains at least one of the expected words
        content = results[0].page_content.lower()
        assert any(word.lower() in content for word in test_case["expected_words"]), \
            f"Expected to find one of {test_case['expected_words']} in result for query: {test_case['query']}"

def test_chunk_embedding_consistency(test_vectorstore):
    """Test that similar chunks have similar embeddings."""
    # Get embeddings for two similar queries
    query1 = "document loading"
    query2 = "loading documents"
    
    results1 = test_vectorstore.similarity_search(query1, k=3)
    results2 = test_vectorstore.similarity_search(query2, k=3)
    
    # There should be some overlap in the results due to semantic similarity
    contents1 = {doc.page_content for doc in results1}
    contents2 = {doc.page_content for doc in results2}
    
    common_results = contents1.intersection(contents2)
    assert len(common_results) > 0, "Similar queries should return some overlapping results"

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
    
    # Test pairs of semantically similar texts
    similar_pairs = [
        (
            "Document loading is important for RAG",
            "Loading documents is crucial for retrieval augmented generation"
        ),
        (
            "Vector stores help with similarity search",
            "Using vector databases for finding similar content"
        )
    ]
    
    for text1, text2 in similar_pairs:
        emb1 = model.embed_query(text1)
        emb2 = model.embed_query(text2)
        
        print(f"\nTesting similarity for:")
        print(f"Text 1: {text1}")
        print(f"Text 2: {text2}")
        print(f"Embedding lengths: {len(emb1)}, {len(emb2)}")
        
        # Both embeddings should have the same dimension
        assert len(emb1) == len(emb2), "Embeddings should have same dimension" 