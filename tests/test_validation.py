from __future__ import annotations

from unittest.mock import patch

from src.graph.nodes.validation import validation_node
from src.models.eval_result import EvalResult, Metric


def test_validation_crystallizes_on_threshold() -> None:
    state = {
        "task_class": "code_review",
        "discovered_knowledge": [],
        "current_config": None,
        "iteration": 1,
        "eval_results": [],
        "current_score": 0.0,
        "final_config": None,
        "is_crystallized": False,
    }

    eval_result = EvalResult(
        iteration=1,
        score=0.8,
        metrics=[Metric(name="f1", value=0.8, description="")],
        config_snapshot={},
        notes="",
    )

    with patch("src.graph.nodes.validation.load_dataset", return_value=[{"code": "", "expected_issues": []}]), patch(
        "src.graph.nodes.validation.run_evaluation", return_value=eval_result
    ):
        result = validation_node(state)

    assert result["is_crystallized"] is True
    assert result["current_score"] == 0.8


def test_validation_respects_max_iterations() -> None:
    state = {
        "task_class": "code_review",
        "discovered_knowledge": [],
        "current_config": None,
        "iteration": 10,
        "eval_results": [],
        "current_score": 0.0,
        "final_config": None,
        "is_crystallized": False,
    }

    eval_result = EvalResult(
        iteration=10,
        score=0.1,
        metrics=[Metric(name="f1", value=0.1, description="")],
        config_snapshot={},
        notes="",
    )

    with patch("src.graph.nodes.validation.load_dataset", return_value=[{"code": "", "expected_issues": []}]), patch(
        "src.graph.nodes.validation.run_evaluation", return_value=eval_result
    ):
        result = validation_node(state)

    assert result["is_crystallized"] is True
