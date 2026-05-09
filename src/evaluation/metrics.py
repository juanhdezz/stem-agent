from __future__ import annotations

import re
from typing import List, Tuple

from src.models.eval_result import Metric


_STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "to",
    "of",
    "for",
    "is",
    "when",
    "with",
    "via",
    "be",
    "will",
    "not",
}


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _tokens(text: str) -> List[str]:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", _normalize(text))
    return [token for token in cleaned.split() if token and token not in _STOPWORDS]


def _is_match(predicted: str, expected: str) -> bool:
    p = _normalize(predicted)
    e = _normalize(expected)
    if e in p or p in e:
        return True
    p_tokens = set(_tokens(p))
    e_tokens = set(_tokens(e))
    if not p_tokens or not e_tokens:
        return False
    overlap = len(p_tokens & e_tokens)
    return overlap / max(len(e_tokens), 1) >= 0.6


def _count_matches(predicted: List[str], expected: List[str]) -> Tuple[int, int, int]:
    matched_expected = set()
    true_positive = 0
    for pred in predicted:
        for idx, exp in enumerate(expected):
            if idx in matched_expected:
                continue
            if _is_match(pred, exp):
                true_positive += 1
                matched_expected.add(idx)
                break
    false_positive = max(0, len(predicted) - true_positive)
    false_negative = max(0, len(expected) - len(matched_expected))
    return true_positive, false_positive, false_negative


def calculate_precision(predicted: List[str], expected: List[str]) -> float:
    tp, fp, _ = _count_matches(predicted, expected)
    return tp / (tp + fp) if (tp + fp) > 0 else 0.0


def calculate_recall(predicted: List[str], expected: List[str]) -> float:
    tp, _, fn = _count_matches(predicted, expected)
    return tp / (tp + fn) if (tp + fn) > 0 else 0.0


def calculate_f1(predicted: List[str], expected: List[str]) -> float:
    precision = calculate_precision(predicted, expected)
    recall = calculate_recall(predicted, expected)
    return (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0


def calculate_metrics(predicted: List[str], expected: List[str]) -> List[Metric]:
    precision = calculate_precision(predicted, expected)
    recall = calculate_recall(predicted, expected)
    f1 = calculate_f1(predicted, expected)
    return [
        Metric(name="precision", value=precision, description="Fraction of reported issues that are correct."),
        Metric(name="recall", value=recall, description="Fraction of expected issues that were found."),
        Metric(name="f1", value=f1, description="Harmonic mean of precision and recall."),
    ]
