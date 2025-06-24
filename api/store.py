from pathlib import Path
from typing import List
from fastapi import UploadFile
from airz.vector_store import build_chroma, load_chroma
from airz.loaders import load_any, split_docs
from airz.retrieval import get_retriever
from .models import Document, SearchResponse, StoreStats, AddDocumentResponse

class VectorStore:
    def __init__(self, db_path: str = "./vector_store_db"):
        """Initialize vector store manager.
        
        Args:
            db_path: Path to the vector store database
        """
        self.db_path = db_path
        self._db = None
    
    @property
    def db(self):
        """Get or initialize the vector store."""
        if self._db is None:
            if Path(self.db_path).exists():
                self._db = load_chroma(self.db_path)
            else:
                self._db = build_chroma([], persist_dir=self.db_path)
        return self._db
    
    async def add_uploaded_document(
        self,
        file: UploadFile,
        chunk_size: int = 300,
        chunk_overlap: int = 20
    ) -> AddDocumentResponse:
        """Process an uploaded file and add it to the vector store.
        
        Args:
            file: Uploaded file
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            AddDocumentResponse with chunk count and message
        """
        # Save uploaded file temporarily
        temp_path = Path("temp_upload")
        try:
            content = await file.read()
            temp_path.write_bytes(content)
            
            # Load and chunk document
            docs = load_any(temp_path)
            chunks = split_docs(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            
            # Add to vector store
            self.db.add_documents(chunks)
            
            return AddDocumentResponse(
                message=f"Added {len(chunks)} chunks from {file.filename}",
                chunk_count=len(chunks)
            )
            
        finally:
            # Always clean up temp file
            if temp_path.exists():
                temp_path.unlink()
    
    def search(self, query: str, k: int = 4, threshold: float | None = None) -> SearchResponse:
        """Search for similar documents.
        
        Args:
            query: Search query
            k: Number of results to return
            threshold: Optional similarity threshold
            
        Returns:
            SearchResponse with query and results
        """
        retriever = get_retriever(self.db, k=k, threshold=threshold)
        results = retriever.invoke(query)
        
        documents = [
            Document(
                content=doc.page_content,
                metadata=doc.metadata
            )
            for doc in results
        ]
        
        return SearchResponse(
            query=query,
            results=documents
        )
    
    def get_stats(self) -> StoreStats:
        """Get vector store status."""
        return StoreStats(
            document_count=self.db._collection.count(),
            location=str(self.db_path)
        ) 