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

# Create and save a new vector store
db = build_chroma(chunks, persist_dir="./my_chroma_db")

# Search in the database
results = db.similarity_search("What is RAG?", k=1)
print(results[0].page_content)

# Later: Load existing database
loaded_db = load_chroma(persist_dir="./my_chroma_db")
results = loaded_db.similarity_search("What is RAG?", k=1)
```

Key features:
- Automatic persistence: Database is saved to disk when created
- Reusable: Load the same database across different sessions
- Configurable: Customize storage location with `persist_dir`
- Efficient: No need to recreate database each time
