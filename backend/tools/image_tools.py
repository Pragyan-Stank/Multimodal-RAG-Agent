import base64, mimetypes
from pathlib import Path
from langchain.tools import tool
from groq import Groq
from backend.config import PROJECT_ROOT, VISION_MODEL

client = Groq()

@tool
def image_analyser(
    file_path: str,
    query: str = "Describe this image in detail."
) -> dict:
    """
    Analyze an image using a vision model.
    """

    try:

        path = Path(file_path)

        if not path.is_absolute():
            path = PROJECT_ROOT / path

        path = path.resolve()

        if not path.exists():
            return {
                "success": False,
                "error": f"Image file not found: {path}"
            }

        mime_type, _ = mimetypes.guess_type(path)

        if mime_type is None:
            mime_type = "image/jpeg"

        with open(path, "rb") as img_file:
            image_b64 = base64.b64encode(
                img_file.read()
            ).decode("utf-8")

        image_url = (
            f"data:{mime_type};base64,{image_b64}"
        )

        completion = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": query
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            temperature=0
        )

        analysis = (
            completion
            .choices[0]
            .message
            .content
        )

        return {
            "success": True,
            "file_path": str(path),
            "analysis": analysis
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }