# Human–Machine Teaming: Whiz Spades Evaluation

A reproducible experiment in partnership decisions under hidden information, built by Charles Austin and his human–machine team. Models select legal actions; a deterministic game engine enforces the rules, accounts for consequences, and produces replayable evidence.

## Completed 100-point baseline

| Cohort | OpenAI + Google | Anthropic + Qwen | Hands |
|---|---:|---:|---:|
| Frontier | **134** | −175 | 2 |
| Mainstream | **132** | −130 | 2 |

[Baseline results](evidence/whiz240-results-20260929.md) · [Download baseline replay](evidence/Whiz_100_Complete_Replay.html) · [Baseline run](https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/36506341980)

All 224 baseline actions and four hand scores were verified. The baseline involved token/deadline amendments and is retained as a pilot, not a uniform-compute ranking.

<!-- WHIZ300:BEGIN -->
## Strict 300-point best-of-five

Status: **HOLD**. Updated 2026-09-29T02:43:28.592596+00:00.

First partnership to three game wins takes its cohort series. Free Play is **not authorized**.

| Cohort | OpenAI + Google wins | Anthropic + Qwen wins |
|---|---:|---:|
| frontier | 0 | 0 |
| mainstream | 0 | 0 |

| Game | Status | Hands | N/S score | E/W score | Replay |
|---|---|---:|---:|---:|---|
| frontier-g01 | HOLD | 1 | 142 | -84 | [Download HTML](evidence/whiz300/frontier-g01/replay.html) |
| mainstream-g01 | IN_PROGRESS | 1 | 140 | 63 | [Download HTML](evidence/whiz300/mainstream-g01/replay.html) |

Replay links open repository files. Download the HTML and open it locally for playback.

| Account | Cumulative accounted USD |
|---|---:|
| openai | 0.953194 |
| anthropic | 2.154230 |
| gemini | 0.38181395 |
| openrouter | 0.69183661 |

Accounting includes prior pilot usage and its unresolved $0.06768 timeout reservation. Each account retains a separate $0.02 probe buffer under its original $10 ceiling. Provider invoices are authoritative.

[Live Actions run](https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/36512137292) · [Machine-readable status](evidence/whiz300/series.json) · [Cumulative gates](evidence/whiz300/gates.sql)

<!-- WHIZ300:END -->

## Players and protocol

| Seat / team | Frontier | Mainstream |
|---|---|---|
| North / N+S | `gpt-6-astra` | `gpt-6-sol` |
| East / E+W | `claude-fable-5-1` | `claude-sonnet-5-5` |
| South / N+S | `gemini-3.8-flash` | `gemini-3.5-flash-lite` |
| West / E+W | `qwen/qwen3.8-2.4t-a95b` | `qwen/qwen3.8-flash` |

Strict Whiz: bid nil or your spade count, follow suit, and observe the spades lead restriction. The series uses games to 300, first to three wins, and matched seeds 101, 202, 303, 404, 505. Fixed partnerships and seats. Each choice has an 8,192-token allowance and 240-second deadline. No automatic retries or provider fallback. [Full series protocol](series/PROTOCOL.md) · [Machine-readable plan](series/plan.json) · [Pinned registry](config/models.lock.json).

Models see their own hand and public history. Observer replays reveal all hands only for inspection. Forced single-option moves are labeled and incur no model call. Raw reasoning and credentials are never recorded. These games do not establish individual intelligence rankings, causal latency diagnoses, or provider token-limit enforcement.

## Reproduce and inspect

Read [Runbook.md](Runbook.md) for offline setup and verification, and [Agents.md](Agents.md) for execution boundaries. Evidence is published after each verified hand, with recorded actions, private prompt projections, complete state hashes, independent scoring, estimated usage, retained uncertainty reservations, and replay HTML. Download an HTML replay, open it in a browser, choose the game, and press Play. C toggles recording mode.

API keys belong in GitHub Actions secrets, never repository files. The original ceiling is $10 per provider across probes and campaigns. Spending guards may stop a series before a winner is decided.

## Attribution

Game engine: `@game-hub/game-spades@0.1.1` and `@game-hub/kernel@1.5.0`, with explicit target-score and failed-nil bag patches. [Third-party BSD-3-Clause notice](baseline/THIRD_PARTY_LICENSE.txt). See the source, tests, and cumulative gate records for the exact extensions.

## Reviewed recovery after the first 429

The first series run published frontier hand 1 at 142 to −84, then held on Qwen Flash's opening mainstream bid. The provider gap was 35.7255 seconds, above the configured 30 seconds. The exact upstream limit remained unknown. A single agent-reviewed recovery at the saved bid uses a further 60-second cooldown and bounded rate-limit metadata capture. It preserves the original failed receipt and reservation, and resumes the series only on a valid response. Another failure holds. This is separate from automatic retries, which remain disabled. [Recovery protocol](series/PROTOCOL.md#reviewed-recovery-after-first-429).


