# Agents

Scope: API smoke probes and the Whiz Spades experiment. Read Runbook.md, config/models.lock.json, and the latest evidence before execution.

Intercept every paid request: fixed model and provider, explicit token/time/request bounds, no secret logging, remaining budget reservation, and no unreviewed retries. Cloud inference is explicitly authorized for this experiment; unrelated build policies must not be imported to change its scope.

Local verification: PYTHONPATH=scripts python -m unittest discover -s tests -p 'test_smoke.py' -v.

Keep functions at or below 60 lines. Build tracer first, preserve cumulative and reverse-RCA ledgers, and never suppress failed tests. Preserve failure evidence. HOLD on missing usage, model/provider mismatch, invalid action, truncation, or uncertain spend. Generation is nondeterministic; replay is based on recorded admitted actions.

Do not enable the campaign from a smoke PASS. Freeze scored-play settings and validate the engine, observations, replay, and campaign budget guard first. The workflow embeds a reviewed copy of scripts/smoke.py; update both together for a new authorized run. Re-running a completed workflow is intentionally blocked.

## Campaign interception

The authorized 240-second continuation completed both strict games. Read evidence/whiz240-results-20260929.md and Runbook.md. The user has subsequently authorized the strict 300-point best-of-five campaign only, as frozen in series/plan.json and series/PROTOCOL.md. Preserve earlier token-control incidents and the $0.06768 unknown-usage reservation. Opening cumulative accounting is $2.14137450. Admit requests only under the $9.98/account guard plus $0.02/account prior-probe buffer. Stop at first issue, never retry or substitute automatically. Publish and verify each hand before admitting the next. Free Play is explicitly prohibited. Both complete replays contain 112 actions; resume240 remains their historical 100-action frontier starting checkpoint. No new call exceeded 120 seconds, so do not claim that a longer deadline was necessary or that provider-side token enforcement was established.

## Pro thinking-off qualification boundary

Read docs/PRO_OFF_REVIEW.md and evidence/pro-off-eval/qualification.json before further model qualification. Preserve the 12/12 inference result and separate 9/12 metadata reconciliation result. Full qualification remains HOLD after three generation IDs returned 404 twice. Do not suppress that gate or retry inference to manufacture replacement receipts. Thinking-disabled Pro is a distinct evaluation profile, and these checks do not authorize a frontier seat change, scored play, or Free Play.

## Authorized Pro 100-point field trial

The user's subsequent order authorizes one fresh strict 100-point cohort-1 game with thinking-disabled DeepSeek Pro in p4 despite the preserved metadata qualification HOLD. Flash thinking-disabled is selected for cohort 2 p4; no cohort-2 game is started by this order. Read config/seat-selections.json. The trial uses seed 707, up to six hands, 8192 tokens, a 240-second request deadline, existing per-account budget ceilings, and no automatic retries. Earlier series remain immutable. Run trials/test_pro100.py offline before trials/pro100.py; the latter is paid and single-use. Inspect evidence/pro100/summary.json, gates.sql, and frontier-pro/Whiz_100_Baseline_Replay.html after each verified hand. HOLD stops play. No Free Play.

## Authorized matched Flash cohort-1 trial

The user authorizes one strict 100-point game substituting thinking-disabled deepseek/deepseek-v4.1-flash for Pro in cohort 1 seat p4. Reuse seed 707, initial game state, the other three models and settings, rules, 8192-token cap, 240-second deadline, six-hand bound, and no automatic retries. Provider remains Wafer. Fresh model decisions may cause trajectories to diverge. Begin cumulative accounting from evidence/pro100/summary.json. Preserve both earlier series and all Pro game files by hash. Run trials/test_flash100.py before the paid, single-use trials/flash100.py. Inspect evidence/flash100/summary.json and frontier-pro/Whiz_100_Baseline_Replay.html, where the internal frontier-pro ID is deliberately retained to match initial state exactly. The final model label identifies Flash. No cohort-2 game or Free Play is authorized by this trial.

## Nil-explicit v2 reruns

