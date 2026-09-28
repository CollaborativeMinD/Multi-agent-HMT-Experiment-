# Bounded inference smoke: September 28, 2026

Result: 7 PASS, 1 HOLD. Eight requests, zero retries. No games launched.

| Model | HTTP | Result | Input tokens | Output including reasoning | Latency ms |
|---|---|---|---|---|---|
| GPT-6 Astra | 200 | PASS | 95 | 18 | 3524 |
| GPT-6 Sol | 200 | PASS | 95 | 18 | 1532 |
| Claude Fable 5.1 | 200 | PASS | 323 | 16 | 5483 |
| Claude Sonnet 5.5 | 200 | PASS | 323 | 16 | 1230 |
| Gemini 3.8 Flash | 200 | PASS | 47 | 62 | 1127 |
| Gemini 3.5 Flash-Lite | 200 | PASS | 47 | 20 | 697 |
| Qwen3.8 2.4T A95B via Alibaba | 200 | PASS | 98 | 78 | 4679 |
| Qwen3.8 Flash, Alibaba-only request | 429 | HOLD | Unknown | Unknown | 5703 |

Every PASS returned `{"action":"play","card":"2H"}`. Hearts were led, and the hand contained 2H and AS. The schema allowed either card; the independent legality check admitted only 2H. Checks also required completed generation, matching model identity, nonnegative integer usage within the reservation, and Alibaba identity for the successful Qwen response.

## Cost and bounds

Estimated successful token charges: **$0.00805185**. The unresolved HTTP 429 request retains its full **$0.00171008** reservation. Successful charges plus unresolved reservation total **$0.00976193** for bookkeeping, not a provider invoice. OpenRouter reported $0.000664 for the successful Qwen call, matching its estimate. No remaining account balances were measured.

The batch reserved $0.35872768 using 8,192 input tokens per request and a 1,024-token generation cap. Actual request bodies were at most 2,048 bytes. Input reservation is conservative, not a tokenizer proof. Every returned usage count fit its reservation. Both cohorts and all future tests still share the original $10-per-account ceilings.

## HOLD and reverse RCA

Observed output: HTTP 429 for Qwen Flash, with no admitted response or usage. The request selected the fixed model and Alibaba-only route. The same OpenRouter credential successfully served the large Qwen model immediately before it. This establishes a request-specific service rejection, not its underlying quota or capacity cause. Raw error bodies were intentionally not logged. Investigation stops at that evidenced boundary.

Disposition: INVESTIGATION_INCOMPLETE; REQUIRES_OPERATOR_ESCALATION. No automatic retry, model substitution, provider fallback, or gameplay promotion occurred. A future explicitly bounded retry or account-side quota investigation can resolve the hold; this run does not establish that a credential change is necessary.

A minor local test ResourceWarning was corrected with Path.read_text(), then all six offline test methods passed again. Mocked 429, 500, timeout, malformed/schema-invalid actions, illegal card, identity mismatch, wrong route, missing secret, and rerun rejection exercised the fail-closed boundary without paid calls.

## Evidence and reproduction

- [Live run](https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/36493005982)
- [Receipt](../evidence/inference-smoke-20260928.json)
- [Exact requests, without credentials](../config/smoke-request-profile.json)
- [SQLite ledger reconstruction](../evidence/inference-gates.sql)
- Local tests: `PYTHONPATH=scripts python -m unittest discover -s tests -p 'test_smoke.py' -v`

`request_sha256` hashes the canonical JSON body only. Model and URL are separately recorded. Both Gemini bodies therefore share a body hash while targeting different model URLs. This is not a claim that the complete HTTP requests are identical. No raw reasoning, headers, or secret values are in these artifacts.

The profile uses low effort where supported and a 512-token reasoning allocation for Qwen Flash. It is an economical integration canary, not the frontier benchmark profile. Generation settings for scored play remain pending. No conclusions about strategy, sustained availability, playing strength, or latency ranking follow from one request each.

API contracts consulted: [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs), [Claude structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs), [Claude effort](https://platform.claude.com/docs/en/build-with-claude/effort), [Gemini generateContent](https://ai.google.dev/api/generate-content), and [OpenRouter structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs).
