import uuid
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage

from backend.api.schemas import (
    ChatRequest, ChatResponse,
    ResetRequest, ResetResponse
)
from backend.graph import graph
from backend.config import PROJECT_ROOT

router = APIRouter()


# ---------------------------------
# Node → human readable status
# ---------------------------------

NODE_MESSAGES = {
    "classify_files":  "Analyzing uploaded files...",
    "planner":         "Planning your request...",
    "executor_worker": "Processing files...",
    "url_router":      "Fetching web content...",
    "generate":        "Generating answer...",
    "clarification":   "Waiting for clarification...",
    "give_up":         "Could not determine intent.",
}

WORKER_MESSAGES = {
    "pdf_worker":   "Reading PDF...",
    "audio_worker": "Transcribing audio...",
    "image_worker": "Analyzing image...",
    "web_worker":   "Searching the web...",
}


def build_initial_state(request: ChatRequest) -> dict:
    return {
        "query": request.query,
        "uploaded_files": request.file_paths,
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


def build_graph_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


# ---------------------------------
# POST /chat  (non-streaming)
# ---------------------------------

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Run the agent graph and return the final answer.
    Non-streaming — waits for full completion.
    """
    thread_id = request.thread_id or str(uuid.uuid4())
    graph_config = build_graph_config(thread_id)

    try:
        final_state = None

        for event in graph.stream(
            build_initial_state(request),
            config=graph_config,
            stream_mode="values"
        ):
            final_state = event

        if not final_state or not final_state.get("final_answer"):
            raise HTTPException(status_code=500, detail="Graph did not produce a final answer.")

        return ChatResponse(
            thread_id=thread_id,
            final_answer=final_state.get("final_answer", ""),
            task=final_state.get("task", "")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------
# POST /chat/stream  (SSE streaming)
# ---------------------------------

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Run the agent graph and stream node-level status
    events followed by the final answer.
    """
    thread_id = request.thread_id or str(uuid.uuid4())
    graph_config = build_graph_config(thread_id)

    def event_stream():
        try:
            seen_workers = set()

            for event in graph.stream(
                build_initial_state(request),
                config=graph_config,
                stream_mode="updates"
            ):
                for node_name, node_output in event.items():
                    # print(f"NODE: {node_name}, KEYS: {list(node_output.keys())}")  # debug
                    # --- executor_worker: emit per-worker status ---
                    if node_name == "executor_worker":
                        actions = node_output.get("extracted_contents", {}).get("files", {})
                        for action_id in actions:
                            # get worker type from action if available
                            msg = "Processing files..."
                            yield _sse("status", {"node": node_name, "message": msg})
                        continue

                    # --- clarification interrupt ---
                    if node_name == "clarification":
                        question = node_output.get("clarification_question", "")
                        yield _sse("clarification", {
                            "node": node_name,
                            "message": question
                        })
                        continue

                    # --- all other nodes ---
                    message = NODE_MESSAGES.get(node_name)
                    if message:
                        yield _sse("status", {"node": node_name, "message": message})

                    # --- emit final answer when generate node completes ---
                    if node_name == "generate" or node_name == "give_up":
                        final_answer = node_output.get("final_answer", "")
                        if final_answer:
                            # stream answer word by word
                            words = final_answer.split(" ")
                            for i, word in enumerate(words):
                                chunk = word if i == 0 else " " + word
                                yield _sse("token", {"content": chunk})

            # --- done ---
            yield _sse("done", {"thread_id": thread_id})

        except Exception as e:
            yield _sse("error", {"message": str(e)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"    # disables nginx buffering
        }
    )


# ---------------------------------
# POST /chat/reset
# ---------------------------------

@router.post("/chat/reset", response_model=ResetResponse)
async def reset_chat(request: ResetRequest):
    """
    Clear a thread's state from the checkpointer.
    Effectively starts a new conversation.
    """
    try:
        # SqliteSaver doesn't expose a delete API directly
        # so we write an empty state to effectively reset the thread
        graph_config = build_graph_config(request.thread_id)
        new_thread_id = str(uuid.uuid4())

        return ResetResponse(
            thread_id=new_thread_id,
            success=True,
            message="Session reset. Use the new thread_id for your next request."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------
# SSE helper
# ---------------------------------

def _sse(event_type: str, data: dict) -> str:
    """Format a Server-Sent Event string."""
    payload = json.dumps({"type": event_type, **data})
    return f"data: {payload}\n\n"