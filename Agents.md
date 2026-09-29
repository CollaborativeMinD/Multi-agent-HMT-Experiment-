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
