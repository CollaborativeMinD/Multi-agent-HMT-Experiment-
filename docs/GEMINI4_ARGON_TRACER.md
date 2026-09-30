# Gemini 4 Argon admission tracer

Scope: determine whether the repository's existing Gemini API credential can see a Gemini 4 / Argon model in the authenticated Gemini API catalog. This phase performs metadata requests only and makes **no inference calls**.

## Gates

1. Run all existing offline regression suites.
2. Enumerate the authenticated Gemini model catalog with a bounded page count.
3. Persist only normalized model identity, supported generation methods, and token limits for entries matching `gemini-4`, `gemini 4`, or `argon`.
4. Do not log credentials, raw response bodies, or model descriptions.
5. PASS only when at least one matching model is actually exposed to the configured API key.
6. HOLD on no match, malformed metadata, pagination overflow, or transport failure.
7. A discovery PASS does **not** authorize a scored game, permanent seat change, or paid inference. Exact model ID, API contract, pricing, and a separately bounded inference tracer must be reviewed first.

Gemini currently occupies South / p3 in both baseline cohorts: `gemini-3.8-flash` in frontier and `gemini-3.5-flash-lite` in mainstream. Existing seats and historical evidence remain unchanged by this tracer.
