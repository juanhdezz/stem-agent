from __future__ import annotations

from typing import List, Optional

from src.models.agent_config import AgentConfig


def generate_system_prompt(
    task_class: str,
    knowledge: List[str],
    previous_score: Optional[float] = None,
    previous_config: Optional[AgentConfig] = None,
) -> str:
    knowledge_block = "\n".join(f"- {item}" for item in knowledge) or "- No external knowledge yet"
    prompt = (
        "You are a specialist system prompt designer. "
        f"Create a system prompt for an agent specializing in {task_class}.\n\n"
        "Expert knowledge discovered:\n"
        f"{knowledge_block}\n\n"
    )
    if previous_score is not None and previous_config is not None:
        prompt += (
            f"Previous score: {previous_score:.3f}.\n"
            "Improve the previous system prompt with concrete changes to increase precision and recall.\n"
            "Previous system prompt:\n"
            f"{previous_config.system_prompt}\n"
        )
    prompt += "Return only the improved system prompt text."
    return prompt
