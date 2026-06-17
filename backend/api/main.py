from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from backend.api.routes import chat, upload
from backend import config as app_config
from backend.db.connection import init_pool, close_pool


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Init DB connection pool
    print("[startup] Connecting to Neon...")
    await init_pool()
    print("[startup] DB pool ready.")

    # Warm up embeddings
    print("[startup] Loading embedding model...")
    app_config.get_embeddings()
    print("[startup] Embeddings ready.")

    # Initialize Postgres checkpointer and compile graph
    print("[startup] Initializing checkpointer...")

    async with AsyncPostgresSaver.from_conn_string(
        app_config.NEON_DATABASE_URL
    ) as checkpointer:
        await checkpointer.setup()  # creates langgraph checkpoint tables if not exist

        from backend.graph import graph_builder

        compiled = graph_builder.compile(
            checkpointer=checkpointer,
            interrupt_before=["clarification"]
        )

        app.state.graph = compiled
        print("[startup] Graph compiled and ready.")

        yield

    # Cleanup
    await close_pool()
    print("[shutdown] Cleaning up...")


app = FastAPI(
    title="Multimodal Agent API",
    description="LangGraph-powered multimodal RAG agent",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(chat.router,   prefix="/api/v1", tags=["chat"])


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "version": "0.1.0"}