from __future__ import annotations

from xml.sax.saxutils import escape

from .causality import build_causal_edges
from .models import TraceEnvelope


def trace_to_dot(trace: TraceEnvelope) -> str:
    lines = ["digraph trace {", "  rankdir=LR;"]
    for event in trace.events:
        label = escape(f"{event.kind}\\n{event.summary}")
        lines.append(f'  "{event.id}" [label="{label}"];')
    for edge in build_causal_edges(trace):
        lines.append(f'  "{edge.source}" -> "{edge.target}" [label="{escape(edge.reason)}"];')
    lines.append("}")
    return "\n".join(lines) + "\n"
