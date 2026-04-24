# Verifier Guidelines

A good verification entrypoint for this skill should:

- accept or derive a unique output directory per run
- avoid reusing the same artifact directory silently
- make it easy to compare baseline and follow-up attempts
- preserve logs, metrics, and key outputs

This verifier is usually the final or authoritative check. It should not automatically replace cheaper validation loops when the repository is large or the run is expensive.

Before relying on the full verifier for iteration, Codex should look for smaller trustworthy checks such as:

- a focused unit test near the changed code
- a narrow integration test with reduced fixtures
- a module-level or target-level compile command
- a small smoke script that checks the behavior under change

If none exists and the repository is large enough that full verification is slow or costly, Codex should add a narrow validation entrypoint in a reasonable repository location when practical, then use that in the inner loop before rerunning the full verifier.

Typical naming style:

- `Try01_baseline`
- `Try02_fix_null_guard`
- `Try03_batch32_tuned`

If the current verifier does not support this, Codex should raise the issue before mass experimentation and offer to help patch it.

Common signals that a verifier already supports the workflow:

- references to `mkdir`, `runs`, `outputs`, or `artifacts`
- string patterns such as `Try`, `trial`, `experiment`, timestamps, or numbered suffixes
- CLI flags like `--output-dir`, `--save-dir`, `--run-name`, or `--exp-name`

Common signals that it probably does not:

- hard-coded single output file paths
- unconditional overwrite of the same directory
- no logging destination and no artifact management