## DeepSeek isolated diagnostic batch

No game moves applied. Both series remain on HOLD. Provider: Wafer; retries: zero.

| Model | Case | Result | Output/cap | Seconds |
|---|---|---|---:|---:|
| deepseek-v4-pro-0813 | canary | PASS | 22/1024 | 0.78 |
| deepseek-v4-pro-0813 | boundary | HOLD | 24640/64 | 143.26 |
| deepseek-v4-pro-0813 | game | HOLD | 15842/8192 | 105.37 |
| deepseek-v4.1-flash | canary | PASS | 24/1024 | 0.50 |
| deepseek-v4.1-flash | boundary | TRUNCATED_AS_BOUNDED | 64/64 | 1.34 |
| deepseek-v4.1-flash | game | TRUNCATED_AS_BOUNDED | 8192/8192 | 100.76 |

Diagnostic accounted cost: $0.17678838. Separate from frozen series accounting. [Receipts](evidence/deepseek-diagnostic/receipts.json). Truncation tests the boundary, not a usable game action. One probe per condition cannot establish reliability.

**Reviewed verdict:** neither configuration qualifies as a replacement yet. Pro exceeded both tested pressure ceilings. Flash respected the reported total caps but truncated the game response. Some reasoning counters exceeded reported totals, so detailed usage consistency remains unresolved. [Full diagnostic review](evidence/deepseek-diagnostic/REVIEW.md). No game actions applied.


## Flash supported low-effort tracer

Same Wafer route, held observation, and 8192 game cap. Prior medium effort is not advertised in the live model catalog. Exact reasoning budget not advertised; this tracer uses supported low. No game moves applied.

| Probe | Case | Response | Total/cap | Reasoning | Seconds | Admission |
|---|---|---|---:|---:|---:|---|
| FLASH-LOW-01 | boundary | TRUNCATED_AS_BOUNDED | 64/64 | 69 | 1.06 | HOLD |
| FLASH-LOW-02 | game | PASS | 7096/8192 | 7090 | 95.29 | PASS |
| FLASH-LOW-03 | game | TRUNCATED_AS_BOUNDED | 8192/8192 | 8194 | 109.64 | HOLD |

Cost accounted: $0.0109330942. OpenRouter cumulative including both diagnostic batches: $0.8795580842. [Receipts](evidence/flash-low-tracer/receipts.json). Three probes cannot establish general reliability or move quality. Original series remain on HOLD.

**Flash tracer verdict:** one of two identical game requests passed under supported low effort; the repeat truncated. Reported total caps held, but both truncated responses had reasoning counts exceeding their totals. Candidate remains HOLD for replacement. [Review and interpretation](evidence/flash-low-tracer/REVIEW.md).

## Router RCA: translation, accounting, and demand

Upstream echo preserved requested numeric token ceilings. Pro still exceeded 64 with 24640 reported tokens. Nine historical generation records confirmed our native-token parsing; truncated reasoning counters remain inconsistent. On the same Flash/Wafer game state, thinking low truncated at 8192 tokens in 67.635s, while thinking disabled returned a valid choice with 7 output tokens in 0.777s. This is a candidate configuration, not a qualified replacement or a model-quality ranking. No game moves applied. [Full RCA review](evidence/router-wire-tracer/REVIEW.md).

Wire tracer accounted cost: $0.1094308348. OpenRouter cumulative accounted including all diagnostics: $0.9889889190.

## Final Pro token-semantics isolation

The predeclared additive prediction reproduced: thinking-low Pro with a 128-token cap reported 24,704 tokens, exactly 24,576 + 128. Its upstream echo preserved the cap. The same boundary with thinking disabled returned 7 tokens in 0.782s; the held game returned a legal choice in 6 tokens and 0.637s. Both disabled responses passed, but this does not qualify a frontier replacement or establish strategic quality. The responsible internal layer remains unproven. [Full review](evidence/pro-final-tracer/REVIEW.md).

Three calls, no retries, zero applied moves, unchanged game evidence. Batch cost: $0.1046598. OpenRouter cumulative accounted: $1.0936487190. Thinking-enabled Pro and both series remain HOLD.

## Pro thinking-off qualification

**12/12 inference checks passed; full qualification remains HOLD.** Four known-answer checks, six game-observation calls across four replay-verified states, and two deliberate one-token cutoffs passed. All responses reported zero reasoning tokens. Ordinary outputs used 6–7 tokens; both cutoffs stopped at 1.

Identical game requests chose all three legal options, with latencies of 100.739s, 0.693s, and 0.799s. Strategic quality and decision consistency are not established. Nine stored generation records matched; the remaining three returned 404 twice, including a reviewed delayed lookup. Missing metadata is not a token mismatch. [Full qualification review](docs/PRO_OFF_REVIEW.md).

