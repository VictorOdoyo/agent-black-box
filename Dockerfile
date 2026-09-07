FROM python:3.13-slim AS python-checks
WORKDIR /app
COPY pyproject.toml README.md ./
COPY packages ./packages
COPY tests ./tests
RUN python -m pip install -e ".[dev]"
RUN python -m pytest

FROM node:20-bookworm-slim AS viewer
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@9.15.9 --activate
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/viewer ./apps/viewer
RUN pnpm install --frozen-lockfile
RUN pnpm --dir apps/viewer build
