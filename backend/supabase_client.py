"""Supabase client (service role) for server-side DB and Storage."""
from supabase import create_client, Client

from config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY


def get_supabase() -> Client:
    """Return a Supabase client with service role. Call only when env is set."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set. See backend/.env.example."
        )
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
