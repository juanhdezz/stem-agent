from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.graph.nodes.discovery import discovery_node


def test_discovery_returns_knowledge() -> None:
    state = {
        "task_class": "code_review",
        "discovered_knowledge": [],
        "current_config": None,
        "iteration": 0,
        "eval_results": [],
        "current_score": 0.0,
        "final_config": None,
        "is_crystallized": False,
    }

    with patch("src.graph.nodes.discovery.search", return_value=[{"title": "A", "content": "B"}]), patch(
        "src.graph.nodes.discovery.ChatOpenAI"
    ) as mock_llm:
        mock_llm.return_value.invoke.return_value = MagicMock(content="- Use checklists\n- Run static analysis")
        result = discovery_node(state)

    assert "discovered_knowledge" in result
    assert result["discovered_knowledge"] == ["Use checklists", "Run static analysis"]


def test_discovery_handles_empty_response() -> None:
    state = {
        "task_class": "code_review",
        "discovered_knowledge": [],
        "current_config": None,
        "iteration": 0,
        "eval_results": [],
        "current_score": 0.0,
        "final_config": None,
        "is_crystallized": False,
    }

    with patch("src.graph.nodes.discovery.search", return_value=[]), patch(
        "src.graph.nodes.discovery.ChatOpenAI"
    ) as mock_llm:
        mock_llm.return_value.invoke.return_value = MagicMock(content="")
        result = discovery_node(state)

    assert result["discovered_knowledge"]
