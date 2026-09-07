from __future__ import annotations

import time
from typing import Any, Awaitable, Callable, Mapping

from .recorder import AgentRecorder


async def capture_async_tool(
    recorder: AgentRecorder,
    name: str,
    request: Mapping[str, Any],
    func: Callable[[], Awaitable[Mapping[str, Any]]],
    *,
    requires_permission: bool = False,
) -> Mapping[str, Any]:
    started = time.perf_counter()
    try:
        response = await func()
    except Exception as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        recorder.tool_call(
            name,
            request,
            {"error_type": type(exc).__name__, "message": str(exc)},
            status="error",
            duration_ms=duration_ms,
            requires_permission=requires_permission,
        )
        raise
    duration_ms = int((time.perf_counter() - started) * 1000)
    recorder.tool_call(name, request, dict(response), duration_ms=duration_ms, requires_permission=requires_permission)
    return response
