from pathlib import Path
from typing import List
from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, CSVLoader, DirectoryLoader, UnstructuredExcelLoader
)
from langchain.schema import Document

def load_any(path: str | Path) -> List[Document]:
    """Dispatch to the right LC loader based on suffix / folder."""
    p = Path(path)
    if p.is_dir():
        return DirectoryLoader(str(p), glob="**/*.*", show_progress=True).load()

    match p.suffix.lower():
        case ".pdf":
            return PyPDFLoader(str(p)).load_and_split()
        case ".csv":
            # default: one row ⇒ one Document
            return CSVLoader(file_path=str(p)).load()
        case ".xlsx" | ".xls":
            return UnstructuredExcelLoader(str(p)).load()
        case _:
            return TextLoader(str(p)).load()
        

def split_docs(docs, chunk_size=300, overlap=20):
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=overlap, length_function=len
    )
    return splitter.split_documents(docs)

if __name__ == "__main__":
    # Quick demonstration of loader functionality
    print("Document Loading Demonstration")
    
    # 1. Load a single text file
    from pathlib import Path
    doc_path = Path("testing_docs/LangchainRetrieval.txt")
    
    print(f"\n1. Loading document from {doc_path}")
    docs = load_any(doc_path)
    print(f"Loaded {len(docs)} document(s)")
    print(f"First document preview: {docs[0].page_content[:100]}...")
    
    # 2. Demonstrate chunking
    print("\n2. Splitting document into chunks")
    chunks = split_docs(docs, chunk_size=300, overlap=20)
    print(f"Created {len(chunks)} chunks")
    print(f"First chunk preview: {chunks[0].page_content[:100]}...")
    print(f"Last chunk preview: {chunks[-1].page_content[:100]}...")
    
    # 3. Show chunk overlap
    if len(chunks) > 1:
        overlap = set(chunks[0].page_content.split()) & set(chunks[1].page_content.split())
        print(f"\n3. Demonstrating overlap between chunks")
        print(f"Found {len(overlap)} overlapping words between first two chunks")
