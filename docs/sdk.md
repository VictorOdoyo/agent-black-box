# Python SDK

Use `AgentRecorder` as a context manager. It records lifecycle events automatically and exposes helpers for observations, decisions, permissions, tool calls, environment changes, artifacts, and errors.

```python
from agent_black_box import AgentRecorder

with AgentRecorder("support-agent") as recorder:
    recorder.observation("User reported failed checkout")
    recorder.decision("Check payment logs", "The error mentioned provider timeout.")
```
