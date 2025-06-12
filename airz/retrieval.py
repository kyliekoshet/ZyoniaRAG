from langchain.vectorstores.base import VectorStore
from langchain.schema import Document

def get_retriever(
    store: VectorStore,
    k: int = 4,
    threshold: float | None = None,
):
    """Get a retriever from a vector store with either top-k or threshold-based retrieval.
    
    Args:
        store: The vector store to create a retriever from
        k: Number of documents to retrieve in top-k mode
        threshold: If set, use similarity threshold instead of top-k
        
    Returns:
        A retriever configured for either top-k or threshold-based retrieval
    """
    if threshold is None:
        return store.as_retriever(search_kwargs={"k": k})
    return store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": threshold},
    )

def format_docs(docs: list[Document]) -> str:
    """Combine multiple documents into a single string.
    
    Args:
        docs: List of Documents to combine
        
    Returns:
        A single string with all document contents, separated by double newlines
    """
    return "\n\n".join(d.page_content for d in docs)


if __name__ == "__main__":
    print("Retrieval Demonstration")
    
    # 1. Set up a sample vector store
    from vector_store import build_chroma
    from loaders import load_any, split_docs
    from pathlib import Path
    
    print("\n1. Loading and preparing documents")
    docs = load_any("testing_docs/LangchainRetrieval.txt")
    chunks = split_docs(docs, chunk_size=300, overlap=20)
    store = build_chroma(chunks, persist_dir="./demo_chroma_db")
    print(f"Prepared {len(chunks)} chunks for retrieval")
    
    # 2. Demonstrate top-k retrieval
    print("\n2. Top-K Retrieval (k=2)")
    retriever_topk = get_retriever(store, k=2)
    query = "What is retrieval augmented generation?"
    results_topk = retriever_topk.invoke(query)
    
    print(f"\nQuery: {query}")
    print(f"Retrieved {len(results_topk)} documents")
    print("\nFormatted Results:")
    print("-" * 50)
    print(format_docs(results_topk))
    
    # 3. Demonstrate threshold-based retrieval
    print("\n3. Threshold-based Retrieval (threshold=0.8)")
    retriever_threshold = get_retriever(store, threshold=0.8)
    results_threshold = retriever_threshold.invoke(query)
    
    print(f"\nQuery: {query}")
    print(f"Retrieved {len(results_threshold)} documents with similarity > 0.8")
    print("\nFormatted Results:")
    print("-" * 50)
    print(format_docs(results_threshold)) 