from pydantic import BaseModel
from typing import List, Optional, Any

class UpsertItem(BaseModel):
    id: Optional[str] = None
    text: str
    metadata: Optional[dict[str, Any]] = None

class UpsertRequest(BaseModel):
    items: List[UpsertItem]

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    score_threshold: Optional[float] = None

class RetrievedChunk(BaseModel):
    id: str
    text: str
    score: float
    metadata: Optional[dict] = None

class SearchResponse(BaseModel):
    query: str
    results: List[RetrievedChunk]
