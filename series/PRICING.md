# Pricing refresh, September 28, 2026 HST

Standard text input/output USD per million tokens, unchanged from the pinned registry:

| Model | Input | Output |
|---|---:|---:|
| gpt-6-astra | 10 | 50 |
| gpt-6-sol | 2 | 10 |
| claude-fable-5-1 | 10 | 50 |
| claude-sonnet-5-5 | 2 | 10 |
| gemini-3.8-flash | .75 | 3.75 |
| gemini-3.5-flash-lite | .30 | 2.50 |
| qwen/qwen3.8-2.4t-a95b | 2 | 6 |
| qwen/qwen3.8-flash | .15 | .47 |

Primary sources checked: https://developers.openai.com/api/docs/models/gpt-6-astra ; https://developers.openai.com/api/docs/models/gpt-6-sol ; https://www.anthropic.com/claude/fable ; https://platform.claude.com/docs/en/about-claude/pricing ; https://ai.google.dev/gemini-api/docs/pricing ; https://openrouter.ai/api/v1/models .

Gemini 3.8 Flash introductory standard rates apply through December 31, 2026. No tools, cache-write directives, batch, or premium service tier is requested. Accounting uses standard token estimates and retains unknown reservations; invoices remain authoritative. Input reservation is capped at 20,000, below long-context pricing thresholds. OpenRouter is fixed to Alibaba; no route fallback.
