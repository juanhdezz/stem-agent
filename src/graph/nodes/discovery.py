from __future__ import annotations

from typing import List

try:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover - fallback for environments without deps
    class SystemMessage:  # type: ignore
        def __init__(self, content: str) -> None:
            self.content = content

    class HumanMessage:  # type: ignore
        def __init__(self, content: str) -> None:
            self.content = content

    class ChatOpenAI:  # type: ignore
        def __init__(self, *_: object, **__: object) -> None:
            raise RuntimeError("ChatOpenAI dependency is not available")

from src.graph.state import StemAgentState
from src.tools.web_search import search


SYSTEM_PROMPT = (
    "You are an expert research syntheses agent. "
    "Summarize how specialists approach the given task class. "
    "Extract concrete strategies, tools, and heuristics as bullet points."
)


def _format_results(results: List[dict]) -> str:
    if not results:
        return "No web results available."
    lines = []
    for result in results:
        title = result.get("title", "Untitled")
        content = result.get("content") or result.get("snippet") or ""
        url = result.get("url", "")
        lines.append(f"- {title} ({url}): {content}")
    return "\n".join(lines)


def _parse_knowledge(text: str) -> List[str]:
    items: List[str] = []
    for line in text.splitlines():
        stripped = line.strip().lstrip("- ").strip()
        if stripped:
            items.append(stripped)
    return items or ["Use static analysis and structured checklists."]


def discovery_node(state: StemAgentState) -> dict:
    task_class = state["task_class"]
    query = f"best practices for {task_class} code review and QA"
    results = search(query=query, max_results=5)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Task class: {task_class}\n\n"
                f"Web results:\n{_format_results(results)}\n\n"
                "Provide 6-10 bullet points."
            )
        ),
    ]
    response = llm.invoke(messages)
    knowledge = _parse_knowledge(response.content)
    return {"discovered_knowledge": knowledge}
