from __future__ import annotations

from typing import List


def count_lines(code: str) -> int:
    return len([line for line in code.splitlines() if line.strip()])


def extract_functions(code: str) -> List[str]:
    functions: List[str] = []
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("def ") and stripped.endswith(":"):
            name = stripped[4:stripped.index("(")].strip()
            functions.append(name)
    return functions


def detect_long_functions(code: str, threshold: int = 50) -> List[str]:
    lines = code.splitlines()
    long_functions: List[str] = []
    current_name = None
    current_count = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("def ") and stripped.endswith(":"):
            if current_name and current_count > threshold:
                long_functions.append(current_name)
            current_name = stripped[4:stripped.index("(")].strip()
            current_count = 0
            continue
        if current_name:
            if stripped:
                current_count += 1
    if current_name and current_count > threshold:
        long_functions.append(current_name)
    return long_functions
