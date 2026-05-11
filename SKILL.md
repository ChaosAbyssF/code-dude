---
name: code-dude
description: Use this skill when the user wants Codex to take over an engineering workflow end to end in an existing repository, guided by a task-local config plus shared notes for user preferences and reusable repository context.
---

# Code Dude

Use this skill when the user wants Codex to iteratively modify code, build it, run a provided verifier, track experiments, record lessons, and deliver a final report under a reusable project workflow.

## What this skill owns

This skill standardizes a project-local workspace, normally rooted at `.code-dude/`, with shared and task-specific state kept separate:

- `lessons/`: shared mistakes, debugging heuristics, and reusable lessons learned across tasks
- `project-notes/`: shared repository context, execution hints, and other cross-task notes
- `user-profile.md`: shared notes about stable user preferences, especially forbidden actions
- `tasks/<task-id>/`: one workspace per materially distinct active task
- `tasks/<task-id>_done/`: a completed task workspace after the user has confirmed the task is done

Each task workspace should contain:

- `config.yaml`: user-maintained goal, environment, verification entrypoint, and task caveats
- `scenario-model.md`: Codex-written understanding of the task and repository
- `current-status.md`: concise current state, latest attempt, and next step
- `unresolved-issues.md`: open blockers, gaps, regressions, and still-open questions for the task
- `reports/`: final task reports and milestone summaries

Prefer these as single markdown files instead of tiny directories. When creating a new task workspace, create these real files directly with starter content instead of creating separate template markdown files.

## Task selection

At the start of using this skill in a repository, first scan `.code-dude/tasks/` when it exists. Read the task directory names and the most relevant task-local files before deciding what workspace to use:

- `config.yaml`
- `scenario-model.md`
- `current-status.md`
- `unresolved-issues.md`

Prefer reusing an active task directory when the current request is materially the same task as an existing one. Use the goal, success definition, current status, unresolved issues, and the user's current request as the matching evidence.

Do not reuse a task directory just because it is the newest one. If the match is unclear, create a new date-prefixed task id and note the uncertainty in `scenario-model.md`. Treat directories ending in `_done` as historical context only unless the user explicitly asks to reopen or continue that completed task.

Use `scripts/list_tasks.py` when available to summarize task workspaces quickly, then inspect the relevant task files directly before relying on the summary.

## First pass

Before making meaningful changes:

1. Determine the active task workspace under `.code-dude/tasks/`. Scan the existing task list first. Reuse an existing active task directory only when the current request is materially the same task; otherwise create a new date-prefixed task id such as `.code-dude/tasks/20260424_fix_login_bug/`.
2. Ensure the active task workspace contains `config.yaml`, `scenario-model.md`, `current-status.md`, and `unresolved-issues.md`. If any are missing, create the real file with sensible starter content, then read it.
3. Read the active repository and the user's current request together. Treat the conversation as the source of truth for the current request instead of duplicating it in config.
4. After reading the user's message, explicitly consider whether it reveals a stable preference that belongs in shared `.code-dude/user-profile.md`. This review is required on every user turn, including the first one, even when no update is needed.
5. Produce or update `scenario-model.md` in the active task workspace.
6. Inspect the verification entrypoint from the task-local config before running it.
7. Check task-local `unresolved-issues.md` and `current-status.md` together with shared lessons, project notes, and `user-profile.md` for relevant context.

The first scenario model should cover:

- user goal in operational terms
- current repository shape
- project scale and validation cost, especially whether full builds or end-to-end runs are slow or expensive
- whether the user has already provided enough baseline, reproduction detail, logs, metrics, or expected behavior to avoid an initial exploratory run
- likely success criteria
- known risks and unknowns
- intended edit and validation loop

After that first pass, move quickly into code changes. Do not default to only editing config files or launch scripts unless that is genuinely the right fix. In normal cases, once the repository is understood well enough, directly modify the relevant code and validate.

## Bug fix reproduction policy

When the current task is a bug fix, first consider the cheapest trustworthy way to reproduce the failure before editing implementation code. Good reproduction surfaces include:

- an existing focused failing test
- a new narrow regression test near the affected module
- a small fixture or smoke script in the repository's normal test location
- a minimal command that exercises the failing path

