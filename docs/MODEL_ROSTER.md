# Whiz Spades model roster

Roster version: 2026-09-28.1. Eight model identities selected and registry-verified; inference and game execution remain pending.

## Two cohorts

| Account / lab | Frontier cohort | Mainstream / lower-cost cohort | Standard input / output USD per million tokens, frontier; mainstream |
|---|---|---|---|
| OpenAI | `gpt-6-astra` | `gpt-6-sol` | $10 / $50; $2 / $10 |
| Anthropic | `claude-fable-5-1` | `claude-sonnet-5-5` | $10 / $50; $2 / $10 |
| Google Gemini | `gemini-3.8-flash` | `gemini-3.5-flash-lite` | $0.75 / $3.75; $0.30 / $2.50 |
| Qwen through OpenRouter | `qwen/qwen3.8-2.4t-a95b` | `qwen/qwen3.8-flash` | $2 / $6; $0.15 / $0.47 |

The machine-readable selection is [config/models.lock.json](../config/models.lock.json). The budget is $10 per account and $40 combined across BOTH cohorts, including smoke tests, retries, and games. These are required ceilings for the future runner, not an implemented spending guard. Reasoning tokens can dominate cost. No inference requests have been made by the registry check.

## Selection rationale and limits

- OpenAI: Astra is the provider's most capable general model; Sol provides a contemporary, substantially cheaper capable counterpart. Luna would represent the smallest efficiency tier instead.
- Anthropic: Fable 5.1 is recommended for demanding reasoning; Sonnet 5.5 supplies the speed/intelligence tier. Opus 5.5 can lead on particular coding tasks, so this choice is not a universal superiority claim. Sonnet 5.5 was released on the freeze date and its exact ID passed the account metadata check.
- Google: the September 2 launch describes 3.8 Flash as Google's best reasoning and coding model. Selecting the older 3.1 Pro merely because of its name would be misleading. Flash-Lite 3.5 provides a currently supported lower-cost tier. This pair has a larger capability-tier separation than some other pairs, which must be disclosed in results.
- Qwen: retain the requested cloud-hosted open-weight slot and use the large 2.4T/A95B model against Flash from the same family. This is the frontier OPEN-WEIGHT selection, not a claim that it exceeds every proprietary Qwen Max service. The published licenses are `qwen3.8-max` and `qwen-community-1.0`; do not describe them as unrestricted open source. OpenRouter is the billing gateway, Qwen the model lab, and Alibaba the selected inference provider for both.

"Mainstream" is our operational label for lower-cost general use. It is not evidence of market share or a reproduction of the hidden routing, prompts, and tools inside consumer chat apps. Capability labels are selection hypotheses; Whiz performance is what we will measure.

## What is pinned

- Eight explicit model IDs. No `latest`, automatic model router, or backup model list.
- Both Qwen calls must send `provider: {"only": ["alibaba"], "allow_fallbacks": false, "require_parameters": true}`. An unavailable route stops that participant rather than swapping providers.
- OpenRouter catalog canonical slugs are recorded as evidence, not assumed to be callable snapshot IDs. The checked request IDs remain the published catalog IDs. Serving quantization is reported as unknown.
- Anthropic documents these dateless IDs as fixed snapshots. OpenAI publishes the selected IDs without separate dated alternatives on the checked pages. Gemini IDs are stable, but no endpoint pin promises deterministic outputs or permanent availability.
- Preserve the returned model/version, provider identity, request settings, usage, prompt hash, and commit in every eventual run receipt. Gemini 3.8 returned a generic `version: 3.0` in metadata; preserve it verbatim rather than inventing a more specific revision.

Generation settings are deliberately marked pending in the lock file. The next gate is a bounded inference smoke test that establishes valid request parameters and billable usage for every model. Freeze reasoning effort, output caps, timeouts, and retries before scored play. Do not present equally named reasoning levels across labs as equal compute.

## Evidence and release gates

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Credentials and API metadata | PASS | Existing API-access receipt |
| Eight exact model identities | PASS | [Registry receipt](../evidence/model-pins-20260928.json), eight HTTP 200 responses |
| Fixed Qwen provider availability | PASS for public metadata | Alibaba endpoints present for both models |
| Paid inference, structured action, usage accounting | PENDING | One bounded smoke request per model; registry success does not prove entitlement or quota |
| Campaign cost guard and experiment settings | PENDING | Reserve maximum request cost before dispatch, count both cohorts, freeze execution settings |
| Scored games and replay | PENDING | Same deals and observations, seat/partner rotation, legal-action validation, complete action log |

The verification workflow makes at most eight GET requests, does not follow redirects, has no retries, and logs allowlisted metadata only. It makes no token-generation requests. Local checks rejected incorrect model identities and validated route selection and missing-secret handling. [Successful workflow run](https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/36492155237).

For results, report within-cohort outcomes and matched within-lab changes. Rotate seats and partners and reuse deal schedules. Publish cost, latency, invalid actions, failed bids, nil outcomes, and uncertainty alongside wins. A limited-budget pilot cannot establish a general intelligence ranking. Replay should reconstruct logged game actions without API keys; rerunning inference may yield different actions.

## Sources checked September 28, 2026

- [OpenAI Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) and [Sol](https://developers.openai.com/api/docs/models/gpt-6-sol)
- [Anthropic models](https://platform.claude.com/docs/en/models/overview) and [snapshot semantics](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions)
- [Google 3.8 launch](https://blog.google/innovation-and-ai/models-and-research/gemini-models/3-8-flash-and-3-8-flash-cyber/), [Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite), and [pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Qwen large model card](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B) and [Flash model card](https://huggingface.co/Qwen/Qwen3.8-Flash-Next)
- OpenRouter [large-model endpoints](https://openrouter.ai/api/v1/models/qwen/qwen3.8-2.4t-a95b/endpoints), [Flash endpoints](https://openrouter.ai/api/v1/models/qwen/qwen3.8-flash/endpoints), and [routing controls](https://openrouter.ai/docs/guides/routing/provider-selection)

Prices describe standard short-context text, excluding caching, special processing modes, and other fees. Gemini 3.8 introductory pricing expires December 31, 2026. Recheck rates before any campaign.
