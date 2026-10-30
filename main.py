from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from search import search_courses
from collections import defaultdict, deque
import anthropic
import os
import threading
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Every search is a paid Claude request and the endpoint is public, so cap
# how many searches one visitor can do per minute.
MAX_SEARCHES_PER_MINUTE = 10

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

_hits = defaultdict(deque)
_hits_lock = threading.Lock()


def allow_search(ip: str) -> bool:
    now = time.monotonic()
    with _hits_lock:
        hits = _hits[ip]
        while hits and hits[0] <= now - 60:
            hits.popleft()
        if len(hits) >= MAX_SEARCHES_PER_MINUTE:
            return False
        hits.append(now)
        return True


def client_ip(request: Request) -> str:
    # Railway's proxy puts the visitor's address first in X-Forwarded-For.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=300)
    top_k: int = Field(default=5, ge=1, le=10)


@app.get("/", response_class=HTMLResponse)
def index():
    with open(os.path.join(BASE_DIR, "templates/index.html"), "r", encoding="utf-8") as f:
        return f.read()


@app.post("/search")
def search(request: SearchRequest, http_request: Request):
    if not allow_search(client_ip(http_request)):
        raise HTTPException(status_code=429, detail="Te veel zoekopdrachten, probeer het zo opnieuw.")
    try:
        results = search_courses(request.query.strip(), request.top_k)
    except (anthropic.APIError, RuntimeError) as e:
        print(f"Search failed: {type(e).__name__}: {e}")
        raise HTTPException(status_code=503, detail="Zoeken is even niet beschikbaar.")
    return {"results": results}


@app.get("/health")
def health():
    return {"status": "ok"}
