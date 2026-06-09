from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from backend.state import AgentState
from backend.config import INTENT_CLASSIFIER_MODEL, CHAR_LIMIT
from backend.tools.youtube_tools import youtube_transcript_tool, extract_video_id
from backend.tools.web_tools import url_classifier
from backend.tools.summarizer import map_reduce_summarizer

intent_classifier_llm = ChatGroq(model=INTENT_CLASSIFIER_MODEL)


def url_router_node(state:AgentState):

    extracted_contents = state["extracted_contents"]

    counter = 1

    for url in state["urls_found"]:

        try:

            classification = url_classifier.invoke(
                {
                    "url": url
                }
            )

            if not classification["success"]:
                continue

            # -------------------------
            # YouTube URL
            # -------------------------

            if classification["type"] == "youtube":

                video_id = extract_video_id(url)

                result = (
                    youtube_transcript_tool.invoke(
                        {
                            "video_id": video_id
                        }
                    )
                )

                raw_transcript = result.get("transcript", "")

                # Auto-summarize if transcript exceeds context window
                if raw_transcript and len(raw_transcript) > CHAR_LIMIT:

                    summary_result = map_reduce_summarizer.invoke(
                        {
                            "text":        raw_transcript,
                            "source_type": "youtube"
                        }
                    )

                    transcript_to_store = (
                        summary_result["summary"]
                        if summary_result["success"]
                        else raw_transcript[:CHAR_LIMIT]
                    )

                else:

                    transcript_to_store = raw_transcript

                extracted_contents["files"][
                    f"url_{counter}"
                ] = {

                    "type": "youtube",

                    "source_url": url,

                    "transcript":
                        transcript_to_store,

                    "error":
                        result.get(
                            "error"
                        )
                }

        
            counter += 1

        except Exception as e:

            extracted_contents["files"][
                f"url_{counter}"
            ] = {

                "type": "url",

                "source_url": url,

                "error": str(e)
            }

            counter += 1

    return {

        "extracted_contents":
            extracted_contents
    }




def should_process_urls(state:AgentState):
    """
    Route to url_router ONLY if:
    - YouTube URLs were found in the document, AND
    - LLM determines user explicitly wants YouTube content processed
    """
    if not state.get("urls_found"):
        return "generate"

    youtube_discovered = any(
        "youtube" in u or "youtu.be" in u
        for u in state["urls_found"]
    )

    if not youtube_discovered:
        return "generate"

    # Ask LLM whether the user's query requires fetching YouTube content
    response = intent_classifier_llm.invoke([
        SystemMessage(content=(
            "You are an intent classifier. "
            "Answer only 'yes' or 'no', nothing else."
        )),
        HumanMessage(content=(
            f"Does this query explicitly ask to fetch, summarize, "
            f"transcribe, or extract information from a YouTube URL present either in the uploaded pdf (or pdfs) or in the user query?\n\n"
            f"Query: {state['query']}"
        ))
    ])

    if response.content.strip().lower().startswith("yes"):
        return "url_router"

    return "generate"