# Contributing

Contributions should include tests for behavior changes and fixture updates when the trace format changes.

## Development flow

1. Install dependencies with `python -m pip install -e ".[dev]"` and `pnpm install`.
2. Add or update Python tests under `tests/`.
3. Add or update viewer tests under `apps/viewer/src/`.
4. Run `python -m pytest`, `pnpm --dir apps/viewer exec vitest run`, and `pnpm --dir apps/viewer build`.
