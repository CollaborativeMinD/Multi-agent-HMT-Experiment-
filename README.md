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

Status: **HOLD**. Updated 2026-09-29T02:11:24.406155+00:00.

First partnership to three game wins takes its cohort series. Free Play is **not authorized**.

| Cohort | OpenAI + Google wins | Anthropic + Qwen wins |
|---|---:|---:|
| frontier | 0 | 0 |
| mainstream | 0 | 0 |

| Game | Status | Hands | N/S score | E/W score | Replay |
|---|---|---:|---:|---:|---|
| frontier-g01 | IN_PROGRESS | 1 | 142 | -84 | [Download HTML](evidence/whiz300/frontier-g01/replay.html) |
| mainstream-g01 | HOLD | 0 | 0 | 0 | [Download HTML](evidence/whiz300/mainstream-g01/replay.html) |

Replay links open repository files. Download the HTML and open it locally for playback.

| Account | Cumulative accounted USD |
|---|---:|
| openai | 0.770728 |
| anthropic | 1.616908 |
| gemini | 0.28307510 |
| openrouter | 0.53505594 |

Accounting includes prior pilot usage and its unresolved $0.06768 timeout reservation. Each account retains a separate $0.02 probe buffer under its original $10 ceiling. Provider invoices are authoritative.

[Live Actions run](https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/36510344003) · [Machine-readable status](evidence/whiz300/series.json) · [Cumulative gates](evidence/whiz300/gates.sql)

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
