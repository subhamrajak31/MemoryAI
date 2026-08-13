"""
Web search integration tool using DuckDuckGo Search.
"""

from __future__ import annotations

from ddgs import DDGS

from utils.logger import logger


class WebSearchTool:
    """
    Executes real-time web searches and extracts structured result summaries.
    """

    def __init__(self, max_results: int = 5) -> None:
        self.max_results = max_results

    def search(self, query: str) -> str:
        """
        Perform a web search for a query string and return formatted summaries.
        """
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self.max_results))

            if not results:
                return f"No web search results found for query: '{query}'."

            formatted_results = []
            for idx, res in enumerate(results, start=1):
                title = res.get("title", "No Title")
                snippet = res.get("body", "No Description")
                link = res.get("href", "")
                formatted_results.append(
                    f"[{idx}] {title}\nSummary: {snippet}\nURL: {link}"
                )

            return "\n\n".join(formatted_results)

        except Exception as error:
            logger.exception("Web search error for query '%s': %s", query, error)
            return f"Error executing web search: {error}"


def web_search(query: str, max_results: int = 5) -> str:
    """
    Standalone wrapper function for tool execution.
    """
    search_tool = WebSearchTool(max_results=max_results)
    return search_tool.search(query)