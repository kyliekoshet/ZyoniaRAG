import pytest
from pathlib import Path
from airz.loaders import load_any, split_docs

@pytest.fixture
def retrieval_doc():
    """Load the LangchainRetrieval.txt file."""
    doc_path = Path("testing_docs/LangchainRetrieval.txt")
    return load_any(doc_path)

def test_basic_chunking(retrieval_doc):
    """Test basic chunking with default parameters."""
    chunks = split_docs(retrieval_doc, chunk_size=300, overlap=20)
    assert len(chunks) > 1  # Should split into multiple chunks
    assert all(len(chunk.page_content) <= 400 for chunk in chunks)  # Allow some flexibility in chunk size


def test_small_document_single_chunk(retrieval_doc):
    """Test that very large chunk size results in single chunk."""
    chunks = split_docs(retrieval_doc, chunk_size=10000, overlap=20)
    assert len(chunks) == 1  # Should be a single chunk
    assert chunks[0].page_content == retrieval_doc[0].page_content  # Content should be unchanged 