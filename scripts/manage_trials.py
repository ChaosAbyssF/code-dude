#!/usr/bin/env python3
"""Summarize experiment directories and optionally emit a cleanup plan."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Parent directory that contains experiment runs.")
    parser.add_argument(
        "--threshold",
        type=int,
        default=15,
        help="Cleanup threshold after which old runs should be reviewed.",
    )
    parser.add_argument(
        "--keep-recent",
        type=int,
        default=5,
        help="How many recent run directories to keep by default.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of markdown.",
    )
    return parser.parse_args()


def list_run_dirs(root: Path) -> list[Path]:
    return sorted(
        [item for item in root.iterdir() if item.is_dir()],
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )


def iso_time(path: Path) -> str:
    mtime = path.stat().st_mtime
    return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()


def main() -> int:
    args = parse_args()
    root = Path(args.path).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"not a directory: {root}")

    runs = list_run_dirs(root)
    keep = runs[: args.keep_recent]
    candidates = runs[args.keep_recent :]
    review_needed = len(runs) >= args.threshold

    data = {
        "root": str(root),
        "total_runs": len(runs),
        "cleanup_threshold": args.threshold,
        "review_needed": review_needed,
        "keep_recent": [str(item) for item in keep],
        "cleanup_candidates": [str(item) for item in candidates],
        "runs": [{"name": item.name, "path": str(item), "modified_utc": iso_time(item)} for item in runs],
    }

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=True))
        return 0

    print(f"# Trial Summary for {root.name}")
    print()
    print(f"- Total runs: {len(runs)}")
    print(f"- Cleanup threshold: {args.threshold}")
    print(f"- Review needed: {'yes' if review_needed else 'no'}")
    print(f"- Suggested keep count: {args.keep_recent}")
    print()
    print("## Keep")
    if keep:
        for item in keep:
            print(f"- {item.name}")
    else:
        print("- None")
    print()
    print("## Cleanup Candidates")
    if candidates:
        for item in candidates:
            print(f"- {item.name}")
    else:
        print("- None")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
