# Pro 100-point field trial

**Complete: OpenAI + Google beat Anthropic + thinking-disabled DeepSeek Pro, 132 to -195.**

User authorization: one strict 100-point cohort-1 game, Pro in West/p4, partnered with Anthropic. Flash is selected for cohort 2 p4; no cohort-2 game was run. This order authorized gameplay despite the preserved earlier metadata HOLD, not its erasure.

| Hand | Bids N/E/S/W | Tricks N/E/S/W | Pro nil | Cumulative N/S | Cumulative E/W |
|---|---|---|---|---:|---:|
| 1 | 5 / 4 / 2 / 0 | 5 / 4 / 2 / 2 | Failed | 70 | -58 |
| 2 | 5 / 4 / 1 / 0 | 3 / 2 / 5 / 3 | Failed | 132 | -195 |

## Playing evidence

Pro chose nil both times, despite non-nil alternatives of 2 and 3. In hand 1 it held two aces, three kings, three queens, and JS among its cards. On trick 2, hearts were led as 2H, partner TH, opponent 3H. Pro played QH to win and break its nil, while 4H was legal and would have lost that trick. This establishes a missed immediate nil-preservation opportunity, not a proof that an alternative sequence would win the hand or game.

Anthropic made its four-trick bid in hand 1. In hand 2, Anthropic took two against a bid of four, while Pro's three tricks counted against its nil and did not satisfy the positive contract under the strict rules. Both contributions must remain visible; the team loss is not an individual ranking.

## Execution evidence

- 112 admitted game actions: 92 accepted model calls and 20 forced single-option moves.
- Pro: 22/22 calls accepted, zero reported reasoning tokens throughout, 154 total output tokens, no overruns or retries.
- Pro latency: median 0.640s, maximum 61.898s. Provider cooldown totaled 189.605s and is separate from inference latency.
- Pro accounted cost: $0.0115508. All four accounts' game cost: $1.57317205.
- Every replay state hash and private observation projection passed; trick winners and hand scores were independently checked.
- Original 300-point evidence remained unchanged.
- Final state hash: 022ed4f93b9fd83f62cace01ffeea16981c4af0f6d45d019ba7cc0d5367ba129.

Controls: fresh seed 707; target 100; maximum six hands; 8192 output tokens per request; 240-second request deadline; no fallback; no automatic retries; per-account admission below $9.98. Pro used Wafer with thinking disabled. Other cohort-1 players retained the previous medium reasoning settings. The asymmetry is explicit and this game does not represent a matched-compute frontier ranking.

Accounting metadata clarification: the Pro entry in the recorded plan retained the old Qwen display field standard_text_usd_per_million_tokens when copied from the registry. The Pro adapter did not use it. The saved native_prices, reservations, and individual receipts used refreshed Wafer prices of $0.40/M input and $4.20/M output. The recorded plan is preserved rather than rewritten after the run.

## Disposition

The field trial is COMPLETE. Pro demonstrated technical participation under the selected thinking-off configuration. The observed nil decisions provide adverse strategic evidence; this game does not establish that it deserves a permanent frontier seat. No further game or Free Play was started automatically. Flash's cohort-2 selection is recorded separately.

The prior three unavailable diagnostic generation records remain a historical metadata HOLD. This game captures streaming usage, generation IDs, upstream echoes, hashes, and choices; it does not claim that every provider generation record or invoice has been independently reconciled.

## Evidence

- [Run](https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/36530004392)
- [HTML replay](../evidence/pro100/frontier-pro/Whiz_100_Baseline_Replay.html)
- [Summary, metrics, and independent scoring](../evidence/pro100/summary.json)
- [All admitted actions](../evidence/pro100/frontier-pro/frontier.jsonl)
- [Call receipts](../evidence/pro100/frontier-pro/calls.jsonl)
- [Cumulative gates](../evidence/pro100/gates.sql)
- [User seat selections](../config/seat-selections.json)

## Subsequent matched-trial interpretation note

The Flash comparison identified a shared prompt assumption: "Nil +/-100" does not explicitly state the zero-trick success condition. The observed Pro actions and scores remain valid, but attributing them solely to model capability or disabled reasoning would exceed the evidence. See [matched comparison](PRO_FLASH_100_COMPARISON.md) for the controlled observation and backend sampling limitation.
