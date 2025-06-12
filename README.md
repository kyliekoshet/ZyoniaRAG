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

## Setup

### 1. Installation
```bash
# Clone the repository
git clone <repository_url>

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
1. Copy the example environment file:
```bash
cp env.example .env
```

2. Edit `.env` with your settings:
```bash
# Required
GOOGLE_API_KEY=your_google_api_key_here  # Get from https://makersuite.google.com/app/apikey

# Optional
CHUNK_SIZE=300  # Default chunk size
CHUNK_OVERLAP=20  # Default overlap
```

## Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_embeddings.py -v
```

