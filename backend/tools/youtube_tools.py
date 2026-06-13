from urllib.parse import urlparse, parse_qs
from langchain.tools import tool
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from backend.utils.retry import api_retry


# ---------------------------------
# Retryable internal calls
# ---------------------------------

@api_retry
def _list_transcripts(ytt_api: YouTubeTranscriptApi, video_id: str):
    """List available transcripts with retry."""
    return ytt_api.list(video_id)


@api_retry
def _fetch_transcript(selected):
    """Fetch selected transcript with retry."""
    return selected.fetch()


# ---------------------------------
# Tool
# ---------------------------------

@tool
def youtube_transcript_tool(video_id: str) -> dict:
    """
    Fetch transcript from a YouTube video.
    """
    try:
        ytt_api = YouTubeTranscriptApi()

        transcript_list = _list_transcripts(ytt_api, video_id)

        selected = None
        for transcript in transcript_list:
            if transcript.language_code == "en":
                selected = transcript
                break

        if not selected:
            selected = next(iter(transcript_list))

        fetched = _fetch_transcript(selected)

        transcript_text = " ".join(
            item["text"]
            for item in fetched.to_raw_data()
        )

        return {
            "success": True,
            "video_id": video_id,
            "language": selected.language_code,
            "transcript": transcript_text
        }

    except TranscriptsDisabled:
        # Permanent failure — no captions exist, retrying won't help
        return {
            "success": False,
            "error": "No captions available for this video"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def extract_video_id(url: str) -> str | None:
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]

    parsed = urlparse(url)
    return parse_qs(parsed.query).get("v", [None])[0]