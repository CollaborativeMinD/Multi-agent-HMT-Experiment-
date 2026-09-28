# Qwen spaced retest, 2026-09-28

Result: both models PASS. All eight roster members now have at least one passing inference canary across the initial run and this retest. Campaign remains disabled.

| Model | HTTP | Legal action | Latency | Provider-reported USD |
|---|---|---|---|---|
| Qwen3.8 2.4T A95B | 200 | 2H | 3.661 seconds | 0.000652 |
| Qwen3.8 Flash | 200 | 2H | 2.578 seconds | 0.00004384 |

The completion-to-next-start gap was 30.000367 seconds. Total reported retest cost: $0.00069584. Same order, identical request body hashes, original token limits, Alibaba-only routing, and zero automatic retries. Two requests only. The original 429 evidence remains intact. Its conservative $0.00171008 cost reservation remains unresolved; this success is not retrospective billing reconciliation.

This clears the basic Flash inference HOLD. It does not isolate the earlier failure's cause: both elapsed time and request spacing changed. One passing retest does not establish a sustained rate limit or guarantee that 30 seconds is necessary or sufficient. Rate-limit headers are allowlisted only for numeric Retry-After values if another HTTP failure occurs.

For gameplay, measure model response latency separately from deliberate provider cooldown and any human-facing turn clock. The 30-second cooldown is an operational precaution tested here, not a measured thinking time or a finalized game rule. Preserve comparable thinking/token policies when setting the scored campaign profile.

Local regression: six original test methods passed. A mocked two-request run verified unchanged order and one 30-second gap. Live receipts verified request identity, exact model/provider, legal JSON, completion, and usage; SQLite integrity check passed. Root cause remains INVESTIGATION_INCOMPLETE while bounded recovery is evidenced.

[Live run](https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/36494065776) · [Receipt](../evidence/qwen-retest-20260928.json) · [Request profile](../config/qwen-retest-profile.json) · [Cumulative SQLite reconstruction](../evidence/qwen-retest-gates.sql)
