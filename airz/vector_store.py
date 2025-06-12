from pathlib import Path
from typing import Iterable
from langchain_chroma import Chroma
from langchain.schema import Document
from embeddings import get_embedding_model
from loaders import load_any, split_docs

def build_chroma(
    docs: Iterable[Document],
    persist_dir: str | Path = "./chroma_db",
    force_rebuild: bool = False,
) -> Chroma:
    """Build or load a Chroma vector store.
    
    Args:
        docs: Documents to store in the database
        persist_dir: Directory to store the database
        force_rebuild: If True, rebuild the database even if it exists
        
    Returns:
        Chroma: A vector store instance
    """
    persist_dir = Path(persist_dir)
    
    # Check if database already exists
    if not force_rebuild and persist_dir.exists():
        print(f"Loading existing database from {persist_dir}")
        return load_chroma(persist_dir)
        
    # Create parent directory if it doesn't exist
    persist_dir.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Building new database in {persist_dir}")
    return Chroma.from_documents(
        docs,
        embedding=get_embedding_model(),
        persist_directory=str(persist_dir),
    )

def load_chroma(persist_dir: str | Path = "./chroma_db") -> Chroma:
    return Chroma(
        embedding_function=get_embedding_model(),
        persist_directory=str(persist_dir),
    )

if __name__ == "__main__":
    # Example usage of the RAG pipeline
    print("Starting RAG demonstration...")
    
    # 1. Load documents
    doc_path = Path("testing_docs/LangchainRetrieval.txt")
    print(f"\n1. Loading documents from {doc_path}")
    docs = load_any(doc_path)
    print(f"Loaded {len(docs)} document(s)")
    
    # 2. Split into chunks
    print("\n2. Splitting documents into chunks")
    chunks = split_docs(docs, chunk_size=300, overlap=20)
    print(f"Created {len(chunks)} chunks")
    print(f"First chunk preview: {chunks[0].page_content[:100]}...")
    
    # 3. Create and save a new vector store
    print("\n3. Creating and saving a new vector store")
    persist_dir = "./demo_chroma_db"
    print(f"Creating new database in {persist_dir}")
    
    # First build - should create new
    db = build_chroma(chunks, persist_dir=persist_dir)
    print("✓ Database operation completed")
    
    # Second build - should load existing
    print("\n4. Trying to build again (should load existing)")
    db_loaded = build_chroma(chunks, persist_dir=persist_dir)
    print("✓ Database operation completed")
    
    # Force rebuild
    print("\n5. Force rebuilding the database")
    db_rebuilt = build_chroma(chunks, persist_dir=persist_dir, force_rebuild=True)
    print("✓ Database operation completed")
