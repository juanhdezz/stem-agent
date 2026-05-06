from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.evaluation.dataset import load_dataset
from src.evaluation.runner import run_evaluation
from src.models.agent_config import AgentConfig, FlowStep, ToolSpec


def main() -> None:
    load_dotenv()
    dataset_path = os.getenv("EVAL_DATASET_PATH", "data/benchmark/samples.jsonl")
    dataset = load_dataset(dataset_path)

    baseline_config = AgentConfig(
        system_prompt=(
            "You are a helpful code reviewer. Find bugs, security issues, and style problems in Python code."
        ),
        tools=[ToolSpec(name="code_analysis", description="Analyze basic structure."),],
        flow=[FlowStep(name="review", instructions="Review code and list issues."),],
        version=0,
    )

    result = run_evaluation(baseline_config, dataset)
    output_dir = Path("data/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "baseline_results.json"

    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "score": result.score,
                "metrics": [metric.__dict__ for metric in result.metrics],
                "notes": result.notes,
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )

    print("Baseline evaluation saved to", output_path)


if __name__ == "__main__":
    main()