For large repositories or expensive verifiers, prefer this minimal reproduction as the inner edit loop, then run the configured verifier after the narrow check passes. If the user already provided a precise failing test, stack trace, reproduction command, or other sufficient evidence, use that evidence directly and do not spend time inventing another reproduction. If adding a focused reproduction would require disproportionate scaffolding, document that tradeoff in `scenario-model.md` or `unresolved-issues.md` and use the smallest existing trustworthy check.

## Core operating loop

For active implementation work, follow this loop:

1. Re-state the working objective internally from the task-local config plus the user request.
2. Inspect relevant code and prior notes from the active task workspace, shared lessons, shared project notes, and shared `user-profile.md`.
3. Do not default to running the project just to observe the current state when the user has already provided enough signal. Use the user's report, logs, stack traces, baseline metrics, expected behavior, and code inspection first. Only do an exploratory run when that missing information is necessary and the cost is justified.
4. For bug fixes, identify the minimal trustworthy reproduction or explain why the existing evidence is sufficient before editing.
5. Make the smallest changes that move the objective forward.
6. Prefer the cheapest meaningful validation first:
   - run a small-unit compile, targeted test, or other narrow check around the changed code
   - use broader builds only when the narrow check passes or cannot prove the requirement
7. Run the configured verifier after targeted validation, or sooner only when no smaller trustworthy check exists.
8. After every run or verification attempt, update at least one maintained memory location with the outcome. Valid targets include task-local `current-status.md`, task-local `unresolved-issues.md`, shared `.code-dude/lessons/`, and shared `.code-dude/project-notes/`. Do not finish a run and leave all of them untouched.
9. Record outcomes in the most appropriate places:
   - update `current-status.md` for latest phase, result, and next step
   - update `unresolved-issues.md` when the run exposes a blocker, gap, regression, or still-open question
   - update shared `lessons/` when the run teaches a reusable debugging or validation lesson
   - update shared `project-notes/` when the run reveals reusable repository facts, setup quirks, or safe operating guidance
10. Repeat until the goal is satisfied or the remaining blocker requires user input.

Always prefer evidence from the verifier over intuition.
Do not stop to present a proposed implementation plan to the user unless user confirmation is actually required.

For large or slow repositories, treat small-unit validation as the default path. Signs include expensive compile times, heavy dependency graphs, large test suites, or verifier scripts that run end-to-end workflows. In those cases, avoid using the full verifier as the first feedback loop unless the task itself is inherently end-to-end.

Treat user-provided evidence as the primary starting point across bug fixes and other change requests. If the user already provides a bug description, baseline numbers, regression symptoms, target behavior, or comparison results, do not spend time on an initial full-project run just to recreate that context unless the missing information is blocking and the run cost is justified.

## Stop condition

Stop when the configured goal has been achieved according to the verifier or other explicit success condition in the user request. Do not invent broader stopping criteria.

If the user confirms that the task is complete, rename the task workspace from `tasks/<task-id>/` to `tasks/<task-id>_done/`. Do this only after explicit user confirmation, not merely because the verifier passed.

## User dissatisfaction and cleanup

When the user explicitly says they are dissatisfied with Codex's execution, especially near the end of a task, treat that as a corrective workflow rather than a normal completion signal.

First identify what Codex changed during the task:

- implementation files, tests, configs, and other repository files
- generated or updated skill documents under `.code-dude/`, including task-local `scenario-model.md`, `current-status.md`, `unresolved-issues.md`, `reports/`, shared `project-notes/`, and shared `user-profile.md`
- shared lesson entries under `.code-dude/lessons/`
- verifier outputs, trial directories, temporary artifacts, and helper files created for the task

Then consider whether code rollback is appropriate, but do not destructively reset unrelated user work. Prefer targeted reverse patches for Codex-authored changes, and ask before deleting or reverting anything when ownership is unclear.

Also clean up skill-generated documents that no longer reflect an accepted task outcome. In particular:

- remove or revise final reports, stale task summaries, and task-local status documents that present the rejected work as successful
- remove task-local generated documents when the whole task workspace only represents the rejected attempt and the user has not asked to preserve it
- keep `config.yaml` when it contains user-maintained task intent unless the user asks to delete the task workspace
- do not silently erase useful evidence of the failure; preserve a concise note when it helps explain what was rejected or rolled back

