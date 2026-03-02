from __future__ import annotations

import argparse
import json

from agentic_ai.api import OrchestratorAPI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the agentic orchestration engine")
    parser.add_argument("objective", nargs="?", help="Objective to orchestrate")
    parser.add_argument("--run-dir", default=".runs", help="Directory for persisted run state")
    parser.add_argument("--resume", help="Existing run ID to resume")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    api = OrchestratorAPI(run_dir=args.run_dir)

    if args.resume:
        result = api.resume(args.resume)
    elif args.objective:
        result = api.run(args.objective)
    else:
        raise SystemExit("Provide an objective or --resume run_id")

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
