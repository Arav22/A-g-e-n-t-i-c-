#!/usr/bin/env bash
set -euo pipefail

PROMPT=${1:-"Count words in: hello world from shell"}
python -m agentic_ai --prompt "$PROMPT"
