from __future__ import annotations

from typing import List, Optional, TypedDict

from src.models.agent_config import AgentConfig
from src.models.eval_result import EvalResult


class StemAgentState(TypedDict):
    task_class: str
    discovered_knowledge: List[str]
    current_config: AgentConfig
    iteration: int
    eval_results: List[EvalResult]
    current_score: float
    final_config: Optional[AgentConfig]
    is_crystallized: bool
