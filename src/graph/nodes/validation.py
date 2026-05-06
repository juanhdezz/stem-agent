from __future__ import annotations

import os
from typing import List

from src.evaluation.dataset import load_dataset
from src.evaluation.runner import run_evaluation
from src.graph.state import StemAgentState
from src.models.eval_result import EvalResult


def _sample_dataset(dataset: List[dict]) -> List[dict]:
    max_samples = int(os.getenv("MAX_VALIDATION_SAMPLES", "5"))
    return dataset[: max_samples if max_samples > 0 else len(dataset)]


def validation_node(state: StemAgentState) -> dict:
    dataset_path = os.getenv("EVAL_DATASET_PATH", "data/benchmark/samples.jsonl")
    dataset = load_dataset(dataset_path)
    sample = _sample_dataset(dataset)

    eval_result: EvalResult = run_evaluation(state["current_config"], sample)
    eval_result.iteration = state.get("iteration", 0)

    threshold = float(os.getenv("VALIDATION_THRESHOLD", "0.70"))
    max_iterations = int(os.getenv("MAX_ITERATIONS", "5"))
    iteration = state.get("iteration", 0)

    eval_results = list(state.get("eval_results", [])) + [eval_result]
    is_crystallized = eval_result.is_above_threshold(threshold) or iteration >= max_iterations

    return {
        "current_score": eval_result.score,
        "eval_results": eval_results,
        "is_crystallized": is_crystallized,
    }
