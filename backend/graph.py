from langgraph.graph import StateGraph, START, END
from backend.state import AgentState
from backend.nodes.planner import planner_node, after_planner
from backend.nodes.executor import executor_node
from backend.nodes.url_router import url_router_node, should_process_urls
from backend.nodes.clarification import clarification_node
from backend.nodes.generator import generate_node
from pathlib import Path
from langgraph.checkpoint.memory import MemorySaver


def classify_files(files):
    result = {"pdf_files": [], "audio_files": [], "image_files": []}
    for file in files:
        suffix = Path(file).suffix.lower()
        if suffix == ".pdf":
            result["pdf_files"].append(file)
        elif suffix in [".mp3", ".wav", ".m4a"]:
            result["audio_files"].append(file)
        elif suffix in [".jpg", ".jpeg", ".png"]:
            result["image_files"].append(file)
    return result

def input_router(state):
    return classify_files(state["uploaded_files"])




builder = StateGraph(AgentState)
builder.add_node("input_router", input_router)
builder.add_node("planner", planner_node)
builder.add_node("clarification", clarification_node)
builder.add_node("executor", executor_node)
builder.add_node("url_router", url_router_node)
builder.add_node("generate", generate_node)

builder.add_edge(START, "input_router")
builder.add_edge("input_router", "planner")
builder.add_conditional_edges("planner", after_planner, {"clarification": "clarification", "executor": "executor"})
builder.add_edge("clarification", "planner")
builder.add_conditional_edges("executor", should_process_urls, {"url_router": "url_router", "generate": "generate"})
builder.add_edge("url_router", "generate")
builder.add_edge("generate", END)

graph = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["clarification"]
)