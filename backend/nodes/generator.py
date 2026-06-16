from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from backend.state import AgentState
from backend.prompts import GENERATE_SYSTEM_PROMPT
from backend.config import GENERATOR_MODEL
from backend.utils.retry import async_llm_retry

generator_llm = ChatGroq(model=GENERATOR_MODEL)


# ---------------------------------
# Retryable internal call
# ---------------------------------

async def _call_generator(messages: list) -> str:
    """Async generator LLM call with retry."""
    response = await async_llm_retry(generator_llm.ainvoke, messages)
    return response.content


# ---------------------------------
# Node
# ---------------------------------

async def generate_node(state: AgentState):

    messages = [
        SystemMessage(content=GENERATE_SYSTEM_PROMPT),
        HumanMessage(
            content=f"""
            User Query:
            {state['query']}

            Task:
            {state['task']}

            Extracted Contents:
            {state['extracted_contents']}

            Note: Any source with was_summarized=True was too large for the context
            window and has been pre-summarized. Treat its content as a summary,
            not the full original.
            """
        )
    ]

    final_answer = await _call_generator(messages)
    return {"final_answer": final_answer}