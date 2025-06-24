from fastapi import APIRouter, UploadFile, HTTPException, Depends
from .store import VectorStore
from .models import SearchQuery, SearchResponse, AddDocumentResponse, StoreStats

# Create router
router = APIRouter(prefix="/api")

# Initialize vector store
store = VectorStore()

@router.post("/documents", response_model=AddDocumentResponse)
async def add_document(
    file: UploadFile,
    chunk_size: int = 300,
    chunk_overlap: int = 20
):
    """Add a document to the vector store."""
    try:
        return await store.add_uploaded_document(
            file=file,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=SearchResponse)
async def search_documents(query: SearchQuery = Depends()):
    """Search for similar documents."""
    try:
        return store.search(
            query=query.query,
            k=query.k,
            threshold=query.threshold
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=StoreStats)
async def get_status():
    """Get vector store status."""
    try:
        return store.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 