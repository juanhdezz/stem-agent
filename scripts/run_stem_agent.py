from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.graph.graph import build_graph
from src.models.agent_config import AgentConfig


def _initial_state(task_class: str) -> dict[str, Any]:
    placeholder_config = AgentConfig(system_prompt="", tools=[], flow=[], version=0)
    return {
        "task_class": task_class,
        "discovered_knowledge": [],
        "current_config": placeholder_config,
        "iteration": 0,
        "eval_results": [],
        "current_score": 0.0,
        "final_config": None,
        "is_crystallized": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the StemAgent specialization graph.")
    parser.add_argument("--task-class", default="code_review", help="Problem class for specialization")
    args = parser.parse_args()

    load_dotenv()
    graph = build_graph()
    result = graph.invoke(_initial_state(args.task_class))
    final_config = result.get("final_config")
    if final_config:
        print("Final agent ready. Config version:", final_config.version)


if __name__ == "__main__":
    main()
