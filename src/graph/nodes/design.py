from __future__ import annotations

import json

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

from src.graph.state import StemAgentState
from src.models.agent_config import AgentConfig, FlowStep, ToolSpec
from src.tools.prompt_generator import generate_system_prompt


SYSTEM_PROMPT = (
    "You are an expert agent designer. "
    "Generate a JSON configuration for a specialized QA/code-review agent."
)


def _default_config(system_prompt: str) -> AgentConfig:
    tools = [
        ToolSpec(name="web_search", description="Search for best practices or known bug patterns."),
        ToolSpec(name="code_analysis", description="Analyze Python code for structure and smells."),
    ]
    flow = [
        FlowStep(name="quick_scan", instructions="Scan code for obvious logic, security, and style issues."),
        FlowStep(name="deep_review", instructions="Apply checklists and compare with expected bug patterns."),
        FlowStep(name="report", instructions="Return concise issue list with categories."),
    ]
    return AgentConfig(system_prompt=system_prompt, tools=tools, flow=flow, version=1)


def _parse_config(raw: str, fallback_prompt: str) -> AgentConfig:
    try:
        data = json.loads(raw)
        tools = [ToolSpec(**tool) for tool in data.get("tools", [])]
        flow = [FlowStep(**step) for step in data.get("flow", [])]
        return AgentConfig(
            system_prompt=data.get("system_prompt", fallback_prompt),
            tools=tools or _default_config(fallback_prompt).tools,
            flow=flow or _default_config(fallback_prompt).flow,
            version=int(data.get("version", 1)),
        )
    except Exception:
        return _default_config(fallback_prompt)


def design_node(state: StemAgentState) -> dict:
    knowledge = state.get("discovered_knowledge", [])
    iteration = state.get("iteration", 0)
    previous_score = state.get("current_score")
    previous_config = state.get("current_config")

    system_prompt_seed = generate_system_prompt(
        task_class=state["task_class"],
        knowledge=knowledge,
        previous_score=previous_score if iteration > 0 else None,
        previous_config=previous_config if iteration > 0 else None,
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                "Generate JSON with keys: system_prompt, tools, flow, version.\n"
                "tools is a list of {name, description, enabled}.\n"
                "flow is a list of {name, instructions}.\n"
                f"Seed prompt:\n{system_prompt_seed}"
            )
        ),
    ]
    response = llm.invoke(messages)
    config = _parse_config(response.content, system_prompt_seed)

    return {
        "current_config": config,
        "iteration": iteration + 1,
    }
