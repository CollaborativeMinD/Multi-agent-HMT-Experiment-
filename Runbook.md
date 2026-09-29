# Runbook

## Current pilot status: HOLD after the 8,192-token test

Read [the latest result](evidence/whiz8192-results-20260929.md) and [cumulative gates](evidence/whiz8192-gates.sql). Run 36504424064 stopped at frontier action 100 when Qwen reached the unchanged 120-second deadline. There was no retry. Mainstream has not started; neither game is complete. Known estimated cost is $1.60005550, plus a retained $0.06768 timeout reservation. No inference is running.

The user explicitly authorized this limited scored pilot and directed reevaluation on the next issue. Broader unrestricted campaigns remain disabled. Preserve the 100-action checkpoint; do not restart or silently replace a player. The proposed 240-second deadline test has not been executed.

### Verify the current game evidence offline

1. Install exact dependencies: `npm ci --ignore-scripts --prefix baseline`.
2. Apply the source-checked patch once after install: `python baseline/patch_engine.py`.
3. Prepare the reviewed start checkpoint: `python baseline/prepare_checkpoint.py`.
4. Run engine gates: `node baseline/test_engine.mjs`.
5. Run runner gates: `PYTHONPATH=scripts:baseline python -m unittest discover -s baseline -p test_runner.py -v`.
6. After extracting the run artifact, verify the new checkpoint with `python baseline/analyze.py PATH_TO_EVIDENCE`, then render with `python baseline/build_replay.py PATH_TO_EVIDENCE`.

These commands require no model keys. The checked-in resume8192 package is the 92-action starting checkpoint; the new 100-action terminal checkpoint is in the run's evidence artifact and delivered evidence bundle. Never confuse them.

## Scope

This repository contains model selection, API probes, and a bounded strict Whiz Spades pilot. A passed smoke canary proves one valid response at the recorded settings. It does not authorize scored play or prove strategic quality, sustained throughput, or remaining balance.

## Inspect evidence

1. Read `config/models.lock.json` for the roster and campaign status.
2. Read `evidence/inference-smoke-20260928.json` and its linked Actions run.
3. Inspect `evidence/inference-gates.sql` or reconstruct SQLite with `sqlite3 inference-gates.sqlite < evidence/inference-gates.sql`.
4. Read `docs/INFERENCE_SMOKE.md` for outcomes and remaining gates.

## Reproduce local checks without keys

Run `python -m unittest discover -s tests -p 'test_smoke.py' -v` with `PYTHONPATH=scripts` set. The tests inject fake providers, require no network, and cover budget admission, wrong model/provider, malformed actions, illegal play, missing credentials, timeout, HTTP 429/500, and retry suppression. Functions are checked against the 60-line limit.

## Execute a new paid smoke test

Do not rerun the completed live workflow. Rerun attempts are blocked to prevent duplicate charges. First account for prior usage, review the exact request profiles and current prices, and confirm the new request count and reservation fit the remaining account budgets. A new reviewed workflow revision is required for another live attempt. Its own-path push trigger runs only that revision; other file commits do not trigger inference. Secrets are injected only into the request step from GitHub Actions.

Never put secrets into config files, receipts, test fixtures, screenshots, or logs. Never print a raw provider error body or reasoning content. The canary contains synthetic game data only. Do not widen model or provider fallback to make a check pass.

## Failure handling

- HTTP 401/403: inspect the corresponding account's credential permissions; do not copy the secret into a diagnostic artifact.
- HTTP 400: verify request fields against the provider API before a bounded correction. Preserve the original failure.
- HTTP 429/500 or timeout: HOLD the model; do not automatically retry. A timeout can still incur charges. Reserve its full request allowance until reconciled.
- Incomplete output: inspect cap and reasoning settings. Treat a higher cap as a new costed test, not proof of model failure at gameplay.
- Schema, legality, identity, or route mismatch: HOLD; trace the failing seam with fixtures before another paid attempt.
- Missing or excessive usage: HOLD and reconcile accounting before additional requests.

Record output-first cause, evidence, regression, and disposition in the Reverse RCA Ledger. Keep existing good local gates passing. Provider invoices remain the billing authority; receipt estimates are not invoices.

## Before scored games

Build and verify the game rules and private observations, replay, seat/partner rotation, campaign-wide budget guard, and explicit reasoning/token settings. The smoke profile uses economical reasoning and must not silently become the frontier benchmark profile. Both cohorts share each account's original $10 ceiling, including tests and retries.