The user authorizes a neutral nil-definition clarification and one new 100-point game each for Pro and Flash. Only replace the original `Nil +/-100;` clause with an explicit zero-tricks/+100 and one-or-more-tricks/-100 definition. Every player receives the same revised rules. Use seed 707, existing cohort-1 seats, thinking-disabled Pro/Flash, prior limits, and unchanged engine rules. Run trials/test_nil100.py plus previous regression gates before trials/nil100.py pro, followed by trials/nil100.py flash only if Pro completes. Start account totals and cumulative ledgers from the last completed Flash trial, then carry Pro v2 usage into Flash v2. Preserve original Pro/Flash and series evidence. Each new directory evidence/nil-v2-pro or evidence/nil-v2-flash records prompt-delta.json with old/new text and hashes, plan, call receipts, verified score, cumulative gates, and replay. No inference retries or Free Play. Do not interpret one run per condition as proof of prompt causality.


## Strategy-guided v3 reruns

The user authorizes one new strict 100-point game each for Pro and Flash, appending the approved partnership-strategy paragraph to the nil-explicit v2 prompt. All four players receive identical guidance. Preserve seed 707, seats, candidate thinking-disabled settings, 8192-token cap, 240-second deadline, six-hand bound, and no retries. Run all offline gates before trials/strategy100.py pro, then flash only if Pro completes. Carry cumulative accounting from evidence/nil-v2-flash/summary.json, including the Anthropic HTTP 529 unknown-usage reservation. The prior Flash v2 game remains HOLD; these are fresh conditions, not a retry of that game. Freeze cumulative account ceilings in config/strategy-v3-budget.json, retaining the $0.02/account buffer. An announced top-up alone does not specify a new numeric ceiling.

Each hand verifies replay, private views, scores, and historical evidence hashes, publishes summary, receipts, HTML replay, and cumulative SQL, and updates the README. Inspect evidence/strategy-v3-pro or evidence/strategy-v3-flash. No Free Play. Do not infer prompt causality or individual rankings from one game per condition. Backend sampling parity remains unproven.


## Authorized Kimi/Mistral seat tracers

Read docs/SEAT_TRACER.md. The user authorizes up to ten isolated calls, $2 batch admission under the existing cumulative OpenRouter guard, with no retries, fallback, game moves, or seat changes. Run all offline workflow gates first. Inspect evidence/seat-tracer-kimi-mistral. This supersedes earlier restrictions only for these bounded probes.


## Authorized Kimi cohort-1 field evaluation

The user authorizes one strict 100-point game with Kimi K3 in p4, partnered with Anthropic. Read trials/kimi100.py and inspect evidence/kimi100/plan.json, summary.json, gates.sql, and frontier-pro/Whiz_100_Baseline_Replay.html. Reuse seed 707, v3 guidance for all players, the other three models, 8192 total output tokens, 240-second deadlines, six-hand/336-action limit, and no retries. Pin moonshotai/mxfp4 with low reasoning, as tested. Carry all account totals from strategy-v3-flash and subsequent OpenRouter tracer usage. Preserve historical evidence and metadata HOLDs; the user authorizes this field trial despite those HOLDs. No permanent seat assignment or Free Play. Run all prior offline gates plus test_kimi100.py before the single-use own-path workflow launch. Publish and independently verify each completed hand before proceeding; execution HOLD stops play. Never rerun the paid workflow.

## Gemini 4 Argon admission boundary

The user authorized checking whether Gemini 4 Argon can enter the Whiz evaluation system. Read docs/GEMINI4_ARGON_TRACER.md and evidence/gemini4-argon-discovery. The authenticated Gemini API catalog enumerated 61 models and exposed no `gemini-4`, `gemini 4`, or `argon` match. Status is HOLD: `MODEL_NOT_EXPOSED_TO_API_KEY`. No inference call, game action, spend, seat mutation, or retry occurred. Existing Google seats remain South/p3: `gemini-3.8-flash` frontier and `gemini-3.5-flash-lite` mainstream. Do not infer API availability from announcement screenshots; a new discovery window requires explicit authorization.