Update `.code-dude/lessons/` promptly with the reusable lesson from the dissatisfaction, such as the rejected assumption, forbidden action, cleanup expectation, or validation gap that led to the bad outcome. If an existing lesson caused or encouraged the mistake, revise or remove it instead of adding a contradictory new entry. If the user states a stable preference or forbidden action, update `.code-dude/user-profile.md` as well.

Do not rename the task workspace to `_done` after a dissatisfaction signal unless the user later explicitly confirms that the corrective cleanup or rollback is complete.

## Missing logged files

When task logs, status files, reports, lessons, or project notes refer to a repository file that no longer exists, do not assume it is merely an accidental missing path. First consider that the user may have manually deleted the file because they did not accept Codex's update to it.

Before recreating, re-editing, or relying on that path:

- check recent context and git status to determine whether Codex created or modified the file
- treat a user-deleted Codex-authored file as a rejection of that file's update unless the user says otherwise
- avoid recreating the file automatically just because a prior task note mentions it
- update `current-status.md` or `unresolved-issues.md` to reflect that the file disappeared and may have been intentionally removed
- update shared lessons when the disappearance reveals a reusable mistake about file ownership, generated artifacts, or user acceptance

If the missing file is required for the task to proceed, explain the dependency and ask before restoring it when user intent is unclear.

## Verifier policy

The task-local `config.yaml` contains `verification.entrypoint`. Treat it as the source of truth for success checks unless the user explicitly overrides it.

That entrypoint is the final or authoritative success check, not automatically the first check to run. Before using it heavily, identify whether the repository already has smaller validation surfaces such as:

- package- or module-level builds
- focused unit or integration tests
- single-binary or single-target compilation commands
- reduced fixtures, smoke tests, or minimal reproductions

When the repository is large, complex, or slow, prefer those smaller checks first and use the configured verifier afterward to confirm end-to-end success.

If the user provides only an overall verifier and the repository does not expose a suitable small-unit check, Codex should create one when practical. Typical examples:

- add a focused unit test near the changed module
- add a minimal regression test for the reported failure mode or changed behavior
- add a lightweight build target, script, or harness that compiles only the affected component
- add a small fixture or smoke script in the repository's normal test location

Place this helper in a reasonable project-local location that matches the repo's conventions. Keep it narrow, cheap to run, and directly tied to the edited behavior. Do not create throwaway files outside the repository's normal structure when a proper test or build target can be added instead.

If creating such a targeted check would require a disproportionate amount of scaffolding, document that fact in `scenario-model.md` or shared lessons and fall back to the smallest existing trustworthy validation before the full verifier.

Likewise, do not add an exploratory baseline run if the user already supplied the baseline or current-state evidence needed for the task. For optimization, regression analysis, or behavior-adjustment work, prefer the user-provided baseline plus narrow code-aware validation over rerunning the whole system just to confirm what the user already told you.

Before repeated runs, inspect that entrypoint and determine whether it supports isolated experiment output directories. A good verifier usually:

- creates or accepts a dedicated output directory per run
- avoids overwriting previous runs
- makes logs and artifacts easy to compare
- commonly uses names like `Try01_bsz32_baseline`

If the verifier does not appear to support per-run output isolation:

1. Stop before changing it automatically.
2. Tell the user the verifier is missing stable experiment-directory handling.
3. Offer to patch it.
4. If the user agrees, help implement the change.
5. If the user refuses, continue using the existing verifier and note that limitation in the scenario model and report.

Use `scripts/check_verifier.py` for a quick heuristic check when useful. Do not treat its result as authoritative; inspect the file yourself when the result matters.

## Experiment hygiene

Many projects accumulate run directories quickly. When the verifier writes to a parent experiment directory, periodically review it.

Around every 15 runs, consider cleanup:

- summarize older experiments into a markdown note under the active task workspace `reports/` or shared `.code-dude/lessons/`
- keep representative baselines, latest good runs, and currently relevant failures
- remove or archive stale output directories that no longer add value

Use `scripts/manage_trials.py` to summarize and optionally generate a cleanup plan. Do not delete history blindly; keep the user informed before destructive cleanup.

