#!/usr/bin/env python3
"""Render a markdown task report from a .code-dude workspace."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Target repository root.")
    parser.add_argument(
        "--title",
        default="Task Report",
        help="Markdown report title.",
    )
    return parser.parse_args()


def newest_markdown(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted(path.glob("*.md"), key=lambda item: item.stat().st_mtime, reverse=True)


def first_paragraph(path: Path) -> str:
    if not path.exists():
        return "_None_"
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        return "_Empty_"
    blocks = [block.strip() for block in text.split("\n\n") if block.strip()]
    return blocks[0] if blocks else "_Empty_"


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    workspace = root / ".code-dude"
    scenario_dir = workspace / "scenario-models"
    issues_dir = workspace / "unresolved-issues"
    status_dir = workspace / "current-status"
    reports_dir = workspace / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    scenarios = newest_markdown(scenario_dir)
    issues = newest_markdown(issues_dir)
    statuses = newest_markdown(status_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = reports_dir / f"{timestamp}_task_report.md"

    lines = [
        f"# {args.title}",
        "",
        "## Objective",
        "",
        first_paragraph(workspace / "config.yaml"),
        "",
        "## Repository Understanding",
        "",
        first_paragraph(scenarios[0]) if scenarios else "_No scenario model found._",
        "",
        "## Current Status",
        "",
        first_paragraph(statuses[0]) if statuses else "_No current status file found._",
        "",
        "## Remaining Issues",
        "",
    ]

    if issues:
        lines.extend([f"- {item.name}" for item in issues[:10]])
    else:
        lines.append("_No unresolved issue files found._")

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
