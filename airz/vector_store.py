from pathlib import Path
from typing import Iterable
from langchain_chroma import Chroma
from langchain.schema import Document
from embeddings import get_embedding_model
from loaders import load_any, split_docs

def build_chroma(
    docs: Iterable[Document],
    persist_dir: str | Path = "./chroma_db",
) -> Chroma:
    # Chroma automatically persists when created
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
    print(f"   Loaded {len(docs)} documents")
    
    # 2. Split into chunks
    print("\n2. Splitting documents into chunks")
    chunks = split_docs(docs, chunk_size=300, overlap=20)
    print(f"   Created {len(chunks)} chunks")
    print(f"   First chunk preview: {chunks[0].page_content[:100]}...")
    
    # 3. Create and save a new vector store
    print("\n3. Creating and saving a new vector store")
    persist_dir = "./demo_chroma_db"
    print(f"   Creating new database in {persist_dir}")
    db = build_chroma(chunks, persist_dir=persist_dir)
    print("   ✓ Database created and saved to disk")
    
    # 4. Perform a search with the newly created database
    print("\n4. Searching in the newly created database")
    query = "What is RAG?"
    print(f"   Query: {query}")
    results = db.similarity_search(query, k=1)
    print(f"   Result from new database: {results[0].page_content[:200]}...")
    
    # 5. Now, let's pretend we're starting a new Python session
    print("\n5. Simulating a new session by loading the saved database")
    print(f"   Loading existing database from {persist_dir}")
    loaded_db = load_chroma(persist_dir=persist_dir)
    print("   ✓ Successfully loaded database from disk")
    
    # 6. Search with the loaded database
    print("\n6. Searching in the loaded database")
    print(f"   Same query: {query}")
    loaded_results = loaded_db.similarity_search(query, k=1)
    print(f"   Result from loaded database: {loaded_results[0].page_content[:200]}...")
    
    # 7. Verify both give same results
    print("\n7. Comparing results")
    original_text = results[0].page_content[:100]
    loaded_text = loaded_results[0].page_content[:100]
    print("   Are results identical?", original_text == loaded_text)
    if original_text == loaded_text:
        print("   ✓ Both databases return exactly the same results!")
