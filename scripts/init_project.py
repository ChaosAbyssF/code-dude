#!/usr/bin/env python3
"""Initialize a project-local .code-dude workspace from the bundled template."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Target repository root.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files when they conflict.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    template_root = script_dir.parent / "assets" / "project-template" / ".code-dude"
    target_root = Path(args.root).resolve() / ".code-dude"

    if not template_root.exists():
        print(f"template not found: {template_root}", file=sys.stderr)
        return 1

    copied = []
    skipped = []

    for source in sorted(template_root.rglob("*")):
        relative = source.relative_to(template_root)
        destination = target_root / relative

        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and not args.force:
            skipped.append(str(destination))
            continue

        shutil.copy2(source, destination)
        copied.append(str(destination))

    print(f"initialized: {target_root}")
    if copied:
        print("copied:")
        for item in copied:
            print(f"  {item}")
    if skipped:
        print("skipped existing:")
        for item in skipped:
            print(f"  {item}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
