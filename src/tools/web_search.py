from __future__ import annotations

import os
from typing import List, Dict, Any

try:
    from tavily import TavilyClient
except ImportError:  # pragma: no cover
    TavilyClient = None


def search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key or TavilyClient is None:
        return []
    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(query=query, max_results=max_results)
        return response.get("results", [])
    except Exception:
        return []
