from __future__ import annotations

from unittest.mock import patch

from src.graph.graph import build_graph
from src.models.agent_config import AgentConfig, FlowStep, ToolSpec


def test_graph_runs_to_completion() -> None:
    config = AgentConfig(
        system_prompt="Prompt",
        tools=[ToolSpec(name="code_analysis", description="", enabled=True)],
        flow=[FlowStep(name="review", instructions="")],
        version=1,
    )

    with patch("src.graph.graph.discovery_node", return_value={"discovered_knowledge": ["a"]}), patch(
        "src.graph.graph.design_node", return_value={"current_config": config, "iteration": 1}
    ), patch(
        "src.graph.graph.validation_node",
        return_value={"current_score": 0.9, "eval_results": [], "is_crystallized": True},
    ), patch(
        "src.graph.graph.crystallization_node", return_value={"final_config": config}
    ):
        graph = build_graph()
        result = graph.invoke(
            {
                "task_class": "code_review",
                "discovered_knowledge": [],
                "current_config": config,
                "iteration": 0,
                "eval_results": [],
                "current_score": 0.0,
                "final_config": None,
                "is_crystallized": False,
            }
        )

    assert result["final_config"].system_prompt == "Prompt"


def test_graph_loops_when_not_crystallized() -> None:
    config = AgentConfig(
        system_prompt="Prompt",
        tools=[ToolSpec(name="code_analysis", description="", enabled=True)],
        flow=[FlowStep(name="review", instructions="")],
        version=1,
    )

    with patch("src.graph.graph.discovery_node", return_value={"discovered_knowledge": ["a"]}), patch(
        "src.graph.graph.design_node", return_value={"current_config": config, "iteration": 1}
    ), patch(
        "src.graph.graph.validation_node",
        side_effect=[
            {"current_score": 0.2, "eval_results": [], "is_crystallized": False},
            {"current_score": 0.9, "eval_results": [], "is_crystallized": True},
        ],
    ), patch(
        "src.graph.graph.crystallization_node", return_value={"final_config": config}
    ):
        graph = build_graph()
        result = graph.invoke(
            {
                "task_class": "code_review",
                "discovered_knowledge": [],
                "current_config": config,
                "iteration": 0,
                "eval_results": [],
                "current_score": 0.0,
                "final_config": None,
                "is_crystallized": False,
            }
        )

    assert result["final_config"].version == 1