Batch accounted cost: $0.0045826. OpenRouter cumulative accounted: $1.0982313190. No game moves, retries of inference, roster changes, or Free Play.

## Pro strict 100-point field trial: COMPLETE

OpenAI + Google defeated Anthropic + thinking-disabled Pro **132 to -195**, in two hands. Pro bid nil twice and failed twice, taking two and three tricks. In hand 1 it broke nil by playing QH over its partner's TH with a legal losing 4H available. This is specific adverse playing evidence, not an individual-model ranking.

All 22 Pro calls passed; zero reported reasoning tokens, 154 output tokens total. Median latency 0.640s; maximum 61.898s. All 112 game actions, private views, and independent hand scores verified. Pro cost $0.0115508; total game cost $1.57317205. No retries or changes to earlier series evidence.

[Full field-trial review](docs/PRO100_REVIEW.md) · [Download HTML replay](evidence/pro100/frontier-pro/Whiz_100_Baseline_Replay.html) · [Summary and account totals](evidence/pro100/summary.json). Flash is the user's selected cohort-2 fourth seat; no cohort-2 game ran in this trial. Free Play remains disabled.

## Matched Flash versus Pro trial: COMPLETE

With the same seed, deals, other three models, rules, and client limits, Anthropic + thinking-disabled Flash lost **-207 to 135**. Anthropic + thinking-disabled Pro previously lost **-195 to 132**. Both games completed two hands. Flash passed 23/23 calls with zero reported reasoning tokens, median latency 0.866s, and maximum 1.265s. Pro passed 22/22, with median 0.640s and maximum 61.898s.

At their first differing action, both received the same observation after bidding nil. Pro played 8D under partner JD; Flash played KD and subsequently won the trick, breaking nil. The final scores are team outcomes on diverging trajectories, not individual rankings. The shared prompt leaves nil's zero-trick condition implicit, and effective backend sampling parity is unproven. [Full comparison and limits](docs/PRO_FLASH_100_COMPARISON.md) · [Flash replay](evidence/flash100/frontier-pro/Whiz_100_Baseline_Replay.html).

All six offline comparison checks passed, including matching deals and unchanged Pro evidence. Flash game cost $1.4172806985 across all accounts; Flash itself $0.0020409485. OpenRouter cumulative accounted: $1.1118230675. No further games or Free Play started.


## Nil-explicit v2 results and strategy-guided v3 preparation

Pro completed six hands: OpenAI + Google 107, Anthropic + Pro -730. Pro failed all five nil bids. Flash changed its opening bid to 2 and its team made the first-hand contract; after two hands both teams were -8. Flash v2 stopped in hand 3 on Anthropic HTTP 529, with 126 admitted actions. It is incomplete, not a loss. [Pro v2](evidence/nil-v2-pro/summary.json), [Flash v2](evidence/nil-v2-flash/summary.json).

The user authorized a new strategy-guided condition for both candidates. The exact [added paragraph](trials/strategy-v3-prompt.txt) goes to all four players. Engine rules and inference profiles are unchanged. The runs preserve earlier evidence and cumulative spend. Status: LAUNCHING. Anthropic cumulative ceiling is now $20 after the confirmed $10 top-up; other account ceilings remain $10. Per-hand status will appear below. [Protocol](docs/STRATEGY_V3.md).


<!-- STRATEGY3:BEGIN -->
## Strategy-guided v3 trials

Explicit partnership guidance; strict 100-point games, seed 707, candidate thinking disabled.
All four players receive the same guidance. One trial per condition does not establish causality.

| Candidate | Status | Hands | N/S | E/W | Evidence |
|---|---|---:|---:|---:|---|
| pro | COMPLETE | 2 | 135 | -276 | [Summary](evidence/strategy-v3-pro/summary.json) |
| flash | COMPLETE | 4 | 107 | -214 | [Summary](evidence/strategy-v3-flash/summary.json) |

Latest cumulative accounting, including retained unknown-usage reservations:
- openai: $5.265904
- anthropic: $11.142030
- gemini: $1.69025270
- openrouter: $1.1697940684

Per-account guards are frozen in config/strategy-v3-budget.json, less $0.02 probe buffers. No retries or Free Play.
<!-- STRATEGY3:END -->


<!-- KIMI100:BEGIN -->
## Kimi cohort-1 field evaluation

Strict 100-point game; seed 707; v3 guidance; Moonshot AI mxfp4; low reasoning.
Status: **HOLD**. Hands: 1. OpenAI + Google: -70; Anthropic + Kimi: 64.
[Summary](evidence/kimi100/summary.json) · [Replay](evidence/kimi100/frontier-pro/Whiz_100_Baseline_Replay.html)
Prior tracer metadata HOLDs remain preserved. One game is not a general ranking or permanent seat assignment.
Cumulative accounting: {"openai": "5.504994", "anthropic": "11.705060", "gemini": "1.76572370", "openrouter": "1.9864060684"}
<!-- KIMI100:END -->
