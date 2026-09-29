# Strict Whiz baseline pilot 2026-09-28

Authorized scope: one four-model game per cohort to 100. Strict Whiz only. No table talk, blind nil, free bidding, or automatic model/provider substitution. One fixed seed (7), same initial seat/deal schedule. North OpenAI, East Anthropic, South Google, West Qwen. North/South partner; East/West partner. No seat rotation in this pilot: outcomes describe partnerships under these deals, not individual rankings or general intelligence.

## Frozen rules

Four players, 52 cards, 13 each, spades trump. Bid nil or exactly the number of spades held. Follow suit; do not lead spades before broken unless only spades remain. Dealer's left starts; trick winner leads next; dealer rotates. Positive team contract +10 per bid trick if made, -10 if set. Overtricks +1 point and bag each. Nil +/-100 independently; nil tricks do not help partner contract and failed-nil tricks are bags even when partner is set. Ten bags -100, retain remainder. Score complete hand; at least 100 with a higher score wins, tied scores continue.

Upstream game-spades 0.1.1, kernel 1.5.0; lockfile integrity. Two explicit patches: add target 100; retain failed-nil bags on a set contract. Whiz actions are independently filtered and rejected at the transition boundary. Preserve third-party BSD-3-Clause notice.

## Frozen execution

Exact eight models and Qwen Alibaba-only routes from config/models.lock.json at the run commit. Every genuine choice calls the acting model with its own hand, public history, and enumerated legal actions. One legal action means an automatic forced transition, recorded separately, with no model call. This is legal-action-assisted evaluation, not independent rule recall. No private opponent hands, initial seed, future deals, other models' reasoning, or full observer snapshots enter a model request.

OpenAI, Anthropic, Gemini, and large Qwen: medium effort/thinking. Qwen Flash: 512-token reasoning budget. All: 1,024 generated-token cap, default sampling (no temperature override), no tools, fresh single-turn requests with current public history. This is a bounded pilot profile, not maximum-compute frontier evaluation; equivalent effort names do not imply equal compute across providers.

For each request reserve (UTF-8 request-body bytes + 2,048) input tokens plus 1,024 output tokens at locked standard prices. Reject input reservations above 20,000 or insufficient funds. Release unused reservation after reported usage; retain full reservation when usage is unknown. This is conservative accounting, not a tokenizer proof or provider invoice. $3 per account for this baseline, across both games, within the original $10 per account including prior probes. Prior probes plus unresolved reservations were below $0.02 total. Other use of those accounts is not measured.

90-second per-request deadline, 60-second socket timeout. OpenRouter: at least 30 seconds from previous request completion to next start, shared across both models. One additional attempt only after HTTP 429, after 60 seconds, with a fresh reservation. Every attempt remains in evidence. Other errors stop with HOLD. No synthetic or bot replacement of model choices. Maximum six hands per game, 45-minute workflow deadline. Hitting a bound preserves partial evidence and reports HOLD, never a fabricated winner. Campaign-wide upper bound: 672 actions, at most 1,344 attempts with all retries; budget/deadline normally bind sooner.

## Measures and records

Capture bids, nil attempts/results, contracts made/set, tricks won, bags/penalties, hand and final scores, partnership outcome; model calls vs forced actions, invalid/incomplete responses, retries, latency, cooldown, input/output usage, estimated costs, and uncertainty reservations. Full post-action observer frames, private prompt projections, engine event log, action stream, run commit, seed, and state hashes support replay. Reapply every admitted action and compare the full-state final hash before labeling replay PASS.

Baseline engine checks: scorer edge fixture (-148, 2 bags), rollover, 100-point target, tie continuation, illegal Whiz rejection, private views, and complete exact replay for seeds 1, 7, 19. Runner checks: identity/usage/action contract, private boundary, budget denial before network, forced-action labeling, one-retry bound, <=60-line functions, and headless evidence pipeline.

## Operate

From repository root:

```
npm ci --ignore-scripts --prefix baseline
python baseline/patch_engine.py
node baseline/test_engine.mjs
PYTHONPATH=scripts:baseline python -m unittest discover -s baseline -p test_runner.py -v
```

Apply the patch once after each clean npm ci. Source drift stops patching. Paid execution is the single-use baseline workflow; re-run attempts are blocked. Inspect its summary and retained artifact, even on failure. Do not invoke runner.py casually: it makes paid requests when keys exist. The workflow checks local gates before receiving secrets in the paid step. Replay and observer rendering must operate only from recorded evidence without keys.

## Amendment before resume
Run 36496016934 held after 10 accepted actions. Qwen 2.4T reported 1,291 output tokens against a 1,024-token reservation. The generic error receipt did not preserve finish reason, so truncation versus provider token-limit semantics remains unresolved. No rejected response was applied.

The continuation replays and verifies the ten accepted actions, then resumes at the held decision. All subsequent requests use a 4,096-token requested limit and reservation, with unchanged medium effort (Qwen Flash retains its 512-token reasoning budget). The continuation uses a 120-second request deadline and 110-second socket timeout to accommodate the larger output allowance. Original spend carries forward into the same $3/account pilot cap. Provider finish reason, identity, and response hash are now preserved without raw reasoning or credentials. This is an amended pilot with a mixed output-budget prefix, not a pristine uniform-budget benchmark. A clean repeat belongs in a separately authorized later evaluation.

## User-authorized 8,192-token continuation (2026-09-28 HST)
The user directed doubling the current gameplay token limit for every player and stopping at the next issue. All eight request adapters now request and reserve 8,192 output tokens. Model IDs, routes, effort settings, prompts, seed, gameplay rules, $3/account cumulative pilot budget, 120-second request deadline, and 110-second socket timeout remain as previously configured. Qwen Flash retains its separate 512-token reasoning setting. No retries are permitted in this continuation, including HTTP429.

Resume exactly 92 admitted frontier actions from run36496680649; the separate max_completion_tokens tracer decision is not admitted. Carry all original attempts and the $0.016844 diagnostic charge into cumulative accounting ($1.44642375 starting total). Preserve earlier checkpoint evidence.

Interpretation: completing this run would show that the increased allowance permits these sampled requests to progress. It would not establish server-side enforcement of a combined token cap: prior max_tokens and max_completion_tokens requests both exceeded their requested limits, and inference is stochastic. Another exception, malformed result, token breach, timeout, budget bound, or rate limit stops for reevaluation.
