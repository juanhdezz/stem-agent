from __future__ import annotations

import json
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


def run_agent_on_sample(config: AgentConfig, sample: dict) -> List[str]:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    system_message = SystemMessage(content=config.system_prompt)
    tool_summary = _summarize_tools(config, sample["code"])

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
            return [str(item) for item in parsed]
    except Exception:
        pass

    issues: List[str] = []
    for line in response.content.splitlines():
        stripped = line.strip().lstrip("- ").strip()
        if stripped:
            issues.append(stripped)
    return issues


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
