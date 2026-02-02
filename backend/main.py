"""
Meta Ad Creator — Backend API (FastAPI).

Part 1: Health, CORS, Supabase client, JWT auth dependency.
Part 2.2 (in progress): Projects CRUD.
"""
from typing import Any

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS
from auth import get_current_user_id
from supabase_client import get_supabase

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


class ProjectCreate(BaseModel):
    """Payload for creating a new project."""

    name: str | None = Field(
        default=None,
        description="Optional human-friendly project name shown in the dashboard.",
        max_length=255,
    )
    meta: dict[str, Any] | None = Field(
        default=None,
        description="Optional metadata (e.g. product_name, target_audience, promotion_text).",
    )


@app.get("/api/projects")
def list_projects(user_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    """
    List projects for the authenticated user.

    Uses Supabase service role client and filters by user_id.
    Returns a JSON object with a "projects" list.
    """
    supabase = get_supabase()
    result = (
        supabase.table("projects")
        .select(
            "id,user_id,name,status,meta,created_at,updated_at",
        )
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    projects = result.data or []
    return {"projects": projects}


@app.post("/api/projects", status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """
    Create a new project for the authenticated user.

    - Sets user_id from the JWT (ignores any user_id from the client).
    - Defaults status to 'draft'.
    """
    supabase = get_supabase()

    insert_data: dict[str, Any] = {
        "user_id": user_id,
        "status": "draft",
    }
    if payload.name is not None:
        insert_data["name"] = payload.name
    if payload.meta is not None:
        insert_data["meta"] = payload.meta

    result = supabase.table("projects").insert(insert_data).execute()

    # supabase-py v2 returns a list of inserted rows in result.data
    rows = result.data or []
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project",
        )

    project = rows[0]
    return {"project": project}


@app.get("/api/projects/{project_id}")
def get_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """
    Get a single project by id for the authenticated user.

    Returns 404 if the project does not exist or does not belong to the user.
    """
    supabase = get_supabase()
    try:
        result = (
            supabase.table("projects")
            .select("id,user_id,name,status,meta,created_at,updated_at")
            .eq("id", project_id)
            .eq("user_id", user_id)
            .execute()
        )
    except Exception:
        # Treat any underlying DB error (including malformed UUIDs) as "not found"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    rows = result.data or []
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    project = rows[0]
    return {"project": project}
