from __future__ import annotations

import json
from pathlib import Path

from src.graph.state import StemAgentState


def crystallization_node(state: StemAgentState) -> dict:
    output_dir = Path("data/outputs/latest")
    output_dir.mkdir(parents=True, exist_ok=True)

    config = state["current_config"]
    config_path = output_dir / "agent_config.json"
    prompt_path = output_dir / "system_prompt.txt"

    with config_path.open("w", encoding="utf-8") as handle:
        json.dump(config.to_dict(), handle, ensure_ascii=False, indent=2)

    with prompt_path.open("w", encoding="utf-8") as handle:
        handle.write(config.system_prompt)

    print(
        "\n".join(
            [
                "Crystallization summary:",
                f"Iterations: {state.get('iteration', 0)}",
                f"Final score: {state.get('current_score', 0.0):.3f}",
                "Tools: " + ", ".join(tool.name for tool in config.tools if tool.enabled),
            ]
        )
    )

    return {"final_config": config}
