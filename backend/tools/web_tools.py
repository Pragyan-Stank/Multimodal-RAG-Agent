from langchain.tools import tool
from langchain_tavily import TavilySearch

@tool
def web_search(query: str) -> dict:
    """
    Search the web for up-to-date information.
    """

    try:

        tavily = TavilySearch(
            max_results=5
        )

        results = tavily.invoke(
            {"query": query}
        )

        return {
            "success": True,
            "query": query,
            "results": results
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


@tool
def url_classifier(url: str) -> dict:
    """
    Classify URL type.
    """

    if "youtube.com" in url or "youtu.be" in url:
        return {
            "success":True,
            "url": url,
            "type": "youtube"
        }

    return {
        "success":True,
        "url": url,
        "type": "website"
    }