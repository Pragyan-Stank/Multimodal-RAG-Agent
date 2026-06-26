from langchain_core.messages import BaseMessage

RECENT_TURNS_TO_KEEP = 3

def get_recent_history_str(messages: list[BaseMessage]) -> str:
    """
    Format up to RECENT_TURNS_TO_KEEP turns of conversation history from state['messages'].
    The last message is the query/answer currently being processed.
    We exclude the last message to get the prior context.
    """
    if not messages:
        return ""
        
    prior_messages = messages[:-1]
    
    limit = 2 * RECENT_TURNS_TO_KEEP
    recent_messages = prior_messages[-limit:] if limit > 0 else []
    
    history_lines = []
    for msg in recent_messages:
        role = "User" if msg.type == "human" else "Assistant"
        history_lines.append(f"{role}: {msg.content}")
        
    return "\n\n".join(history_lines)
