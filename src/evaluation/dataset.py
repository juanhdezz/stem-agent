from __future__ import annotations

import json
from typing import List, Dict, Any


Sample = Dict[str, Any]


def load_dataset(path: str) -> List[Sample]:
    dataset: List[Sample] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            data = json.loads(line)
            dataset.append(
                {
                    "code": data["code"],
                    "expected_issues": data.get("expected_issues", []),
                    "metadata": data.get("metadata", {}),
                }
            )
    return dataset
