# ZyoniaRAG

A RAG (Retrieval Augmented Generation) system built with LangChain.

## Current Features

### Document Loading (`airz/loaders.py`)
- Supports multiple file formats:
  - PDF files
  - CSV files
  - Excel files (XLSX/XLS)
  - Text files
  - Directory loading (recursive)
- Document splitting functionality with customizable chunk size and overlap