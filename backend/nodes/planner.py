from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from backend.state import AgentState, PlannerDecision
from backend.prompts import PLANNER_SYSTEM_PROMPT
from backend.config import PLANNER_MODEL
from backend.utils.retry import llm_retry


llm = ChatGroq(model=PLANNER_MODEL)
planner_llm = llm.with_structured_output(PlannerDecision, method="json_mode")

MAX_CLARIFICATION_ATTEMPTS = 3


# ---------------------------------
# Retryable internal call
# ---------------------------------

@llm_retry
def _call_planner(messages: list) -> PlannerDecision:
    """Planner LLM call with retry."""
    return planner_llm.invoke(messages)


# ---------------------------------
# Node
# ---------------------------------

def planner_node(state: AgentState):

    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(
            content=f"""
            User Query:
            {state["query"]}

            Available PDF Files:
            {state["pdf_files"]}

            Available Audio Files:
            {state["audio_files"]}

            Available Image Files:
            {state["image_files"]}
            """
        )
    ]

    decision = _call_planner(messages)

    return {
        "query": state["query"],
        "task": decision.task,
        "required_actions": [
            {**action.model_dump(), "action_id": action.action_id or f"action_{i+1}"}
            for i, action in enumerate(decision.required_actions)
        ],
        "needs_clarification": decision.needs_clarification,
        "clarification_question": decision.clarification_question
    }