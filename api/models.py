from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class Document(BaseModel):
    """A document with its content and metadata."""
    content: str
    metadata: Dict

class SearchQuery(BaseModel):
    """Search query parameters."""
    query: str
    k: int = Field(default=4, gt=0, description="Number of results to return")
    threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Similarity threshold"
    )

class SearchResponse(BaseModel):
    """Search results response."""
    query: str
    results: List[Document]

class AddDocumentResponse(BaseModel):
    """Response after adding a document."""
    message: str
    chunk_count: int

class StoreStats(BaseModel):
    """Vector store statistics."""
    document_count: int
    location: str 