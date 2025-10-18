import os
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .schemas import UpsertRequest, SearchRequest, SearchResponse
from .rag import upsert_items, retrieve

load_dotenv()

AUTH_TOKEN = os.getenv("AUTH_TOKEN")

app = FastAPI(title="Qdrant RAG Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_auth(authorization: str = Header(default="")):
    if not AUTH_TOKEN:
        return
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if token != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/upsert", dependencies=[Depends(verify_auth)])
def upsert(req: UpsertRequest):
    ids = upsert_items(req.items)
    return {"upserted": ids}

@app.post("/search", response_model=SearchResponse, dependencies=[Depends(verify_auth)])
def search(req: SearchRequest):
    results = retrieve(query=req.query, top_k=req.top_k, score_threshold=req.score_threshold)
    return SearchResponse(query=req.query, results=results)

from fastapi.openapi.utils import get_openapi

@app.get("/openapi.json", include_in_schema=False)
def custom_openapi():
    return get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        servers=[{"url": "https://web-production-5ac0c.up.railway.app"}],
    )
