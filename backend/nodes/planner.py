from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from backend.state import AgentState, PlannerDecision
from backend.prompts import PLANNER_SYSTEM_PROMPT
from backend.config import PLANNER_MODEL


llm = ChatGroq(model=PLANNER_MODEL)
planner_llm = llm.with_structured_output(PlannerDecision, method="json_mode")


def planner_node(state: AgentState):

    decision = planner_llm.invoke(
        [
            SystemMessage(
                content=PLANNER_SYSTEM_PROMPT
            ),

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
    )

    return {
        "query":state["query"],

        "task": decision.task,

        "required_actions": [
            {**action.model_dump(), "action_id": action.action_id or f"action_{i+1}"}
            for i, action in enumerate(decision.required_actions)
        ],

        "needs_clarification":
            decision.needs_clarification,

        "clarification_question":
            decision.clarification_question
    }



MAX_CLARIFICATION_ATTEMPTS = 3

def after_planner(state: AgentState):
    if state.get("needs_clarification"):
        if state.get("clarification_attempts", 0) >= MAX_CLARIFICATION_ATTEMPTS:
            # Give up, route to generate with whatever we have
            return "executor"
        return "clarification"
    return "executor"