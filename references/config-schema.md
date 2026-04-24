# Config Schema

Each task-local config lives at `.code-dude/tasks/<task-id>/config.yaml`.

Recommended shape:

```yaml
version: 1

goal:
  summary: "Fix a bug"  # short operational objective
  success_definition: "Describe what done looks like"

verification:
  entrypoint: "./scripts/verify.sh"
  working_directory: "."
  expected_artifact_root: "./runs"
  notes:
    - "Verifier usually writes TryXX_* directories"
    - "This is usually the final end-to-end verifier, not necessarily the first validation step"

runtime:
  type: "local"  # one of: local, remote, container, remote_container
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
  - "Do not change public API signatures"

cleanup:
  trial_cleanup_threshold: 15
  keep_recent_trials: 5
```

Guidance:

- `goal.summary` should be short and concrete.
- `goal.success_definition` should describe what the verifier should prove.
- `verification.entrypoint` should be the actual command entry file or script for the authoritative overall success check.
- Codex should still look for or create smaller validation commands when the repository is large or the verifier is expensive.
- If the user already provides sufficient baseline or current-state evidence, Codex should not default to an exploratory full-project run before editing.
- `verification.expected_artifact_root` should point to the parent directory where run outputs are created, if applicable.
- `runtime.type` controls how Codex should think about command execution.
- `attention_points` is the place for project-specific caveats.
- The current user request should come from the active conversation, not be duplicated in config.
- Shared lessons should live under `.code-dude/lessons/`, while task-progress state should stay inside the task workspace.
- Shared user preferences should live in `.code-dude/user-profile.md`.
- Task-specific notes should live under a task workspace like `.code-dude/tasks/20260424_fix_login_bug/`.
- Prefer task-local markdown files such as `scenario-model.md`, `current-status.md`, and `unresolved-issues.md` instead of creating one-file directories for them.
- Once the user explicitly confirms completion, rename that task workspace to `.code-dude/tasks/20260424_fix_login_bug_done/`.
