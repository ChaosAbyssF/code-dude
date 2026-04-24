#!/usr/bin/env python3
"""Initialize a task workspace under .code-dude/tasks with real starter files."""

from __future__ import annotations

import argparse
from pathlib import Path


TASK_CONFIG_TEMPLATE = """version: 1

goal:
  summary: "Describe the objective"
  success_definition: "Describe what the verifier should prove when the task is done"

verification:
  entrypoint: "./path/to/verify.sh"
  working_directory: "."
  expected_artifact_root: "./runs"
  notes:
    - "Describe expected output naming if known"

runtime:
  type: "local"
  local:
    shell: "bash"
  remote:
    ssh_user: ""
    ssh_host: ""
    workspace: ""
  container:
    name: ""
    workspace: ""
  remote_container:
    ssh_user: ""
    ssh_host: ""
    container_name: ""
    workspace: ""

attention_points:
  - "List important constraints here"

cleanup:
  trial_cleanup_threshold: 15
  keep_recent_trials: 5
"""

TASK_SCENARIO_TEMPLATE = """# Scenario Model

## Objective

- Summarize the task in operational terms.

## Repository Shape

- Note the relevant modules, binaries, services, or subsystems.

## Success Criteria

- Record what will count as done.

## Risks And Unknowns

- List the main uncertainties, gaps, or likely failure modes.

## Validation Plan

- Start with the cheapest meaningful checks.
- Prefer targeted validation before the overall verifier.
- Note whether the user already supplied enough context to avoid an exploratory full-project run.
"""

TASK_STATUS_TEMPLATE = """# Current Status

## Phase

- Not started.

## Latest Result

- No runs recorded yet.

## Next Step

- Identify the smallest meaningful change or validation step.
"""

TASK_UNRESOLVED_TEMPLATE = """# Unresolved Issues

## Active Issues

- None recorded yet.

## Notes

- Add blockers, regressions, open questions, or gaps that still affect the task.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Target repository root.")
    parser.add_argument("--task-id", required=True, help="Task id directory name to create.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files when they conflict.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = Path(args.root).resolve() / ".code-dude" / "tasks" / args.task_id
    reports_dir = workspace / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    skipped = []

    files = {
        workspace / "config.yaml": TASK_CONFIG_TEMPLATE,
        workspace / "scenario-model.md": TASK_SCENARIO_TEMPLATE,
        workspace / "current-status.md": TASK_STATUS_TEMPLATE,
        workspace / "unresolved-issues.md": TASK_UNRESOLVED_TEMPLATE,
    }

    for destination, content in files.items():
        if destination.exists() and not args.force:
            skipped.append(str(destination))
            continue
        destination.write_text(content, encoding="utf-8")
        copied.append(str(destination))

    print(f"initialized task workspace: {workspace}")
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
