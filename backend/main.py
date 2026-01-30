"""
Meta Ad Creator — Backend API (FastAPI).
Part 1: Health, CORS, Supabase client, JWT auth dependency.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS
from auth import get_current_user_id

app = FastAPI(
    title="Meta Ad Creator API",
    description="REST API for ad creation workflow and project management",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Public health check for load balancers and monitoring."""
    return {"status": "ok"}


@app.get("/api/me")
def me(user_id: str = Depends(get_current_user_id)):
    """Protected route example: return current user id (for testing auth)."""
    return {"user_id": user_id}