## Lessons and mistakes

Record things that should influence future edits:

- build and runtime failures
- repeated bad assumptions
- repository-specific constraints
- user corrections
- successful debugging heuristics

Write concise markdown entries in `.code-dude/lessons/`. Review relevant lessons before another risky edit.

Shared lessons should capture mistakes, failed approaches, and debugging heuristics that may help future tasks in the same repository. Keep purely task-progress notes out of this directory.

After a run, update `lessons/` when the result teaches something reusable beyond the current task. Do not force every run into `lessons/`, but do not skip all memory updates either.

## Shared project notes

Maintain lightweight notes in `.code-dude/project-notes/` for information that is useful across multiple tasks in the same repository, for example:

- recurring setup or verification quirks
- important architectural landmarks
- repository-specific debugging shortcuts
- known safe edit boundaries or risky areas
- assumptions that future tasks should not rediscover

Do not duplicate task progress here. Keep it focused on reusable repository context.

After a run, update `project-notes/` when you learn something that future tasks in the same repository should reuse, such as verifier quirks, environment constraints, or module ownership boundaries.

## User modeling

Maintain lightweight notes in `.code-dude/user-profile.md` about stable user preferences that should persist across tasks, for example:

- preferred experiment naming
- tolerance for intrusive refactors
- preferred communication style
- recurring project priorities
- actions or command classes the user has explicitly forbidden

Infer these preferences during normal interaction instead of interrogating the user for them. Only record stable preferences that help future work. Do not store secrets.

After every user message, explicitly consider whether `user-profile.md` should be updated. Do not force a write on every turn, but do not skip the review step. Update it when the user reveals a stable preference, a persistent constraint, a recurring priority, or a clearly stated forbidden action that future tasks should remember.

## Final reporting

When the task reaches a natural checkpoint or completion, create a report in the active task workspace `reports/` that includes:

- objective
- what changed
- targeted validation runs and outcomes
- verifier runs and outcomes
- remaining unresolved issues
- concise action summary only

Use `scripts/render_report.py` when it helps bootstrap the report.

## Repository bootstrap

If `.code-dude/` does not exist, initialize it with:

```bash
python3 code-dude/scripts/init_project.py --root /path/to/repo
```

If running from inside the target repository, `--root .` is usually enough.

When creating a new task workspace, initialize it with:

```bash
python3 code-dude/scripts/init_task.py --root /path/to/repo --task-id 20260424_fix_login_bug
```

To inspect existing task workspaces quickly:

```bash
python3 code-dude/scripts/list_tasks.py --root /path/to/repo
```

## Files to read selectively

- For config field semantics, read `references/config-schema.md`.
- For verifier expectations, read `references/verifier-guidelines.md`.
- For report structure, read `references/report-template.md`.

## Practical defaults

- Prefer incremental edits over broad refactors.
- Scan `.code-dude/tasks/` before choosing or creating the active task workspace.
- For large repositories, prefer targeted compile or test commands before full builds and end-to-end verifier runs.
- For bug fixes, consider a minimal reproduction before implementation edits, unless the user already supplied sufficient failure evidence.
- If no suitable targeted check exists, add one in the normal test or build structure when practical, then use it during the edit loop.
- When the user already provides sufficient baseline or current-state evidence, do not spend time on an initial exploratory run of the whole project.
- After every run, update at least one of `current-status.md`, `unresolved-issues.md`, shared `lessons/`, or shared `project-notes/`.
- After every user message, explicitly consider whether shared `user-profile.md` should be updated.
- If the user is explicitly dissatisfied with Codex's execution, consider targeted rollback, clean stale skill-generated documents, update lessons, and do not mark the task done.
- If a logged file no longer exists, consider that the user may have manually rejected that file's update before recreating it.
- Keep `scenario-model.md`, `current-status.md`, and `unresolved-issues.md` as markdown files in the task workspace instead of creating tiny one-file directories.
- Use date-prefixed names for both task directories and task-local files when practical.
- When a task is explicitly confirmed complete by the user, rename its directory to append `_done`.
- When environment details are incomplete, infer cautiously from the repository, then surface the gap.
- When the task-local config says the environment is remote or containerized, adapt commands accordingly instead of assuming the local shell is the execution target.
