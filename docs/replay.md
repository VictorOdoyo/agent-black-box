# Replay

Replay reads recorded tool-call events and returns their captured responses in order. This lets tests verify how an agent behaves when live tools are replaced by trace-backed mocks.

Replay is intentionally deterministic. It does not claim to reproduce hidden model reasoning or external services.
