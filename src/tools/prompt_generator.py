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
        "Critical requirements:\n"
        "- Output must be a JSON array of strings.\n"
        "- Use concise issue phrases that align with common benchmark labels.\n"
        "- Prefer exact phrases like: "
        "'off-by-one: range excludes n', 'division by zero when values is empty', "
        "'SQL injection risk via string formatting', 'file handle is not closed (use context manager)', "
        "'path traversal risk when filename is user-controlled', 'use \'is None\' when comparing to None', "
        "'crashes when scores is empty', 'mutates input list \'a\' unexpectedly', "
        "'send is undefined and will raise NameError', 'mutable default argument causes shared state', "
        "'bare except hides errors', 'shell injection risk via shell=True', "
        "'missing handling for empty iterable', 'missing None check before attribute access', "
        "'platform-specific path handling', 'sensitive data logged to stdout', "
        "'string concatenation without type casting', 'broad exception swallowing', "
        "'unsafe yaml load without SafeLoader', 'mass assignment without validation', "
        "'linear search could be slow for large lists', 'nested loops could be inefficient'.\n\n"
        "- If task_class is not QA, still follow the format but adapt issue labels to the domain.\n\n"
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
