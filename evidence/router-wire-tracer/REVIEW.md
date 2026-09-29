# Router RCA: three-variable review

Run: https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/36521245904
Metadata reconciliation: https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/36521031839

## Findings

1. Parameter translation: OpenRouter's debug echo reported Pro max_tokens=64 unchanged, reasoning_effort=low, thinking enabled, in response to our intentional reproduction of medium. The response again reported 24640 total tokens and finish=length. This rules against numeric ceiling inflation in the echoed request. It does not establish which provider-side rule or middleware response handling caused the mismatch. Echo is OpenRouter's report, not independently captured provider ingress.
2. Accounting: all nine historical generation records matched receipts for native completion and reasoning counts. Their separate tokens_completion counts differ; our parser uses native usage correctly. Five historical truncated records had native reasoning greater than native completion. This is present in stored metadata, not introduced by our parser. Stored costs agree with recorded costs to sub-nanodollar rounding. No double-counting is demonstrated. Provider processing and special-token counting remain unobserved.
3. Reasoning demand: on the same Flash/Wafer game observation and streaming transport, low forwarded unchanged with thinking enabled, exhausted 8192 tokens in 67.635s, and produced zero visible characters. Disabling reasoning forwarded thinking.type=disabled, returned a valid choice in 0.777s, used 7 output tokens and 0 reasoning tokens. Both upstream message and schema hashes match. Choice 2 is ten of diamonds; it was not applied.

| Probe | Echoed max_tokens | Echoed thinking | Reported output | Reasoning | Seconds | Result |
|---|---:|---|---:|---:|---:|---|
| Pro boundary reproduction | 64 | enabled, low | 24640 | 24641 | 123.256 | Cap failure |
| Flash game | 8192 | enabled, low | 8192 | 8194 | 67.635 | Truncated, no visible answer |
| Flash game | 8192 | disabled | 7 | 0 | 0.777 | Valid choice |

## Disposition

Root cause is not closed globally. Numeric max_tokens translation was observed intact for these three requests. Reasoning control translation was observed: medium mapped to low for Pro; low remained low for Flash; enabled=false became thinking disabled. The accounting mismatch remains at the reported provider/gateway boundary. Pro's 24640=24576+64 pattern reproduced, consistent with separate thinking allocation, but no explicit 24576 budget appeared in the echoed body, so allocation origin remains unproven.

Flash demand ablation gives a promising operating configuration for the fourth seat, not a qualified replacement. It is one paired observation without randomized repetitions or strategic scoring. Disabling reasoning changes the experimental condition and cannot silently replace the original frontier comparison. No new model or provider route was qualified. Direct-versus-routed comparison would require direct access to the same serving endpoint; no such credential was assumed or retrieved.

The historical long waits are primarily recorded generation time, not measured gateway waiting alone. OpenRouter records streamed=true even for our earlier non-streaming client calls, which may describe upstream processing; that field's precise semantics remain unverified.

No games advanced, no rosters changed, no Free Play, no automatic retries. The current series remain on HOLD. Twenty-one diagnostic tests plus prior engine, ten runner, six smoke, and held-state gates passed before inference.

## Evidence

- ../router-rca/generation-metadata.json: nine old generation records, request IDs, upstream IDs, native counts, and cost fields.
- receipts.json: sanitized upstream controls, stream hashes, response usage, and new generation IDs.
- WIRE-01-request.json through WIRE-03-request.json: exact outgoing request bodies without authentication headers.
- summary.json: accounting and game immutability.
- gates.sqlite and gates.sql: cumulative gates and RCA. Review dispositions appended by no-inference seal job.

Debug filtering retained only controls, field names, and message/schema hashes. No raw reasoning, auth headers, or private credentials were published. Provider invoices remain authoritative.
