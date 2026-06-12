from langchain.tools import tool
from langchain_tavily import TavilySearch
from backend.utils.retry import api_retry


# ---------------------------------
# Retryable internal call
# ---------------------------------

@api_retry
def _tavily_search(query: str):
    """Tavily search with retry."""
    tavily = TavilySearch(max_results=5)
    return tavily.invoke({"query": query})


# ---------------------------------
# Tools
# ---------------------------------

@tool
def web_search(query: str) -> dict:
    """
    Search the web for up-to-date information.
    """
    try:
        results = _tavily_search(query)
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
        return {"success": True, "url": url, "type": "youtube"}

    return {"success": True, "url": url, "type": "website"}