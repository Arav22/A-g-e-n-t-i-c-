# Agentic AI Scaffold

A minimal, layered Python project scaffold for building agentic workflows.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
make run PROMPT="Summarize today's todos"
```

Or run directly:

```bash
python -m agentic_ai --prompt "Count words in: hello from agentic ai"
```

## Architecture

```text
User Prompt
   |
   v
api.main -> orchestrator.core
              |      |      \
              |      |       -> providers.simple_provider (LLM/provider abstraction)
              |      -> tools.registry + tools.word_count (tool execution)
              -> memory.store (session history)

observability.logging is used across layers for structured logs.
```

## Project Layout

- `src/agentic_ai/main.py` — CLI entrypoint logic.
- `src/agentic_ai/orchestrator/` — workflow orchestration.
- `src/agentic_ai/tools/` — tool registration + implementations.
- `src/agentic_ai/memory/` — in-memory conversation history.
- `src/agentic_ai/providers/` — provider abstraction/stub.
- `src/agentic_ai/observability/` — logger configuration.
- `src/agentic_ai/api/` — request/response models and app-level service.
