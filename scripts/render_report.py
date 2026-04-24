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
        "--task-dir",
        help="Task workspace directory, relative to repo root or absolute. Defaults to the newest directory under .code-dude/tasks.",
    )
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


def read_config_lines(workspace: Path) -> list[str]:
    config_path = workspace / "config.yaml"
    if not config_path.exists():
        return []
    return config_path.read_text(encoding="utf-8", errors="ignore").splitlines()


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
            value = line.split(":", 1)[1].strip().strip("\"'")
            return value or None
    return None


def objective_summary(task_workspace: Path) -> str:
    lines = read_config_lines(task_workspace)
    summary = section_scalar(lines, "goal", "summary")
    success = section_scalar(lines, "goal", "success_definition")

    if summary and success:
        return f"{summary}\n\nSuccess definition: {success}"
    if summary:
        return summary
    if success:
        return f"Success definition: {success}"
    return first_paragraph(task_workspace / "config.yaml")


def verification_summary(task_workspace: Path) -> str:
    lines = read_config_lines(task_workspace)
    entrypoint = section_scalar(lines, "verification", "entrypoint")
    workdir = section_scalar(lines, "verification", "working_directory")

    parts = []
    if entrypoint:
        parts.append(f"Entrypoint: `{entrypoint}`")
    if workdir:
        parts.append(f"Working directory: `{workdir}`")
    return "\n\n".join(parts) if parts else "_No verification details found in config._"


def newest_directory(path: Path) -> Path | None:
    if not path.exists():
        return None
    directories = [item for item in path.iterdir() if item.is_dir()]
    if not directories:
        return None
    return max(directories, key=lambda item: item.stat().st_mtime)


def newest_active_directory(path: Path) -> Path | None:
    if not path.exists():
        return None
    active_directories = [
        item for item in path.iterdir() if item.is_dir() and not item.name.endswith("_done")
    ]
    if not active_directories:
        return None
    return max(active_directories, key=lambda item: item.stat().st_mtime)


def resolve_tasks_root(workspace: Path) -> Path:
    return workspace / "tasks"


def resolve_task_workspace(root: Path, workspace: Path, task_dir_arg: str | None) -> Path:
    tasks_root = resolve_tasks_root(workspace)

    if task_dir_arg:
        candidate = Path(task_dir_arg)
        if not candidate.is_absolute():
            candidate = (root / candidate).resolve()
        return candidate

    newest = newest_active_directory(tasks_root) or newest_directory(tasks_root)
    if newest is None:
        raise FileNotFoundError(
            f"no task workspace found under {tasks_root}; pass --task-dir explicitly"
        )
    return newest


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    workspace = root / ".code-dude"
    task_workspace = resolve_task_workspace(root, workspace, args.task_dir)
    scenario_dir = task_workspace / "scenario-models"
    issues_dir = task_workspace / "unresolved-issues"
    status_dir = task_workspace / "current-status"
    reports_dir = task_workspace / "reports"
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
        objective_summary(task_workspace),
        "",
        "## Repository Understanding",
        "",
        first_paragraph(scenarios[0]) if scenarios else "_No scenario model found._",
        "",
        "## Task Workspace",
        "",
        str(task_workspace.relative_to(root)) if task_workspace.is_relative_to(root) else str(task_workspace),
        "",
        "## Current Status",
        "",
        first_paragraph(statuses[0]) if statuses else "_No current status file found._",
        "",
        "## Changes Made",
        "",
        first_paragraph(statuses[0]) if statuses else "_No change summary found._",
        "",
        "## Verification",
        "",
        verification_summary(task_workspace),
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
