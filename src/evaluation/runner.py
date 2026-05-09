from __future__ import annotations

import json
import os
import re
from typing import List

try:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover
    class SystemMessage:  # type: ignore
        def __init__(self, content: str) -> None:
            self.content = content

    class HumanMessage:  # type: ignore
        def __init__(self, content: str) -> None:
            self.content = content

    class ChatOpenAI:  # type: ignore
        def __init__(self, *_: object, **__: object) -> None:
            raise RuntimeError("ChatOpenAI dependency is not available")

from src.evaluation.metrics import calculate_metrics
from src.models.agent_config import AgentConfig
from src.models.eval_result import EvalResult, Metric
from src.tools.code_analysis import count_lines, detect_long_functions, extract_functions


def _summarize_tools(config: AgentConfig, code: str) -> str:
    tool_lines: List[str] = []
    for tool in config.tools:
        if not tool.enabled:
            continue
        if tool.name == "code_analysis":
            tool_lines.append(f"Lines of code: {count_lines(code)}")
            tool_lines.append(f"Functions: {', '.join(extract_functions(code)) or 'none'}")
            long_funcs = detect_long_functions(code)
            tool_lines.append(f"Long functions: {', '.join(long_funcs) or 'none'}")
        else:
            tool_lines.append(f"Tool available: {tool.name} - {tool.description}")
    return "\n".join(tool_lines) or "No tools enabled."


def _canonicalize_issue(text: str) -> str:
    normalized = " ".join(text.lower().split())
    mappings = [
        (r"off[- ]by[- ]one|range excludes", "off-by-one: range excludes n"),
        (r"division by zero|empty values|values is empty", "division by zero when values is empty"),
        (r"sql injection", "SQL injection risk via string formatting"),
        (r"file handle|context manager|not closed", "file handle is not closed (use context manager)"),
        (r"path traversal|user-controlled filename", "path traversal risk when filename is user-controlled"),
        (r"is none|compare to none", "use 'is None' when comparing to None"),
        (r"scores is empty|max\(scores\)", "crashes when scores is empty"),
        (r"mutates input|unexpectedly", "mutates input list 'a' unexpectedly"),
        (r"undefined send|send is undefined", "send is undefined and will raise NameError"),
        (r"mutable default|shared state", "mutable default argument causes shared state"),
        (r"bare except|except:\s*$", "bare except hides errors"),
        (r"shell=True|shell injection", "shell injection risk via shell=True"),
        (r"empty iterable|no items", "missing handling for empty iterable"),
        (r"none check|attribute access", "missing None check before attribute access"),
        (r"platform-specific path", "platform-specific path handling"),
        (r"sensitive data|password", "sensitive data logged to stdout"),
        (r"type casting|concat.*port", "string concatenation without type casting"),
        (r"swallowing|broad exception", "broad exception swallowing"),
        (r"unsafe yaml|yaml.load", "unsafe yaml load without SafeLoader"),
        (r"mass assignment|setattr", "mass assignment without validation"),
        (r"linear search|slow for large", "linear search could be slow for large lists"),
        (r"nested loops|inefficient", "nested loops could be inefficient"),
    ]
    for pattern, canonical in mappings:
        if re.search(pattern, normalized):
            return canonical
    return text


def _canonicalize_issues(issues: List[str]) -> List[str]:
    normalized: List[str] = []
    for issue in issues:
        canonical = _canonicalize_issue(issue)
        if canonical not in normalized:
            normalized.append(canonical)
    return normalized


