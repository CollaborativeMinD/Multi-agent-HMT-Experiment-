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
