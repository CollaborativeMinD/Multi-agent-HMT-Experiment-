# Runbook

## Active authorized campaign: strict 300-point best-of-five

The user authorized one first-to-three-wins series per cohort, games to 300. Free Play remains prohibited. Read series/PROTOCOL.md, series/plan.json, and the README live section. Seeds and partnerships are fixed in the plan. The workflow publishes each independently verified hand and stops both cohorts on the first issue. No automatic retries or reruns.

Budget: use the original $10/account ceiling, with $9.98 cumulative request admission and $0.02/account reserved for prior probes. Opening accounting is $2.14137450, including the unresolved $0.06768 timeout reserve. The pilot-only $3 bound is superseded for this explicitly authorized series.

### Series operation and recovery

1. Run the baseline installation and tests below, then `node series/tracer.mjs` and `PYTHONPATH=scripts:baseline:series python -m unittest discover -s series -p test_series.py -v`.
2. The single-use whiz300-series workflow first publishes initial README/status with no model calls, proving publication access before spending.
3. Each invocation of `python series/campaign.py` advances at most one hand. It replays every prior action, reconciles usage, and enforces remaining budget before requests. Do not run it casually with keys available.
4. `python series/report.py` operates offline: verify every state/private projection and hand score, write replay HTML and gate ledger, then project the status into the README markers. A reporting failure prevents the next hand.
5. Inspect `evidence/whiz300/series.json`, per-game calls.jsonl, cohort JSONL, analysis.json, replay.html, and gates.sql. Download HTML files for playback. SQLite is exported cumulatively.
6. On HOLD, preserve the current checkout or Actions artifact, inspect the last call and state hashes, reconcile unknown usage, and follow Reverse RCA. Do not remove HOLD or retry automatically. Never reset spend or replay paid actions. A later authorized recovery must restore the exact persisted state and ledger.
7. Stop after three wins per cohort. Maximum five games per cohort, twenty hands per game, two hundred hand invocations. No new hand after 330 workflow minutes; six-hour hard workflow timeout. A bound is HOLD, never a winner.

The original baseline below is complete and separate from these series wins. No Free Play or additional campaign follows automatically.

## Current pilot status: COMPLETE

Both authorized strict games finished in run 36506341980: frontier 134 to -175; mainstream 132 to -130. Each has two completed hands and 112 actions. Read evidence/whiz240-results-20260929.md and evidence/whiz240-gates.sql. All 94 new API calls passed. No request exceeded 120 seconds; the 240-second deadline is not proven necessary. That baseline run is complete; the newly authorized strict 300-point campaign is described above. Free Play remains disabled.

Cumulative known estimated pilot usage is $2.07369450, plus the prior unresolved $0.06768 timeout reservation, totaling $2.14137450. Preserve all earlier failures. Do not rerun the paid workflow. The active resume240 package remains the 100-action starting checkpoint, not the complete-game evidence.

### Verify the current game evidence offline

1. Install exact dependencies: `npm ci --ignore-scripts --prefix baseline`.
2. Apply the source-checked patch once after install: `python baseline/patch_engine.py`.
3. Prepare the reviewed start checkpoint: `python baseline/prepare_checkpoint.py`.
4. Run engine gates: `node baseline/test_engine.mjs`.
5. Run runner gates: `PYTHONPATH=scripts:baseline python -m unittest discover -s baseline -p test_runner.py -v`.
6. After extracting the run artifact, verify the new checkpoint with `python baseline/analyze.py PATH_TO_EVIDENCE`, then render with `python baseline/build_replay.py PATH_TO_EVIDENCE`.

These commands require no model keys. The active prepare_checkpoint.py materializes resume240: the verified 100-action starting checkpoint. Earlier checkpoint packages remain historical evidence.

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

## Pro thinking-off diagnostic evidence

1. Read docs/PRO_OFF_REVIEW.md and evidence/pro-off-eval/qualification.json. Twelve inference checks passed; metadata availability holds full qualification.
2. Inspect plan.json and receipts.json in evidence/pro-off-eval. The two one-token cutoffs intentionally truncate and are not gameplay responses.
3. Compare generation-metadata.json with delayed-metadata.json. Preserve both initial and delayed 404 records. A missing generation record does not authorize paid inference replay.
4. Verify archived evidence from its directory with `sha256sum -c SHA256SUMS.txt`. Inspect cumulative SQL using SQLite; do not regenerate historical evidence merely to clear a HOLD.
5. Do not rerun completed paid workflows. Any subsequent diagnostic requires reviewed scope, remaining-budget admission, and a fresh single-use workflow. No fourth-seat substitution follows from these interface tests.

## Authorized Pro 100-point field trial

The user's subsequent order authorizes one fresh strict 100-point cohort-1 game with thinking-disabled DeepSeek Pro in p4 despite the preserved metadata qualification HOLD. Flash thinking-disabled is selected for cohort 2 p4; no cohort-2 game is started by this order. Read config/seat-selections.json. The trial uses seed 707, up to six hands, 8192 tokens, a 240-second request deadline, existing per-account budget ceilings, and no automatic retries. Earlier series remain immutable. Run trials/test_pro100.py offline before trials/pro100.py; the latter is paid and single-use. Inspect evidence/pro100/summary.json, gates.sql, and frontier-pro/Whiz_100_Baseline_Replay.html after each verified hand. HOLD stops play. No Free Play.

