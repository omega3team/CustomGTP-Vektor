import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from typing import List, Optional

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "omega3-QD")
EMBED_DIM = 1536

def get_qdrant() -> QdrantClient:
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=30)

def ensure_collection(client: QdrantClient):
    collections = client.get_collections().collections
    names = {c.name for c in collections}
    if QDRANT_COLLECTION not in names:
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )

def upsert_points(client: QdrantClient, points: List[PointStruct]):
    client.upsert(collection_name=QDRANT_COLLECTION, points=points)

def search_vectors(client: QdrantClient, vector: List[float], top_k: int, score_threshold: Optional[float] = None):
    res = client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=vector,
        limit=top_k,
        score_threshold=score_threshold,
        with_payload=True,
    )
    return res
