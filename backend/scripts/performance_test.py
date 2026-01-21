"""
Simple performance test runner for the Prompt Search API.
"""

import argparse
import json
import statistics
import time
from typing import Dict, List, Tuple
from urllib import error as urlerror
from urllib import request as urlrequest


def _post_json(url: str, payload: Dict[str, object]) -> Tuple[float, Dict[str, object]]:
    data = json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.perf_counter()
    with urlrequest.urlopen(req, timeout=30) as response:
        body = response.read().decode("utf-8")
    elapsed = time.perf_counter() - start
    return elapsed, json.loads(body)


def _summarize(times: List[float]) -> Dict[str, float]:
    ordered = sorted(times)
    p95_index = max(0, int(round(0.95 * (len(ordered) - 1))))
    return {
        "avg_ms": statistics.mean(ordered) * 1000,
        "median_ms": statistics.median(ordered) * 1000,
        "p95_ms": ordered[p95_index] * 1000,
    }


def _run_trials(
    base_url: str,
    label: str,
    payload: Dict[str, object],
    runs: int,
) -> Dict[str, float]:
    endpoint = f"{base_url.rstrip('/')}/api/search"
    timings: List[float] = []
    for _ in range(runs):
        elapsed, _ = _post_json(endpoint, payload)
        timings.append(elapsed)
    summary = _summarize(timings)
    summary["runs"] = runs
    return summary


def _run_toggle_trials(
    base_url: str,
    initial_payload: Dict[str, object],
    toggle_payload: Dict[str, object],
    runs: int,
) -> Dict[str, float]:
    endpoint = f"{base_url.rstrip('/')}/api/search"
    timings: List[float] = []
    for _ in range(runs):
        _post_json(endpoint, initial_payload)
        elapsed, _ = _post_json(endpoint, toggle_payload)
        timings.append(elapsed)
    summary = _summarize(timings)
    summary["runs"] = runs
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Prompt Search performance test.")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL for the API (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of runs per scenario (default: 5)",
    )
    args = parser.parse_args()

    try:
        _post_json(
            f"{args.base_url.rstrip('/')}/api/search",
            {"query": "warm up", "top_k": 5},
        )
    except urlerror.URLError as exc:
        raise SystemExit(f"Failed to reach API at {args.base_url}: {exc}") from exc

    english_payload = {
        "query": "relaxing piano music",
        "top_k": 20,
    }
    non_english_payload = {
        "query": "música relajante para yoga",
        "top_k": 20,
    }
    toggle_initial = {
        "query": "dramatic explosion",
        "top_k": 20,
        "content_type": "sfx",
    }
    toggle_target = {
        "query": "dramatic explosion",
        "top_k": 20,
        "content_type": "song",
    }

    english_summary = _run_trials(args.base_url, "english", english_payload, args.runs)
    non_english_summary = _run_trials(
        args.base_url, "non_english", non_english_payload, args.runs
    )
    toggle_summary = _run_toggle_trials(
        args.base_url, toggle_initial, toggle_target, args.runs
    )

    results = {
        "english_query": english_summary,
        "non_english_query": non_english_summary,
        "toggle_research": toggle_summary,
    }

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
