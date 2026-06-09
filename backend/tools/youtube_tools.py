from urllib.parse import urlparse, parse_qs
from langchain.tools import tool
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled



@tool
def youtube_transcript_tool(video_id: str) -> dict:
    """
    Fetch transcript from a YouTube video.
    """

    try:
        ytt_api = YouTubeTranscriptApi()

        transcript_list = ytt_api.list(video_id)

        selected = None

        for transcript in transcript_list:
            if transcript.language_code == "en":
                selected = transcript
                break

        if not selected:
            selected = next(iter(transcript_list))

        fetched = selected.fetch()

        transcript_data = fetched.to_raw_data()

        transcript_text = " ".join(
            item["text"]
            for item in transcript_data
        )

        return {
            "success": True,
            "video_id": video_id,
            "language": selected.language_code,
            "transcript": transcript_text
        }

    except TranscriptsDisabled:
        return {
            "success": False,
            "error": "No captions available for this video"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def extract_video_id(url):

    if "youtu.be" in url:
        # strip everything after ? (tracking params like ?si=...)
        return url.split("/")[-1].split("?")[0]

    parsed = urlparse(url)

    return parse_qs(
        parsed.query
    ).get("v", [None])[0]
