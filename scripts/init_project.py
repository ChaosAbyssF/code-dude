#!/usr/bin/env python3
"""Initialize a project-local .code-dude workspace."""

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


DIRECTORIES = [
    "lessons",
    "project-notes",
    "tasks",
    "user-profile",
]


FILES = {
    "lessons/.gitkeep": "",
    "project-notes/.gitkeep": "",
    "tasks/.gitkeep": "",
    "tasks/.task-config-template.yaml": TASK_CONFIG_TEMPLATE,
    "user-profile/.gitkeep": "",
}


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
    target_root = Path(args.root).resolve() / ".code-dude"

    copied = []
    skipped = []

    target_root.mkdir(parents=True, exist_ok=True)

    for relative in DIRECTORIES:
        destination = target_root / relative
        destination.mkdir(parents=True, exist_ok=True)

    for relative, content in FILES.items():
        destination = target_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and not args.force:
            skipped.append(str(destination))
            continue

        destination.write_text(content, encoding="utf-8")
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
