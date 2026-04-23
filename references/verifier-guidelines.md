# Verifier Guidelines

A good verification entrypoint for this skill should:

- accept or derive a unique output directory per run
- avoid reusing the same artifact directory silently
- make it easy to compare baseline and follow-up attempts
- preserve logs, metrics, and key outputs

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
