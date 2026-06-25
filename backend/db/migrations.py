from backend.db.connection import get_pool


CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""

CREATE_USERS_EMAIL_INDEX = """
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
"""

ENABLE_PGCRYPTO = """
CREATE EXTENSION IF NOT EXISTS pgcrypto;
"""


async def run_migrations():
    """
    Idempotent migration runner — safe to call on every startup.
    CREATE TABLE IF NOT EXISTS / CREATE INDEX IF NOT EXISTS means
    re-running this does nothing if the schema already exists.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        # gen_random_uuid() requires pgcrypto on most Postgres setups
        # (Neon usually has it, but enable explicitly to be safe)
        await conn.execute(ENABLE_PGCRYPTO)
        await conn.execute(CREATE_USERS_TABLE)
        await conn.execute(CREATE_USERS_EMAIL_INDEX)
        print("[migrations] users table ready.")