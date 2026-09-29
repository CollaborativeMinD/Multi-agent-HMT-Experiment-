# Pro thinking-off qualification review

## Disposition

**Inference checks: 12/12 PASS. Full qualification: HOLD.** Nine native generation records reconcile; three return HTTP 404 on both the initial and one reviewed delayed read-only lookup. Missing records are not evidence of a token mismatch, nor proof of an eventual-consistency cause.

No scored move or roster change was applied. This evaluates the thinking-disabled configuration specifically, not Pro's frontier reasoning configuration.

## Matrix and results

| Category | Calls | Criterion | Result |
|---|---:|---|---|
| Known answers | 4 | Correct arithmetic under permuted answer indices; follow suit; strict Whiz bid rule | 4/4 |
| Identical held observation | 3 | Pinned model/route, legal JSON choice, bounded output | 3/3 |
| Other replayed observations | 3 | Same controls, one bidding and two playing states | 3/3 |
| Deliberate cutoff | 2 | One-token cap, length finish, zero reasoning tokens | 2/2 |

Every echoed request showed thinking disabled and the requested cap unchanged. Every response reported zero reasoning tokens. Ordinary responses used 6–7 output tokens; both cutoff responses reported exactly 1. The cutoff PASS means expected truncation, not valid gameplay JSON.

The four unique game observations were reconstructed by replaying the original 102 actions and checking every resulting state hash. There were six game calls because the held observation was repeated three times. Legal options were supplied by the engine, so legality is an assisted-interface result, not proof that the model independently derived every rule.

## Variability

Identical held-state requests selected indices 1, 0, and 2, covering all three legal cards. Their client latencies were 100.739s, 0.693s, and 0.799s. The historical thinking-off probe on this state selected index 2 in 0.637s.

This does not establish random play, deterministic play, or strategic quality. The echoed sampling temperature was 1. Repeated choices may differ legitimately; no optimal-move oracle or partner outcome evaluation was used.

The other replayed game states took 10.033s, 0.583s, and 0.585s. All stayed inside the inherited 240-second deadline. The slowest call's stored generation_time was 100632ms, close to the client duration, while metadata latency was 2095ms. The delay is reflected in upstream metadata, but the internal cause and precise field semantics are unproven. Zero reported reasoning tokens does not independently establish the absence of all internal computation.

## Receipt availability incident

PRO-OFF-10, PRO-OFF-11, and PRO-OFF-12 each returned HTTP 404 from the generation metadata endpoint twice. Their streaming usage receipts and generation IDs are preserved. The original summary remains HOLD, and the delayed lookup has a separate qualification artifact and cumulative RCA entry. No inference was retried.

The verification workflow deliberately failed its qualification gate rather than marking missing receipts successful. The paid workflow completed successfully as an evidence-collection job; that job status is not the qualification verdict.

## Controls and accounting

- Exact model: deepseek/deepseek-v4-pro-0813; route: Wafer only; no fallback.
- Thinking disabled; 12-call maximum; 30-second post-call gap; 240-second deadline.
- $0.50 admission budget, with conservative output reservations including the earlier observed allowance.
- Stop on any unexpected inference failure; expected one-token truncation declared before execution.
- 28 diagnostic unit tests plus hosted engine, runner, and smoke regression gates passed before paid execution.
- Cost accounted: **$0.0045826**. OpenRouter cumulative accounted: **$1.0982313190**. Invoices remain authoritative.
- Original game evidence unchanged; zero model actions applied; no Free Play.

## Operator evidence

- [Paid run](https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/36527010768)
- [Read-only reconciliation run](https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/36527733026)
- [Frozen plan](../evidence/pro-off-eval/plan.json)
- [Streaming receipts](../evidence/pro-off-eval/receipts.json)
- [Original summary](../evidence/pro-off-eval/summary.json)
- [Delayed metadata](../evidence/pro-off-eval/delayed-metadata.json)
- [Final qualification](../evidence/pro-off-eval/qualification.json)
- [Cumulative SQLite export](../evidence/pro-off-eval/gates.sql)
- [Evidence checksums](../evidence/pro-off-eval/SHA256SUMS.txt)

The configuration has stronger bounded-response evidence than before. It is not admitted as the fourth frontier seat: complete metadata reconciliation remains open, strategic quality remains untested, and disabling reasoning changes the benchmark profile.
