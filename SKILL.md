---
name: code-dude
description: Use this skill when the user wants Codex to take over an engineering workflow end to end in an existing repository, guided by a structured config that defines the goal, verification entrypoint, runtime environment, caveats, unresolved issues, user preferences, experiment tracking, and final reporting.
---

# Code Dude

Use this skill when the user wants Codex to iteratively modify code, build it, run a provided verifier, track experiments, record lessons, and deliver a final report under a reusable project workflow.

## What this skill owns

This skill standardizes a project-local workspace, normally rooted at `.code-dude/`, with:

- `config.yaml`: user-maintained task and environment config
- `scenario-models/`: Codex-written understanding of the task and repository
- `current-status/`: concise current state, latest attempt, and next step
- `unresolved-issues/`: one markdown file per open problem
- `lessons/`: accumulated mistakes, run failures, repo insights, and user corrections
- `user-profile/`: notes about stable user preferences, especially forbidden actions
- `reports/`: final task reports and milestone summaries

## First pass

Before making meaningful changes:

1. Read `.code-dude/config.yaml`.
2. Read the active repository and the user's current request together. Treat the conversation as the source of truth for the current request instead of duplicating it in config.
3. Produce or update a scenario model in `.code-dude/scenario-models/`.
4. Inspect the verification entrypoint from config before running it.
5. Check unresolved issues, lessons, current status, and user profile notes for relevant context.

The first scenario model should cover:

- user goal in operational terms
- current repository shape
- likely success criteria
- known risks and unknowns
- intended edit and validation loop

After that first pass, move quickly into code changes. Do not default to only editing config files or launch scripts unless that is genuinely the right fix. In normal cases, once the repository is understood well enough, directly modify the relevant code and validate.

## Core operating loop

For active implementation work, follow this loop:

1. Re-state the working objective internally from config plus the user request.
2. Inspect relevant code and prior notes.
3. Make the smallest changes that move the objective forward.
4. Build or run the project as needed.
5. Run the configured verifier.
6. Record outcomes in lessons and unresolved issues.
7. Update `.code-dude/current-status/` with the current phase, latest result, and next step.
8. Repeat until the goal is satisfied or the remaining blocker requires user input.

Always prefer evidence from the verifier over intuition.
Do not stop to present a proposed implementation plan to the user unless user confirmation is actually required.

## Stop condition

Stop when the configured goal has been achieved according to the verifier or other explicit success condition in the user request. Do not invent broader stopping criteria.

## Verifier policy

The config contains a `verification.entrypoint`. Treat it as the source of truth for success checks unless the user explicitly overrides it.

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

- summarize older experiments into a markdown note under `.code-dude/reports/` or `.code-dude/lessons/`
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

## User modeling

Maintain lightweight notes in `.code-dude/user-profile/` about stable user preferences, for example:

- preferred experiment naming
- tolerance for intrusive refactors
- preferred communication style
- recurring project priorities
- actions or command classes the user has explicitly forbidden

Infer these preferences during normal interaction instead of interrogating the user for them. Only record stable preferences that help future work. Do not store secrets.

## Final reporting

When the task reaches a natural checkpoint or completion, create a report in `.code-dude/reports/` that includes:

- objective
- what changed
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

## Files to read selectively

- For config field semantics, read `references/config-schema.md`.
- For verifier expectations, read `references/verifier-guidelines.md`.
- For report structure, read `references/report-template.md`.

## Practical defaults

- Prefer incremental edits over broad refactors.
- Keep unresolved issues as separate files, one issue per file.
- Use date-prefixed filenames when creating scenario models, lessons, and reports.
- When environment details are incomplete, infer cautiously from the repository, then surface the gap.
- When the config says the environment is remote or containerized, adapt commands accordingly instead of assuming the local shell is the execution target.
