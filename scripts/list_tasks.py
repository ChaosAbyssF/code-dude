#!/usr/bin/env python3
"""Summarize .code-dude task workspaces for quick task selection."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Target repository root.")
    parser.add_argument(
        "--include-done",
        action="store_true",
        help="Include tasks whose directory names end in _done.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of markdown.",
    )
    return parser.parse_args()


def modified_utc(path: Path) -> str:
    mtime = path.stat().st_mtime
    return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()


def read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8", errors="ignore").splitlines()


def section_scalar(lines: list[str], section: str, key: str) -> str | None:
    in_section = False
    section_prefix = f"{section}:"
    key_prefix = f"  {key}:"

    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            in_section = line.strip() == section_prefix
            continue
        if in_section and line.startswith(key_prefix):
            value = line.split(":", 1)[1].strip()
            return decode_scalar(value)
    return None


def decode_scalar(value: str) -> str | None:
    if not value:
        return None
    if value[0] in {"'", '"'}:
        try:
            parsed = json.loads(value)
            return str(parsed) if parsed is not None else None
        except json.JSONDecodeError:
            return value.strip("\"'") or None
    return value


def first_bullet_after_heading(lines: list[str], heading: str) -> str | None:
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_section = stripped == heading
            continue
        if in_section and stripped.startswith("- "):
            return stripped[2:].strip() or None
    return None


def summarize_task(path: Path) -> dict[str, object]:
    config_lines = read_lines(path / "config.yaml")
    status_lines = read_lines(path / "current-status.md")
    issue_lines = read_lines(path / "unresolved-issues.md")

    return {
        "id": path.name,
        "path": str(path),
        "state": "done" if path.name.endswith("_done") else "active",
        "modified_utc": modified_utc(path),
        "summary": section_scalar(config_lines, "goal", "summary"),
        "success_definition": section_scalar(config_lines, "goal", "success_definition"),
        "phase": first_bullet_after_heading(status_lines, "## Phase"),
        "latest_result": first_bullet_after_heading(status_lines, "## Latest Result"),
        "active_issue": first_bullet_after_heading(issue_lines, "## Active Issues"),
    }


def task_directories(tasks_root: Path, include_done: bool) -> list[Path]:
    if not tasks_root.exists():
        return []

    directories = [item for item in tasks_root.iterdir() if item.is_dir()]
    if not include_done:
        directories = [item for item in directories if not item.name.endswith("_done")]
    return sorted(directories, key=lambda item: item.stat().st_mtime, reverse=True)


def print_markdown(tasks_root: Path, tasks: list[dict[str, object]]) -> None:
    print(f"# Tasks under {tasks_root}")
    print()
    if not tasks:
        print("- No task workspaces found.")
        return

    for task in tasks:
        print(f"## {task['id']}")
        print()
        print(f"- State: {task['state']}")
        print(f"- Summary: {task['summary'] or '_None_'}")
        print(f"- Success definition: {task['success_definition'] or '_None_'}")
        print(f"- Phase: {task['phase'] or '_None_'}")
        print(f"- Latest result: {task['latest_result'] or '_None_'}")
        print(f"- Active issue: {task['active_issue'] or '_None_'}")
        print(f"- Modified UTC: {task['modified_utc']}")
        print()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    tasks_root = root / ".code-dude" / "tasks"
    tasks = [summarize_task(path) for path in task_directories(tasks_root, args.include_done)]

    if args.json:
        print(json.dumps({"tasks_root": str(tasks_root), "tasks": tasks}, indent=2, ensure_ascii=True))
        return 0

    print_markdown(tasks_root, tasks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
