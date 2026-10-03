from __future__ import annotations

try:
    from langgraph.graph import StateGraph, END, START
    from langgraph.graph.state import CompiledStateGraph as CompiledGraph
except ImportError:  # pragma: no cover
    START = "__start__"
    END = "__end__"

    class CompiledGraph:  # type: ignore
        def __init__(self, runner):
            self._runner = runner

        def invoke(self, state):
            return self._runner(state)

    class StateGraph:  # type: ignore
        def __init__(self, _state_type):
            self._nodes = {}
            self._edges = {}
            self._conditionals = {}

        def add_node(self, name, fn):
            self._nodes[name] = fn

        def add_edge(self, start, end):
            self._edges.setdefault(start, []).append(end)

        def add_conditional_edges(self, name, condition, mapping):
            self._conditionals[name] = (condition, mapping)

        def compile(self):
            def _next_node(current, state):
                if current in self._conditionals:
                    condition, mapping = self._conditionals[current]
                    key = condition(state)
                    return mapping.get(key)
                edges = self._edges.get(current, [])
                return edges[0] if edges else END

            def _runner(state):
                current = START
                while current != END:
                    next_node = _next_node(current, state)
                    if next_node == END:
                        return state
                    state.update(self._nodes[next_node](state))
                    current = next_node
                return state

            return CompiledGraph(_runner)

from src.graph.nodes.crystallization import crystallization_node
from src.graph.nodes.design import design_node
from src.graph.nodes.discovery import discovery_node
from src.graph.nodes.validation import validation_node
from src.graph.state import StemAgentState


def build_graph() -> CompiledGraph:
    graph = StateGraph(StemAgentState)

    graph.add_node("discovery", discovery_node)
    graph.add_node("design", design_node)
    graph.add_node("validation", validation_node)
    graph.add_node("crystallization", crystallization_node)

    graph.add_edge(START, "discovery")
    graph.add_edge("discovery", "design")
    graph.add_edge("design", "validation")

    graph.add_conditional_edges(
        "validation",
        lambda state: "crystallization" if state.get("is_crystallized") else "design",
        {
            "crystallization": "crystallization",
            "design": "design",
        },
    )

    graph.add_edge("crystallization", END)

    return graph.compile()
