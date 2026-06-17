import hashlib
import asyncio
from typing import List
from backend.db.connection import get_pool
from backend.config import get_embeddings, TEST_USER_ID


def _hash_file(content: str) -> str:
    """Deterministic hash of document content."""
    return hashlib.sha256(content.encode()).hexdigest()


async def document_exists(file_hash: str, user_id: str = TEST_USER_ID) -> bool:
    """Check if document chunks already exist in DB for this user."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT 1 FROM document_chunks
            WHERE file_hash = $1 AND user_id = $2
            LIMIT 1
            """,
            file_hash, user_id
        )
    return row is not None


async def store_document_chunks(
    content: str,
    file_name: str,
    user_id: str = TEST_USER_ID,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> str:
    """
    Chunk, embed, and store document content in pgvector.
    Returns file_hash for later retrieval.
    Skips if already stored (idempotent).
    """
    file_hash = _hash_file(content)

    # Idempotency check — don't re-embed if already stored
    if await document_exists(file_hash, user_id):
        return file_hash

    # Chunking — done in thread since it's CPU bound
    def _chunk(text: str) -> list[str]:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return splitter.split_text(text)

    chunks = await asyncio.to_thread(_chunk, content)

    # Embed all chunks in thread (CPU bound)
    def _embed(texts: list[str]) -> list[list[float]]:
        embeddings = get_embeddings()
        return embeddings.embed_documents(texts)

    vectors = await asyncio.to_thread(_embed, chunks)

    # Batch insert into Neon
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.executemany(
            """
            INSERT INTO document_chunks
                (file_hash, file_name, chunk_index, content, embedding, user_id)
            VALUES
                ($1, $2, $3, $4, $5::vector, $6)
            """,
            [
                (file_hash, file_name, i, chunk, str(vectors[i]), user_id)
                for i, chunk in enumerate(chunks)
            ]
        )

    return file_hash


async def retrieve_similar_chunks(
    query: str,
    file_hash: str,
    user_id: str = TEST_USER_ID,
    k: int = 5,
) -> list[str]:
    """
    Embed query and retrieve top-k similar chunks from pgvector.
    Scoped to specific document and user.
    """
    def _embed_query(text: str) -> list[float]:
        return get_embeddings().embed_query(text)

    query_vector = await asyncio.to_thread(_embed_query, query)

    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT content
            FROM document_chunks
            WHERE file_hash = $1 AND user_id = $2
            ORDER BY embedding <=> $3::vector
            LIMIT $4
            """,
            file_hash, user_id, str(query_vector), k
        )

    return [row["content"] for row in rows]