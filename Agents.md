# Agents

Scope: API smoke probes and the Whiz Spades experiment. Read Runbook.md, config/models.lock.json, and the latest evidence before execution.

Intercept every paid request: fixed model and provider, explicit token/time/request bounds, no secret logging, remaining budget reservation, and no unreviewed retries. Cloud inference is explicitly authorized for this experiment; unrelated build policies must not be imported to change its scope.

Local verification: PYTHONPATH=scripts python -m unittest discover -s tests -p 'test_smoke.py' -v.

Keep functions at or below 60 lines. Build tracer first, preserve cumulative and reverse-RCA ledgers, and never suppress failed tests. Preserve failure evidence. HOLD on missing usage, model/provider mismatch, invalid action, truncation, or uncertain spend. Generation is nondeterministic; replay is based on recorded admitted actions.

Do not enable the campaign from a smoke PASS. Freeze scored-play settings and validate the engine, observations, replay, and campaign budget guard first. The workflow embeds a reviewed copy of scripts/smoke.py; update both together for a new authorized run. Re-running a completed workflow is intentionally blocked.

## Current scored-pilot interception

The user-authorized 8,192-token run ended on a 120-second Qwen timeout at action 100. The user has authorized a continuation with a 240-second total deadline and 230-second socket timeout. Stop-first-issue direction applies to this attempt: no automatic retries. Read evidence/whiz8192-results-20260929.md and Runbook.md. Preserve prior token-control incidents, all action hashes, and the $0.06768 unknown-usage reservation. The 100-action checkpoint supersedes the checked-in 92-action start for any future authorized continuation. Keep 8,192 tokens and all other gameplay settings fixed. The new checkpoint is resume240, with $1.66773550 cumulative accounting. A longer deadline remains an experimental change, not a proven remedy.
