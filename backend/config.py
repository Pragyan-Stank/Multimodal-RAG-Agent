from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from pathlib import Path


def find_env_file() -> Path | str:
    start_dir = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
    for parent in [start_dir] + list(start_dir.parents):
        env_path = parent / ".env"
        if env_path.exists():
            return env_path
    return ".env"


# ---------------------------------
# Settings schema with validation
# ---------------------------------

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_env_file(),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    GROQ_API_KEY: str
    TAVILY_API_KEY: str
    HF_TOKEN: str
    LANGCHAIN_API_KEY: str = ""           # optional — tracing only
    LANGSMITH_ENDPOINT: str = ""          # optional

    @model_validator(mode="after")
    def check_required_keys(self):
        required = {
            "GROQ_API_KEY": self.GROQ_API_KEY,
            "TAVILY_API_KEY": self.TAVILY_API_KEY,
            "HF_TOKEN": self.HF_TOKEN,
        }
        missing = [k for k, v in required.items() if not v or v == "None"]
        if missing:
            raise ValueError(
                f"\n\n[CONFIG ERROR] Missing required API keys: {missing}\n"
                f"Add them to your .env file and restart.\n"
            )
        return self


# Instantiate once — crashes immediately at startup if keys are missing
try:
    settings = Settings()
except Exception as e:
    raise SystemExit(e)


# ---------------------------------
# Inject into environment for LangChain/Groq SDKs
# ---------------------------------

import os
os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY
os.environ["TAVILY_API_KEY"] = settings.TAVILY_API_KEY
os.environ["HF_TOKEN"] = settings.HF_TOKEN
os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
os.environ["LANGSMITH_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
os.environ["LANGCHAIN_TRACING_V2"] = "true" if settings.LANGCHAIN_API_KEY else "false"
os.environ["LANGSMITH_PROJECT"] = "Multimodal agent trace4"


# ---------------------------------
# Models
# ---------------------------------

PLANNER_MODEL = "llama-3.3-70b-versatile"
GENERATOR_MODEL = "llama-3.3-70b-versatile"
INTENT_CLASSIFIER_MODEL = "llama-3.3-70b-versatile"
SUMMARIZER_MODEL = "llama-3.3-70b-versatile"
AUDIO_MODEL = "whisper-large-v3-turbo"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


# ---------------------------------
# Audio chunking
# ---------------------------------

MAX_CHUNK_MB = 20
MAX_WORKERS = 4


# ---------------------------------
# Summarizer limits
# ---------------------------------

SUMMARIZER_TOKEN_LIMIT = 6000
CHARS_PER_TOKEN = 4
CHAR_LIMIT = SUMMARIZER_TOKEN_LIMIT * CHARS_PER_TOKEN


# ---------------------------------
# Embeddings (lazy loaded)
# ---------------------------------

_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        from langchain_huggingface import HuggingFaceEmbeddings
        _embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"local_files_only": True}
        )
    return _embeddings


# ---------------------------------
# Path resolution
# ---------------------------------

if "__file__" in globals():
    PROJECT_ROOT = Path(__file__).resolve().parent
else:
    cwd = Path.cwd()
    PROJECT_ROOT = cwd.parent if cwd.name == "notebooks" else cwd