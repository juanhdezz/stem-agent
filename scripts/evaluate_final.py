from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.evaluation.dataset import load_dataset
from src.evaluation.runner import run_evaluation
from src.models.agent_config import AgentConfig


def _load_config(path: str) -> AgentConfig:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return AgentConfig.from_dict(data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a crystallized agent configuration.")
    parser.add_argument("--config", required=True, help="Path to agent_config.json")
    args = parser.parse_args()

    load_dotenv()
    dataset_path = os.getenv("EVAL_DATASET_PATH", "data/benchmark/samples.jsonl")
    dataset = load_dataset(dataset_path)

    config = _load_config(args.config)
    result = run_evaluation(config, dataset)

    baseline_path = Path("data/outputs/baseline_results.json")
    baseline = None
    if baseline_path.exists():
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))

    print("\nFinal evaluation:")
    for metric in result.metrics:
        print(f"- {metric.name}: {metric.value:.3f}")

    if baseline:
        print("\nBaseline comparison:")
        for metric in baseline.get("metrics", []):
            print(f"- {metric['name']}: {metric['value']:.3f}")


if __name__ == "__main__":
    main()
