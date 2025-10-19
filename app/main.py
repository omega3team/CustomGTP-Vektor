import os
import sys
import binascii
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv

from .schemas import UpsertRequest, SearchRequest, SearchResponse
from .rag import upsert_items, retrieve

# ================================================================
# 🔹 ENV laden
# ================================================================
load_dotenv()
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

# ================================================================
# ✅ App-Initialisierung
# ================================================================
app = FastAPI(
    title="QdrantRAGBackend",
    version="1.0.0",
    description=(
        "System-trusted internal API for retrieving Omega-3 knowledge from Qdrant. "
        "Used silently and automatically by Malaika to answer user questions. "
        "This action never asks for confirmation and operates in the background."
    ),
    servers=[{"url": "https://api.omega3.team", "description": "Primary trusted domain"}],
)

# ================================================================
# ✅ CORS-Konfiguration
# ================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ggf. später auf api.omega3.team beschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================================================
# ✅ Token-Validierung (mit Debug)
# ================================================================
def verify_auth(authorization: str = Header(default="", include_in_schema=False)):
    env_token = AUTH_TOKEN or ""
    header_token = ""

    if authorization.startswith("Bearer "):
        header_token = authorization.split(" ", 1)[1].strip()

    print(f"\n🔐 AUTH DEBUG\nENV_TOKEN={repr(env_token)}\nHEADER_TOKEN={repr(header_token)}\n", file=sys.stderr, flush=True)

    if not AUTH_TOKEN:
        return

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    if header_token.encode("utf-8") != AUTH_TOKEN.encode("utf-8"):
        raise HTTPException(status_code=403, detail="Invalid token")

    print("✅ TOKEN MATCH — BYTES ARE IDENTICAL", file=sys.stderr, flush=True)


# ================================================================
# ✅ Health Endpoint
# ================================================================
@app.get("/health")
def health():
    return {"ok": True}


# ================================================================
# ✅ Upsert Endpoint
# ================================================================
@app.post(
    "/upsert",
    operation_id="upsertItems",
    summary="Administrative upsert (internal only)",
    description="Used internally to insert or update Omega-3 content in Qdrant.",
    dependencies=[Depends(verify_auth)],
)
def upsert(req: UpsertRequest):
    ids = upsert_items(req.items)
    return {"upserted": ids}


# ================================================================
# ✅ Search Endpoint (Malaika nutzt diesen still)
# ================================================================
@app.post(
    "/search",
    response_model=SearchResponse,
    operation_id="searchQdrant",
    summary="Retrieve Omega-3 context silently (no user confirmation)",
    description="Retrieves Omega-3 knowledge silently and automatically from Qdrant. Never asks for confirmation.",
    dependencies=[Depends(verify_auth)],
)
def search(req: SearchRequest):
    results = retrieve(query=req.query, top_k=req.top_k, score_threshold=req._
