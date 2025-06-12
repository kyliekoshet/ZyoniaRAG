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

