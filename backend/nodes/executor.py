from backend.state import AgentState, ExecutorState
from backend.prompts import EXECUTOR_SYSTEM_PROMPT
from backend.config import CHAR_LIMIT
from backend.tools.pdf_tools import pdf_parser, document_retriever
from backend.tools.audio_tools import transcribe_audio
from backend.tools.image_tools import image_analyser
from backend.tools.web_tools import web_search
from backend.tools.summarizer import map_reduce_summarizer



def executor_node(state: ExecutorState):

    extracted_contents = {
        "files": {}
    }

    urls_found = []

    for action in state["required_actions"]:

        action_id = action["action_id"]

        worker = action["worker"]

        operation = action["operation"]

        file_path = action.get("file_path")

        if worker in ["pdf_worker", "audio_worker", "image_worker"] and not file_path:
            extracted_contents["files"][action_id] = {
                "error": f"File path not provided for {worker}"
            }
            continue

        try:

            # ---------------------------------
            # PDF WORKER
            # ---------------------------------

            if worker == "pdf_worker":

                pdf_result = pdf_parser.invoke(
                    {
                        "file_path": file_path
                    }
                )

                if not pdf_result["success"]:

                    extracted_contents["files"][
                        action_id
                    ] = {
                        "type": "pdf",
                        "error": pdf_result["error"]
                    }

                    continue

                urls = pdf_result.get(
                    "urls",
                    []
                )

                urls_found.extend(urls)

                # Full document

                if operation == "full_document":

                    raw_content = pdf_result["content"]

                    # Auto-summarize if content exceeds context window
                    if len(raw_content) > CHAR_LIMIT:

                        summary_result = map_reduce_summarizer.invoke(
                            {
                                "text":        raw_content,
                                "source_type": "pdf"
                            }
                        )

                        content_to_store = (
                            summary_result["summary"]
                            if summary_result["success"]
                            else raw_content[:CHAR_LIMIT]   # fallback: hard truncate
                        )

                        was_summarized = summary_result.get("success", False)

                    else:

                        content_to_store = raw_content
                        was_summarized   = False

                    extracted_contents["files"][
                        action_id
                    ] = {
                        "type":          "pdf",
                        "content":       content_to_store,
                        "was_summarized": was_summarized,
                        "urls":          urls
                    }

                # Retrieval

                elif operation == "retrieve":

                    retrieval_result = (
                        document_retriever.invoke(
                            {
                                "document_content":
                                    pdf_result["content"],

                                "query":
                                    action.get("query") or state["query"]
                            }
                        )
                    )

                    if retrieval_result["success"]:

                        extracted_contents["files"][
                            action_id
                        ] = {
                            "type": "pdf",
                            "retrieved_context":
                                retrieval_result[
                                    "retrieved_context"
                                ],
                            "urls": urls
                        }

                    else:

                        extracted_contents["files"][
                            action_id
                        ] = {
                            "type": "pdf",
                            "error":
                                retrieval_result[
                                    "error"
                                ]
                        }

            # ---------------------------------
            # AUDIO WORKER
            # ---------------------------------

            elif worker == "audio_worker":

                result = (
                    transcribe_audio.invoke(
                        {
                            "audio_path":
                                file_path
                        }
                    )
                )

                if result["success"]:

                    raw_transcript = result["transcript"]

                    # Auto-summarize if transcript exceeds context window
                    if len(raw_transcript) > CHAR_LIMIT:

                        summary_result = map_reduce_summarizer.invoke(
                            {
                                "text":        raw_transcript,
                                "source_type": "audio"
                            }
                        )

                        transcript_to_store = (
                            summary_result["summary"]
                            if summary_result["success"]
                            else raw_transcript[:CHAR_LIMIT]
                        )

                        was_summarized = summary_result.get("success", False)

                    else:

                        transcript_to_store = raw_transcript
                        was_summarized      = False

                    extracted_contents["files"][
                        action_id
                    ] = {
                        "type":           "audio",
                        "transcript":     transcript_to_store,
                        "was_summarized": was_summarized
                    }

                else:

                    extracted_contents["files"][
                        action_id
                    ] = {
                            "type": "audio",
                            "error":
                                result["error"]
                    }

            # ---------------------------------
            # IMAGE WORKER
            # ---------------------------------

            elif worker == "image_worker":

                result = (
                    image_analyser.invoke(
                        {
                            "file_path":
                                file_path,

                            "query":
                                state["query"]
                        }
                    )
                )

                if result["success"]:

                    extracted_contents["files"][
                        action_id
                    ] = {
                        "type": "image",
                        "analysis":
                            result["analysis"]
                    }

                else:

                    extracted_contents["files"][
                        action_id
                    ] = {
                        "type": "image",
                        "error":
                            result["error"]
                    }

            # ---------------------------------
            # WEB WORKER
            # ---------------------------------

            elif worker == "web_worker":

                result = (
                    web_search.invoke(
                        {
                            "query":
                                action.get("query") or state["query"]
                        }
                    )
                )

                if result["success"]:

                    extracted_contents["files"][
                        action_id
                    ] = {
                        "type": "web",
                        "content":
                            str(result["results"])
                    }

                else:

                    extracted_contents["files"][
                        action_id
                    ] = {
                        "type": "web",
                        "error":
                            result["error"]
                    }

        except Exception as e:

            extracted_contents["files"][
                action_id
            ] = {
                "error": str(e)
            }

    return {

        "extracted_contents":
            extracted_contents,

        "urls_found":
            list(set(urls_found))
    }
