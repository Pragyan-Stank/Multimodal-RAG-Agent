from langgraph.types import Command
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend import config as app_config
from backend.graph import graph

UPLOAD_DIR = app_config.PROJECT_ROOT / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def run(query: str, file_paths: list[str]):
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

    graph_config = {"configurable": {"thread_id": "session_1"}}

    for event in graph.stream(initial_state, config=graph_config):
        print(event)
        print("=" * 80)

    # Keep asking until graph finishes
    while True:
        snapshot = graph.get_state(graph_config)

        # No more interrupts — graph is done
        if not snapshot.next:
            break

        # Graph is waiting for clarification — ask the user
        user_response = input("\nAgent is asking for clarification.\nYou: ").strip()

        for event in graph.stream(
            Command(resume=user_response),
            config=graph_config
        ):
            print(event)
            print("=" * 80)


if __name__ == "__main__":
    run(
        query="tell me",
        file_paths=[str(UPLOAD_DIR / "crag.pdf")]
    )