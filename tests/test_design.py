from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from src.graph.nodes.design import design_node
from src.models.agent_config import AgentConfig


def test_design_generates_config() -> None:
    state = {
        "task_class": "code_review",
        "discovered_knowledge": ["Use checklists"],
        "current_config": None,
        "iteration": 0,
        "eval_results": [],
        "current_score": 0.0,
        "final_config": None,
        "is_crystallized": False,
    }

    payload = {
        "system_prompt": "Prompt",
        "tools": [{"name": "code_analysis", "description": "Analyze", "enabled": True}],
        "flow": [{"name": "review", "instructions": "Review"}],
        "version": 1,
    }

    with patch("src.graph.nodes.design.ChatOpenAI") as mock_llm:
        mock_llm.return_value.invoke.return_value = MagicMock(content=json.dumps(payload))
        result = design_node(state)

    assert isinstance(result["current_config"], AgentConfig)
    assert result["current_config"].system_prompt == "Prompt"
    assert result["iteration"] == 1


def test_design_fallback_on_invalid_json() -> None:
    state = {
        "task_class": "code_review",
        "discovered_knowledge": ["Use checklists"],
        "current_config": None,
        "iteration": 0,
        "eval_results": [],
        "current_score": 0.0,
        "final_config": None,
        "is_crystallized": False,
    }

    with patch("src.graph.nodes.design.ChatOpenAI") as mock_llm:
        mock_llm.return_value.invoke.return_value = MagicMock(content="not-json")
        result = design_node(state)

    assert result["current_config"].tools
