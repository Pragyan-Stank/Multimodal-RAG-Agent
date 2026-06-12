from langgraph.types import Send
from backend.nodes.planner import MAX_CLARIFICATION_ATTEMPTS


def route_to_workers(state: dict):
    
    # Case 1: Needs clarification and attempts not exhausted → ask user
    if state.get("needs_clarification"):
        if state.get("clarification_attempts", 0) < MAX_CLARIFICATION_ATTEMPTS:
            return "clarification"
        
        # Case 2: Max attempts hit → user never clarified → end gracefully
        return "give_up"

    # Case 3: No actions planned (pure general chat, unknown task, etc.)
    actions = state.get("required_actions", [])
    if not actions:
        return "generate"

    # Case 4: Normal path → fan out one worker per action
    return [
        Send("executor_worker", {
            "action": action,
            "query": state["query"]
        })
        for action in actions
    ]