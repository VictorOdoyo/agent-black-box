from __future__ import annotations

from dataclasses import dataclass

from .models import TraceEnvelope


@dataclass
class TraceComparison:
    left_run_id: str
    right_run_id: str
    left_events: int
    right_events: int
    first_divergence_index: int | None
    added_tool_calls: list[str]
    removed_tool_calls: list[str]
    summary_changes: list[str]

    def to_markdown(self) -> str:
        lines = [
            f"# Trace comparison: {self.left_run_id} vs {self.right_run_id}",
            "",
            f"- Events: {self.left_events} vs {self.right_events}",
            f"- First divergence: {self.first_divergence_index if self.first_divergence_index is not None else 'none'}",
            f"- Added tool calls: {', '.join(self.added_tool_calls) or 'none'}",
            f"- Removed tool calls: {', '.join(self.removed_tool_calls) or 'none'}",
        ]
        if self.summary_changes:
            lines.append("")
            lines.extend(f"- {change}" for change in self.summary_changes)
        return "\n".join(lines) + "\n"


def compare_traces(left: TraceEnvelope, right: TraceEnvelope) -> TraceComparison:
    first_divergence: int | None = None
    summary_changes: list[str] = []
    for index, pair in enumerate(zip(left.events, right.events)):
        left_event, right_event = pair
        if left_event.kind != right_event.kind or left_event.summary != right_event.summary:
            first_divergence = index
            summary_changes.append(f"event {index}: {left_event.kind}/{left_event.summary} -> {right_event.kind}/{right_event.summary}")
            break
    if first_divergence is None and len(left.events) != len(right.events):
        first_divergence = min(len(left.events), len(right.events))

    left_tools = [event.payload.get("name", "") for event in left.tools()]
    right_tools = [event.payload.get("name", "") for event in right.tools()]
    return TraceComparison(
        left_run_id=left.run_id,
        right_run_id=right.run_id,
        left_events=len(left.events),
        right_events=len(right.events),
        first_divergence_index=first_divergence,
        added_tool_calls=[tool for tool in right_tools if tool not in left_tools],
        removed_tool_calls=[tool for tool in left_tools if tool not in right_tools],
        summary_changes=summary_changes,
    )
