from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from backend.api.routes import chat, upload
from backend import config as app_config


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Warm up embeddings
    print("[startup] Loading embedding model...")
    app_config.get_embeddings()
    print("[startup] Embeddings ready.")

    # Initialize async checkpointer and compile graph
    print("[startup] Initializing checkpointer...")
    db_path = app_config.PROJECT_ROOT / "checkpoints.db"

    async with AsyncSqliteSaver.from_conn_string(str(db_path)) as checkpointer:
        from backend.graph import graph_builder
        from backend.nodes.clarification import clarification_node

        compiled = graph_builder.compile(
            checkpointer=checkpointer,
            interrupt_before=["clarification"]
        )

        # Make compiled graph available to routes
        app.state.graph = compiled
        print("[startup] Graph compiled and ready.")

        yield  # app runs here

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