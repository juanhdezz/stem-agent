from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Metric:
    name: str
    value: float
    description: str


@dataclass
class EvalResult:
    iteration: int
    score: float
    metrics: List[Metric]
    config_snapshot: Dict[str, Any]
    notes: str

    def is_above_threshold(self, threshold: float) -> bool:
        return self.score >= threshold
