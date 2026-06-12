import uuid
from langgraph.types import Command
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend import config as app_config
from backend.graph import graph

UPLOAD_DIR = app_config.PROJECT_ROOT / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def run(query: str, file_paths: list[str], thread_id: str | None = None):
    """
    thread_id: pass a stable ID to resume an existing session,
               or None to start a fresh one.
    """
    thread_id = thread_id or str(uuid.uuid4())
    graph_config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "query": query,
        "uploaded_files": file_paths,
        "pdf_files": [],
        "audio_files": [],
        "image_files": [],
        "task": "",
        "required_actions": [],
        "needs_clarification": False,
        "clarification_attempts": 0,
        "clarification_question": "",
        "awaiting_clarification": False,
        "extracted_contents": {"files": {}},
        "urls_found": [],
        "messages": [],
        "final_answer": ""
    }

    print(f"[Session: {thread_id}]")

    for event in graph.stream(initial_state, config=graph_config):
        print(event)
        print("=" * 80)

    while True:
        snapshot = graph.get_state(graph_config)
        if not snapshot.next:
            break

        user_response = input("\nAgent needs clarification.\nYou: ").strip()

        for event in graph.stream(Command(resume=user_response), config=graph_config):
            print(event)
            print("=" * 80)

    return thread_id


if __name__ == "__main__":
    run(
        query="tell me",
        file_paths=[str(UPLOAD_DIR / "crag.pdf")]
    )