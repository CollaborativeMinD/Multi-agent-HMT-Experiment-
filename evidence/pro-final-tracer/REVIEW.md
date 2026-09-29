# Final Pro token-semantics RCA

## Verdict

The thinking-enabled Pro/Wafer route does not satisfy our total-output ceiling. A predeclared cap-slope prediction succeeded: 128 requested tokens produced 24,704 reported output tokens, exactly 24,576 + 128. Earlier 64-token boundary probes reported 24,640, exactly 24,576 + 64. This is evidence of an additive allowance associated with the thinking-enabled path, not evidence that our client changed the number.

Turning thinking off returned bounded, schema-valid responses on both the identical boundary task and the held game observation. This qualifies the tested responses, not a frontier seat or general reliability.

## Final three-call experiment

| Probe | Thinking | Requested cap | Reported total | Reasoning | Seconds | Admission |
|---|---|---:|---:|---:|---:|---|
| PRO-01 boundary | low | 128 | 24704 | 24704 | 184.435 | HOLD |
| PRO-02 same boundary | disabled | 128 | 7 | 0 | 0.782 | PASS |
| PRO-03 held game | disabled | 8192 | 6 | 0 | 0.637 | PASS |

PRO-01 finished with length and no visible answer. Unlike several historical truncated responses, its reasoning count equals its total, so this particular overrun does not depend on an inconsistent usage partition.

PRO-02 selected choice 2, explicitly allowed as "uncertain." This establishes formatting and accounting coherence, not arithmetic correctness. PRO-03 selected choice 2, the legal ten of diamonds. No move was applied or strategically scored.

## Causal evidence and limits

- Model and route remained deepseek/deepseek-v4-pro-0813 and Wafer, without fallback.
- OpenRouter's upstream debug echo preserved max_tokens: 128 in both boundary requests.
- Upstream boundary message and response-schema hashes matched. The intended intervention changed low/enabled thinking to disabled thinking, removing reasoning_effort.
- With thinking enabled, the observed total shifted by exactly 64 when the requested ceiling shifted from 64 to 128. The implied offset stayed 24,576.
- No explicit 24,576 budget appeared in the echoed body. The behavior is consistent with a default internal reasoning allowance, but neither its implementation location nor intended semantics is established.
- OpenRouter supplies both the echo and generation metadata. These are not independent Wafer ingress logs or a direct-provider control. We cannot assign responsibility exclusively to OpenRouter, Wafer, or model-serving code.
- The tracer does not tokenize or retain raw reasoning. Reported and billed token counts do not independently prove exactly how many internal tokens were generated.
- One thinking-off response per task cannot establish reliable cap enforcement under sustained pressure. The short disabled boundary answer did not exercise the 128-token cutoff.
- Disabling reasoning changes the evaluated configuration. It must not silently replace a frontier reasoning configuration.

Wafer's public [Serverless documentation](https://docs.wafer.ai/serverless), inspected for this review, shows max_tokens usage but does not document a 24,576-token reasoning allowance.

## Evidence and disposition

[Paid run](https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/36523068821), [receipts](receipts.json), [summary](summary.json), and saved request bodies contain the reproducible controls. Raw reasoning and credentials were not stored.

Three inference calls, no retries, zero game actions. Original game evidence was fingerprint-verified unchanged. Cost: $0.1046598. OpenRouter cumulative accounted: $1.0936487190, including earlier usage and retained reservations. Provider invoices remain authoritative.

Thinking-on Pro remains HOLD. Thinking-off Pro and Flash are candidate configurations for subsequent qualification, not approved seat substitutions. Both strict series remain HOLD; no Free Play. This closes the bounded experiment with a reproducible behavioral isolation and unresolved internal attribution.
