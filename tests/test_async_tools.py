import asyncio

from agent_black_box import AgentRecorder
from agent_black_box.async_tools import capture_async_tool


def test_async_tool_capture():
    async def run():
        async def tool():
            return {"ok": True}

        with AgentRecorder("demo") as recorder:
            response = await capture_async_tool(recorder, "async_lookup", {}, tool)
        return response, recorder.trace.tools()[0].payload["name"]

    assert asyncio.run(run()) == ({"ok": True}, "async_lookup")
