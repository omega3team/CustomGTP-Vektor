import os, hashlib, uuid
from typing import List
from openai import OpenAI
from qdrant_client.http.models import PointStruct

from .qdrant_client_utils import get_qdrant, ensure_collection, upsert_points, search_vectors
from .schemas import UpsertItem, RetrievedChunk

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

_oai = OpenAI(api_key=OPENAI_API_KEY)

def embed_texts(texts: List[str]) -> List[List[float]]:
    vectors = []
    for t in texts:
        emb = _oai.embeddings.create(model=EMBEDDING_MODEL, input=t)
        vectors.append(emb.data[0].embedding)
    return vectors

def make_id(s: str) -> str:
    h = hashlib.sha1(s.encode("utf-8")).hexdigest()
    return h or str(uuid.uuid4())

def upsert_items(items: List[UpsertItem]):
    client = get_qdrant()
    ensure_collection(client)
    texts = [i.text for i in items]
    vecs = embed_texts(texts)
    points = []
    for i, v in zip(items, vecs):
        pid = i.id or make_id(i.text)
        points.append(PointStruct(id=pid, vector=v, payload={"text": i.text, **(i.metadata or {})}))
    upsert_points(client, points)
    return [p.id for p in points]

def retrieve(query: str, top_k: int = 5, score_threshold: float | None = None) -> List[RetrievedChunk]:
    client = get_qdrant()
    ensure_collection(client)
    vec = embed_texts([query])[0]
    hits = search_vectors(client, vec, top_k, score_threshold)
    out: List[RetrievedChunk] = []
    for h in hits:
        payload = h.payload or {}
        out.append(
            RetrievedChunk(
                id=str(h.id),
                text=payload.get("text", ""),
                metadata={k:v for k,v in payload.items() if k != "text"},
                score=float(h.score)
            )
        )
    return out
