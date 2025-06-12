# ZyoniaRAG

A RAG (Retrieval Augmented Generation) system built with LangChain

## Basic RAG Pipeline Steps

### 1. Loading Documents
Load documents from various sources using:
```python
from airz.loaders import load_any

# Load single file or directory
docs = load_any("path/to/your/docs")
```

### 2. Chunking Documents
Split documents into manageable chunks:
```python
from airz.loaders import split_docs

# Split with custom chunk size and overlap
chunks = split_docs(docs, chunk_size=300, overlap=20)
```

### 3. Creating Embeddings
Generate embeddings using Google's Generative AI:
```python
from airz.embeddings import get_embedding_model

# Get the embedding model (cached)
model = get_embedding_model()

# Create embeddings for text
embeddings = model.embed_query("your text here")
```

### 4. Vector Store Operations
Store and retrieve documents using Chroma vector store:
```python
from airz.vector_store import build_chroma, load_chroma

# Create or load a vector store
db = build_chroma(chunks, persist_dir="./my_chroma_db")  # Loads if exists, creates if not

# Force rebuild even if exists
db = build_chroma(chunks, persist_dir="./my_chroma_db", force_rebuild=True)

# Explicitly load existing database
loaded_db = load_chroma(persist_dir="./my_chroma_db")

# Search in any database instance
results = db.similarity_search("What is RAG?", k=1)
print(results[0].page_content)
```

Key features:
- **Smart Building**: Automatically loads existing database unless force_rebuild=True
- **Automatic Persistence**: Database is saved to disk when created
- **Reusable**: Load the same database across different sessions
- **Configurable**: Customize storage location with `persist_dir`
- **Efficient**: No need to recreate database each time

### 5. Advanced Retrieval
Configure and use retrievers with different strategies:
```python
from airz.retrieval import get_retriever, format_docs

# Create retrievers with different strategies
retriever_topk = get_retriever(db, k=4)  # Get top 4 most relevant docs
retriever_threshold = get_retriever(db, threshold=0.8)  # Get all docs with similarity > 0.8

# Get relevant documents
results_topk = retriever_topk.invoke("your query here")
results_threshold = retriever_threshold.invoke("your query here")

# Format retrieved documents into a single text
formatted_context = format_docs(results_topk)
```

Key features:
- **Top-K Retrieval**: Get the K most relevant documents
- **Threshold Retrieval**: Get all documents above a similarity threshold
- **Document Formatting**: Easily combine retrieved documents for LLM input
- **Flexible**: Switch between retrieval strategies based on your needs