## Authorized matched Flash cohort-1 trial

The user authorizes one strict 100-point game substituting thinking-disabled deepseek/deepseek-v4.1-flash for Pro in cohort 1 seat p4. Reuse seed 707, initial game state, the other three models and settings, rules, 8192-token cap, 240-second deadline, six-hand bound, and no automatic retries. Provider remains Wafer. Fresh model decisions may cause trajectories to diverge. Begin cumulative accounting from evidence/pro100/summary.json. Preserve both earlier series and all Pro game files by hash. Run trials/test_flash100.py before the paid, single-use trials/flash100.py. Inspect evidence/flash100/summary.json and frontier-pro/Whiz_100_Baseline_Replay.html, where the internal frontier-pro ID is deliberately retained to match initial state exactly. The final model label identifies Flash. No cohort-2 game or Free Play is authorized by this trial.

## Inspect the completed Pro/Flash comparison

1. Read docs/PRO_FLASH_100_COMPARISON.md for results and shared prompt/sampling limits.
2. Read evidence/flash100/comparison.json for verified matching controls and the first differing action.
3. Download the replay HTML from each trial's frontier-pro directory. The retained internal directory name allows an identical initial game ID; the displayed model names distinguish the trials.
4. Verify Flash evidence from evidence/flash100 with `sha256sum -c SHA256SUMS.txt`. Cumulative gates and RCA observations are in gates.sql and gates.sqlite.
5. Treat both games as complete. Do not rerun paid workflows or revise their prompts retrospectively. Future wording changes require a separately identified evaluation profile.

## Nil-explicit v2 reruns

The user authorizes a neutral nil-definition clarification and one new 100-point game each for Pro and Flash. Only replace the original `Nil +/-100;` clause with an explicit zero-tricks/+100 and one-or-more-tricks/-100 definition. Every player receives the same revised rules. Use seed 707, existing cohort-1 seats, thinking-disabled Pro/Flash, prior limits, and unchanged engine rules. Run trials/test_nil100.py plus previous regression gates before trials/nil100.py pro, followed by trials/nil100.py flash only if Pro completes. Start account totals and cumulative ledgers from the last completed Flash trial, then carry Pro v2 usage into Flash v2. Preserve original Pro/Flash and series evidence. Each new directory evidence/nil-v2-pro or evidence/nil-v2-flash records prompt-delta.json with old/new text and hashes, plan, call receipts, verified score, cumulative gates, and replay. No inference retries or Free Play. Do not interpret one run per condition as proof of prompt causality.


## Strategy-guided v3 reruns

The user authorizes one new strict 100-point game each for Pro and Flash, appending the approved partnership-strategy paragraph to the nil-explicit v2 prompt. All four players receive identical guidance. Preserve seed 707, seats, candidate thinking-disabled settings, 8192-token cap, 240-second deadline, six-hand bound, and no retries. Run all offline gates before trials/strategy100.py pro, then flash only if Pro completes. Carry cumulative accounting from evidence/nil-v2-flash/summary.json, including the Anthropic HTTP 529 unknown-usage reservation. The prior Flash v2 game remains HOLD; these are fresh conditions, not a retry of that game. Freeze cumulative account ceilings in config/strategy-v3-budget.json, retaining the $0.02/account buffer. An announced top-up alone does not specify a new numeric ceiling.

Each hand verifies replay, private views, scores, and historical evidence hashes, publishes summary, receipts, HTML replay, and cumulative SQL, and updates the README. Inspect evidence/strategy-v3-pro or evidence/strategy-v3-flash. No Free Play. Do not infer prompt causality or individual rankings from one game per condition. Backend sampling parity remains unproven.


## Authorized Kimi/Mistral seat tracers

Read docs/SEAT_TRACER.md. The user authorizes up to ten isolated calls, $2 batch admission under the existing cumulative OpenRouter guard, with no retries, fallback, game moves, or seat changes. Run all offline workflow gates first. Inspect evidence/seat-tracer-kimi-mistral. This supersedes earlier restrictions only for these bounded probes.


## Authorized Kimi cohort-1 field evaluation

The user authorizes one strict 100-point game with Kimi K3 in p4, partnered with Anthropic. Read trials/kimi100.py and inspect evidence/kimi100/plan.json, summary.json, gates.sql, and frontier-pro/Whiz_100_Baseline_Replay.html. Reuse seed 707, v3 guidance for all players, the other three models, 8192 total output tokens, 240-second deadlines, six-hand/336-action limit, and no retries. Pin moonshotai/mxfp4 with low reasoning, as tested. Carry all account totals from strategy-v3-flash and subsequent OpenRouter tracer usage. Preserve historical evidence and metadata HOLDs; the user authorizes this field trial despite those HOLDs. No permanent seat assignment or Free Play. Run all prior offline gates plus test_kimi100.py before the single-use own-path workflow launch. Publish and independently verify each completed hand before proceeding; execution HOLD stops play. Never rerun the paid workflow.
