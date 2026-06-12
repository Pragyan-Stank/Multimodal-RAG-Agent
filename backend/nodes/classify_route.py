from pathlib import Path
from backend.state import AgentState

def classify_and_route(state: AgentState) -> dict:
    """Classify uploaded files and populate state before planning."""
    result = {"pdf_files": [], "audio_files": [], "image_files": []}
    for file in state.get("uploaded_files", []):
        suffix = Path(file).suffix.lower()
        if suffix == ".pdf":
            result["pdf_files"].append(file)
        elif suffix in [".mp3", ".wav", ".m4a"]:
            result["audio_files"].append(file)
        elif suffix in [".jpg", ".jpeg", ".png"]:
            result["image_files"].append(file)
    return result
