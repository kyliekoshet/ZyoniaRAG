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