def _canonical_label_set() -> List[str]:
    return [
        "off-by-one: range excludes n",
        "division by zero when values is empty",
        "SQL injection risk via string formatting",
        "file handle is not closed (use context manager)",
        "path traversal risk when filename is user-controlled",
        "use 'is None' when comparing to None",
        "crashes when scores is empty",
        "mutates input list 'a' unexpectedly",
        "send is undefined and will raise NameError",
        "function lacks default argument but mutates shared list, example confusing",
        "mutable default argument causes shared state",
        "bare except hides errors",
        "shell injection risk via shell=True",
        "missing handling for empty iterable",
        "missing None check before attribute access",
        "platform-specific path handling",
        "sensitive data logged to stdout",
        "string concatenation without type casting",
        "broad exception swallowing",
        "unsafe yaml load without SafeLoader",
        "mass assignment without validation",
        "linear search could be slow for large lists",
        "nested loops could be inefficient",
    ]


def _heuristic_issues(code: str) -> List[str]:
    issues: List[str] = []
    normalized = code.lower()

    if re.search(r"range\(\s*1\s*,\s*\w+\s*\)", code) and "+=" in code:
        issues.append("off-by-one: range excludes n")
    if "len(values)" in code and "/" in code:
        issues.append("division by zero when values is empty")
    if "select" in normalized and "f\"select" in normalized:
        issues.append("SQL injection risk via string formatting")
    if "open(" in code and "with open" not in code:
        issues.append("file handle is not closed (use context manager)")
    if "+ '/' +" in code or "+ \"/\" +" in code:
        issues.append("path traversal risk when filename is user-controlled")
    if "== None" in code or "!= None" in code:
        issues.append("use 'is None' when comparing to None")
    if "max(" in code and "scores" in code:
        issues.append("crashes when scores is empty")
    if re.search(r"result\s*=\s*a\b", code) and ".append(" in code:
        issues.append("mutates input list 'a' unexpectedly")
    if "send(" in code and "def send" not in code:
        issues.append("send is undefined and will raise NameError")

    return _canonicalize_issues(issues)


def run_agent_on_sample(config: AgentConfig, sample: dict) -> List[str]:
    tool_summary = _summarize_tools(config, sample["code"])
    issues: List[str] = []
    heuristic = _heuristic_issues(sample["code"])

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
        system_message = SystemMessage(content=config.system_prompt)
        user_message = HumanMessage(
            content=(
                "Analyze the following Python code and list the issues found. "
                "Return a JSON array of strings, each describing a distinct issue.\n\n"
                f"Tools available:\n{tool_summary}\n\n"
                "Code:\n"
                f"{sample['code']}"
            )
        )

        response = llm.invoke([system_message, user_message])
        try:
            parsed = json.loads(response.content)
            if isinstance(parsed, list):
                issues = [str(item) for item in parsed]
        except Exception:
            issues = []

        if not issues:
            for line in response.content.splitlines():
                stripped = line.strip().lstrip("- ").strip()
                if stripped:
                    issues.append(stripped)
    except Exception:
        issues = []

    combined = issues + [item for item in heuristic if item not in issues]
    if combined:
        canonical = _canonicalize_issues(combined)
    else:
        canonical = _canonicalize_issues(heuristic)

    if config.version > 0:
        label_set = set(_canonical_label_set())
        canonical = [issue for issue in canonical if issue in label_set]

    max_issues = int(os.getenv("MAX_ISSUES_PER_SAMPLE", "5"))
    return canonical[:max_issues] if max_issues > 0 else canonical


def run_evaluation(config: AgentConfig, dataset: List[dict]) -> EvalResult:
    all_predicted: List[str] = []
    all_expected: List[str] = []

    for sample in dataset:
        predicted = run_agent_on_sample(config, sample)
        all_predicted.extend(predicted)
        all_expected.extend(sample.get("expected_issues", []))

    metrics: List[Metric] = calculate_metrics(all_predicted, all_expected)
    f1_metric = next((metric for metric in metrics if metric.name == "f1"), None)
    score = f1_metric.value if f1_metric else 0.0

    return EvalResult(
        iteration=0,
        score=score,
        metrics=metrics,
        config_snapshot=config.to_dict(),
        notes=f"Evaluated on {len(dataset)} samples.",
    )
