from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ToolSpec:
    name: str
    description: str
    enabled: bool = True


@dataclass
class FlowStep:
    name: str
    instructions: str


@dataclass
class AgentConfig:
    system_prompt: str
    tools: List[ToolSpec]
    flow: List[FlowStep]
    version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "system_prompt": self.system_prompt,
            "tools": [tool.__dict__ for tool in self.tools],
            "flow": [step.__dict__ for step in self.flow],
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentConfig":
        tools = [ToolSpec(**tool) for tool in data.get("tools", [])]
        flow = [FlowStep(**step) for step in data.get("flow", [])]
        return cls(
            system_prompt=data.get("system_prompt", ""),
            tools=tools,
            flow=flow,
            version=int(data.get("version", 1)),
        )
