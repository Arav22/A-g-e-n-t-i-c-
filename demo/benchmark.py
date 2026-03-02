#!/usr/bin/env python3
"""Simple benchmark harness for agent demo use cases.

Usage:
  python demo/benchmark.py --runs 5
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CaseResult:
    name: str
    latency_s: float
    success: bool
    retries: int


def simulate_agent_call(case_name: str, max_retries: int = 2) -> CaseResult:
    """Simulate one agent run with retriable failures.

    Replace this function with a real model invocation when integrating.
    """
    start = time.perf_counter()
    retries = 0

    while True:
        # Simulate network/model latency
        time.sleep(random.uniform(0.08, 0.22))
        transient_failure = random.random() < 0.12
        quality_failure = random.random() < 0.08

        if transient_failure and retries < max_retries:
            retries += 1
            continue

        success = not transient_failure and not quality_failure
        latency_s = time.perf_counter() - start
        return CaseResult(case_name, latency_s, success, retries)


def run_benchmark(runs: int, seed: int) -> dict:
    random.seed(seed)
    cases = [
        "incident-triage",
        "research-assistant",
        "workflow-automation",
    ]

    results: list[CaseResult] = []
    for _ in range(runs):
        for case in cases:
            results.append(simulate_agent_call(case))

    latencies = [r.latency_s for r in results]
    success_rate = sum(r.success for r in results) / len(results)
    retries = [r.retries for r in results]

    return {
        "total_runs": len(results),
        "latency_avg_s": round(statistics.mean(latencies), 4),
        "latency_p95_s": round(sorted(latencies)[int(0.95 * len(latencies)) - 1], 4),
        "success_rate": round(success_rate, 4),
        "retry_avg": round(statistics.mean(retries), 4),
        "retry_max": max(retries),
        "by_case": {
            case: {
                "success_rate": round(
                    sum(r.success for r in results if r.name == case)
                    / sum(1 for r in results if r.name == case),
                    4,
                ),
                "latency_avg_s": round(
                    statistics.mean(r.latency_s for r in results if r.name == case),
                    4,
                ),
            }
            for case in cases
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=5, help="Runs per use case")
    parser.add_argument("--seed", type=int, default=7, help="Random seed")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("demo/traces/benchmark-report.json"),
        help="Where to write JSON report",
    )
    args = parser.parse_args()

    report = run_benchmark(args.runs, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Benchmark complete")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
