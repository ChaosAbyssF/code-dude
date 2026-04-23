# Config Schema

The project-local config lives at `.code-dude/config.yaml`.

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

scenario:
  current_request: ""
  tags: []

tracking:
  unresolved_issues_dir: ".code-dude/unresolved-issues"
  scenario_models_dir: ".code-dude/scenario-models"
  current_status_dir: ".code-dude/current-status"
  lessons_dir: ".code-dude/lessons"
  user_profile_dir: ".code-dude/user-profile"
  reports_dir: ".code-dude/reports"

cleanup:
  trial_cleanup_threshold: 15
  keep_recent_trials: 5
```

Guidance:

- `goal.summary` should be short and concrete.
- `goal.success_definition` should describe what the verifier should prove.
- `verification.entrypoint` should be the actual command entry file or script.
- `verification.expected_artifact_root` should point to the parent directory where run outputs are created, if applicable.
- `runtime.type` controls how Codex should think about command execution.
- `attention_points` is the place for project-specific caveats.
- `tracking.*` may be kept at defaults unless the project needs a different layout.
- `tracking.current_status_dir` should contain short rolling notes instead of long historical logs.
