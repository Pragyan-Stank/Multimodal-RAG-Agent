from langchain.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from groq import Groq
from backend.config import CHAR_LIMIT, SUMMARIZER_MODEL

client = Groq()


@tool
def map_reduce_summarizer(text: str, source_type: str = "document") -> dict:
    """
    Summarize arbitrarily large text using Map-Reduce.

    Splits text into chunks that fit the 8k context window,
    summarizes each chunk independently (MAP), then combines
    all chunk summaries into a final summary (REDUCE).

    Use whenever text length may exceed ~6000 tokens.
    Works for: PDF content, audio transcripts, YouTube transcripts,
    webpage content, or any large block of text.

    Args:
        text:        The raw text to summarize.
        source_type: Label for logging — 'pdf', 'audio', 'youtube', etc.
    """

    try:

        # -------------------------------------------------------
        # Short enough — summarize directly in one shot
        # -------------------------------------------------------

        if len(text) <= CHAR_LIMIT:

            response = client.chat.completions.create(
                model=SUMMARIZER_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a precise summarizer. "
                            "Return a concise but complete summary."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Summarize the following {source_type}:\n\n{text}"
                        )
                    }
                ],
                max_tokens=800,
                temperature=0
            )

            return {
                "success":    True,
                "strategy":   "direct",
                "num_chunks": 1,
                "summary":    response.choices[0].message.content
            }

        # -------------------------------------------------------
        # Too large — MAP phase: chunk and summarize each piece
        # -------------------------------------------------------

        splitter = RecursiveCharacterTextSplitter(
            chunk_size    = CHAR_LIMIT,
            chunk_overlap = 800           # ~200 tokens overlap to avoid losing context at boundaries
        )

        chunks = splitter.split_text(text)

        chunk_summaries = []

        for i, chunk in enumerate(chunks):

            response = client.chat.completions.create(
                model=SUMMARIZER_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a precise summarizer. "
                            "Summarize this section, preserving "
                            "key facts, names, numbers, and decisions."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Summarize section {i+1} of {len(chunks)} "
                            f"from a {source_type}:\n\n{chunk}"
                        )
                    }
                ],
                max_tokens=600,
                temperature=0
            )

            chunk_summaries.append(
                response.choices[0].message.content
            )

        # -------------------------------------------------------
        # REDUCE phase: combine chunk summaries into final summary
        # -------------------------------------------------------

        combined = "\n\n---\n\n".join(
            f"[Section {i+1}]\n{s}"
            for i, s in enumerate(chunk_summaries)
        )

        reduce_response = client.chat.completions.create(
            model=SUMMARIZER_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise summarizer. "
                        "You will receive a list of section summaries "
                        "from a larger document. Synthesize them into "
                        "one coherent, complete final summary. Do not "
                        "repeat yourself. Connect ideas across sections."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Combine these {len(chunks)} section summaries "
                        f"from a {source_type} into one final summary:\n\n"
                        f"{combined}"
                    )
                }
            ],
            max_tokens=1000,
            temperature=0
        )

        return {
            "success":         True,
            "strategy":        "map_reduce",
            "num_chunks":      len(chunks),
            "chunk_summaries": chunk_summaries,
            "summary":         reduce_response.choices[0].message.content
        }

    except Exception as e:

        return {
            "success": False,
            "error":   str(e)
        }
