from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from backend.state import AgentState
from backend.prompts import GENERATE_SYSTEM_PROMPT
from backend.config import GENERATOR_MODEL

generator_llm = ChatGroq(model=GENERATOR_MODEL)

def generate_node(state:AgentState):

    response = generator_llm.invoke(

        [
            SystemMessage(
                content=GENERATE_SYSTEM_PROMPT
            ),

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
    )

    return {

        "final_answer":
            response.content
    }
