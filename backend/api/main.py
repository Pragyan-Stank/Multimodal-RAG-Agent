from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.api.routes import chat, upload
from backend import config as app_config

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once at startup and once at shutdown.
    Use for warming up connections, loading models, etc.
    """
    # Warm up embeddings at startup so first request isn't slow
    print("[startup] Loading embedding model...")
    app_config.get_embeddings()
    print("[startup] Embeddings ready.")

    yield  # app runs here

    # Shutdown cleanup (add DB pool closing here later)
    print("[shutdown] Cleaning up...")


# ---------------------------------
# App
# ---------------------------------

app=FastAPI(
    title="Multimodal Agent API",
    description="LangGraph-powered multimodal RAG chatbot",
    version="0.1.0",
    lifespan=lifespan
)

# ---------------------------------
# CORS
# ---------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # React dev server
        "http://localhost:5173",    # Vite dev server
        "http://localhost:8501",    # Streamlit
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---------------------------------
# Routers
# ---------------------------------

app.include_router(upload.router,prefix="/api/v1",tags=["upload"])
app.include_router(chat.router,prefix="/api/v1",tags=["chat"])


# ---------------------------------
# Health check
# ---------------------------------

@app.get("/health",tags=["health"])
async def health():
    return {"status":"ok","version":"0.1.0"}