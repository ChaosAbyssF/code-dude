#!/usr/bin/env python3
"""Heuristically inspect a verification entrypoint for per-run artifact handling."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


POSITIVE_PATTERNS = [
    r"Try\d+",
    r"trial",
    r"experiment",
    r"output[_-]?dir",
    r"save[_-]?dir",
    r"artifact",
    r"run[_-]?name",
    r"exp[_-]?name",
    r"mkdir",
]

NEGATIVE_PATTERNS = [
    r"rm\s+-rf",
    r"overwrite",
    r">",
    r"tee\s+\S+$",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Path to the verification entrypoint.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.path).resolve()
    if not path.exists():
        print(json.dumps({"ok": False, "error": f"file not found: {path}"}))
        return 1

    content = path.read_text(encoding="utf-8", errors="ignore")
    lowered = content.lower()

    positives = [pattern for pattern in POSITIVE_PATTERNS if re.search(pattern, content, re.IGNORECASE)]
    negatives = [pattern for pattern in NEGATIVE_PATTERNS if re.search(pattern, lowered, re.IGNORECASE)]

    likely_isolated = len(positives) >= 2 and not negatives
    result = {
        "ok": True,
        "path": str(path),
        "likely_supports_isolated_runs": likely_isolated,
        "positive_signals": positives,
        "risk_signals": negatives,
        "note": "Heuristic only; inspect the verifier directly before relying on this result.",
    }
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
