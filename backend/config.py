import os
from dotenv import load_dotenv

load_dotenv()

# API keys
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
os.environ['TAVILY_API_KEY'] = os.getenv('TAVILY_API_KEY')
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

# LangSmith tracing
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_PROJECT"] = "Multimodal agent trace4"
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "")

# Models
PLANNER_MODEL = "openai/gpt-oss-120b"
GENERATOR_MODEL = "openai/gpt-oss-120b"
INTENT_CLASSIFIER_MODEL = "llama-3.3-70b-versatile"
SUMMARIZER_MODEL = "llama-3.3-70b-versatile"
AUDIO_MODEL = "whisper-large-v3-turbo"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# Audio chunking
MAX_CHUNK_MB = 20
MAX_WORKERS = 4

# Summarizer limits
SUMMARIZER_TOKEN_LIMIT = 6000
CHARS_PER_TOKEN = 4
CHAR_LIMIT = SUMMARIZER_TOKEN_LIMIT * CHARS_PER_TOKEN  # ~24000 chars

# Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Path resolution
from pathlib import Path
if "__file__" in globals():
    PROJECT_ROOT = Path(__file__).resolve().parent
else:
    cwd = Path.cwd()
    PROJECT_ROOT = cwd.parent if cwd.name == "notebooks" else cwd
    