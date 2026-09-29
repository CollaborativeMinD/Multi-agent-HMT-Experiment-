# Strict Whiz 300-point best-of-five protocol

Authorized September 28, 2026 HST: one best-of-five series per pinned cohort, each game to 300. First partnership to three wins ends that cohort; no extra games after a decision. Free Play is not authorized.

Teams remain North/South OpenAI + Google, East/West Anthropic + Qwen. Seats are fixed as in the baseline. Seeds are predeclared as 101, 202, 303, 404, 505, matched by game number across cohorts. Outcomes measure these partnerships under these deals, not individual model superiority. No seed selection based on synthetic tracer wins. Inference remains stochastic.

All strict rules from baseline/BASELINE_PROTOCOL.md remain, with target 300. Nil or spade-count bidding only, follow suit, spades lead restriction, nil ±100, bags and set-contract scoring unchanged. A whole hand is scored before checking target; tied scores continue. Legal-action menus and forced single-option moves are retained. No table talk, free bidding, model replacement, or access to opponents' private hands.

All eight pinned adapters request 8,192 output tokens. Total deadline 240 seconds; socket 230 seconds. Medium reasoning for OpenAI, Anthropic, Gemini, and large Qwen; Qwen Flash retains 512 reasoning tokens. Qwen remains Alibaba-only, with at least 30 seconds between requests. No retries. Stop both cohorts on the first API, schema, usage, replay, budget, or publication issue.

Cohorts alternate after each completed hand. Each invocation restores the existing action stream and all state hashes before making a new request. Each completed hand produces JSONL, verified scores, HTML replay, SQLite/SQL ledgers, and a README update. Partial hands after a failure remain evidence, never a winner. The prior baseline is excluded from series win counts.

Budget: original $10/account remains binding. The new series replaces the earlier pilot-only $3/account bound with a cumulative $9.98 guard, reserving a conservative $0.02 per account for earlier API probes. Carry the exact $2.14137450 prior pilot accounting, including its unresolved $0.06768 timeout reservation. Reserve each call before dispatch; retain unknown-usage reservations. A budget HOLD does not authorize topping up. Provider invoices remain authoritative.

Safety bounds: at most 20 hands per game, five games per cohort, and 200 hand invocations. A workflow may run for at most six hours; it admits no new hand after 330 minutes. A time, hand, or spending bound yields HOLD, not a fabricated series result. Resume requires inspection of the final evidence; never rerun a paid job blindly. No additional campaign is enabled by a completed series.

Current rates remain the same pinned standard text estimates as the pilot, refreshed against provider pricing on September 28 HST. Model catalog aliases may change upstream; the receipt checks exact returned model and Qwen route. Mixed-prefix baseline results are preserved separately. This series begins with uniform limits.
