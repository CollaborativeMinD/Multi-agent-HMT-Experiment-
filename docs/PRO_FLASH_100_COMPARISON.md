# Pro versus Flash: matched 100-point cohort-1 trials

## Result

Both thinking-disabled configurations lost their games alongside Anthropic. Flash did not improve the observed partnership result.

| Measure | DeepSeek Pro | DeepSeek Flash |
|---|---:|---:|
| OpenAI + Google final score | 132 | 135 |
| Anthropic + candidate final score | -195 | -207 |
| Candidate bids, hands 1 / 2 | Nil / Nil | Nil / 3 |
| Candidate tricks, hands 1 / 2 | 2 / 3 | 3 / 1 |
| Candidate accepted API calls | 22/22 | 23/23 |
| Reported reasoning tokens | 0 | 0 |
| Candidate total output tokens | 154 | 156 |
| Candidate median latency | 0.640s | 0.866s |
| Candidate maximum latency | 61.898s | 1.265s |
| Candidate accounted cost | $0.0115508 | $0.0020409485 |

Flash was cheaper in this game and had a much lower maximum observed latency, but its median was slightly higher. Different game trajectories and call counts prevent treating these figures as a controlled per-prompt speed benchmark.

## Closest head-to-head observation

The initial state, both dealt hands, other three model identities, client limits, and first four bids matched. The first different action occurred at zero-based action index 6, West's first card play:

- Both candidates had bid nil and received the same private/public observation.
- Partner had led JD; South had played 2D.
- Legal choices were 8D, KD, and QD.
- Pro selected 8D. Flash selected KD.
- Flash subsequently won that trick, immediately breaking nil. Pro did not win that trick.
- Observation SHA-256: 3333eddea2252082327381c1129a43f027164acfa2db7100a2baca240a1e9e62.

This is direct evidence of different choices from the same observed state. It is one sample per model, not a general ability ranking. After this point, the other players respond to different histories; the final-score difference cannot be assigned solely to the replacement model.

Pro later broke its own first-hand nil by playing QH over partner TH while 4H was available. Both configurations therefore supplied concrete examples of taking a trick contrary to the intended immediate nil objective.

## Flash hand outcomes

| Hand | Bids N/E/S/W | Tricks N/E/S/W | N/S cumulative | E/W cumulative |
|---|---|---|---:|---:|
| 1 | 5 / 4 / 2 / 0 | 3 / 3 / 4 / 3 | 70 | -137 |
| 2 | 5 / 4 / 1 / 3 | 7 / 1 / 4 / 1 | 135 | -207 |

Flash changed to a positive bid in hand 2, but one observation on a different hand does not establish learning or adaptation. Its team took two tricks against a combined bid of seven. Anthropic's contribution and opponents' changed decisions remain part of that outcome.

## Shared interpretation limits

1. The unchanged rule prompt says "Nil +/-100" and identifies nil as bid zero, but does not explicitly define success as taking zero tricks or failure as taking any trick. It assumes knowledge of the term. This is our shared prompt limitation, not a diagnosed cause of the decisions. A future rule-comprehension control should spell out that condition before attributing the errors to thinking-off capability.
2. Pro's upstream echo included temperature=1 and top_p=1. Flash's echo omitted both fields. Client sampling fields were omitted for both configurations; effective backend sampling equality is unproven.
3. Both candidates used thinking disabled. The other three models retained their prior medium settings. No causal claim about the effect of disabling thinking follows from these games.
4. One fixed partnership and seed do not establish a model ranking. This is a matched-start seat-substitution case study, not direct adversarial play between Pro and Flash.
5. The engine supplies legal options. The observed distinction is between legal response selection and serving the intended partnership objective, not independent discovery of the full rule set.
6. This software harness tests sequential, coupled decisions under hidden information and enforced state constraints. It does not test physical card handling or simultaneous real-time execution.

## Verification and accounting

Both games completed two hands and 112 actions. Flash's game comprised 91 admitted model decisions and 21 forced moves. All 23 Flash calls passed the pinned route, thinking-disabled, zero-reasoning, output-cap, and schema gates. No inference retry or Free Play occurred.

Independent replay, private observation, trick winner, and score checks passed. The offline comparison verified all six controls, including unchanged Pro evidence and matching deals. Original 300-point evidence remained unchanged. The earlier unavailable diagnostic generation records are not cleared by this trial.

Flash game cost across all four accounts: $1.4172806985. Cumulative account totals after this game: OpenAI $1.836154, Anthropic $3.917510, Gemini $0.71243495, OpenRouter $1.1118230675. Totals include previous usage and retained reservations; invoices remain authoritative.

Flash remains the user's selected cohort-2 fourth seat. This trial makes no automatic permanent cohort-1 substitution and starts no further game.

## Evidence

- [Flash replay](../evidence/flash100/frontier-pro/Whiz_100_Baseline_Replay.html)
- [Pro replay](../evidence/pro100/frontier-pro/Whiz_100_Baseline_Replay.html)
- [Machine-readable comparison](../evidence/flash100/comparison.json)
- [Flash summary](../evidence/flash100/summary.json)
- [Flash call receipts](../evidence/flash100/frontier-pro/calls.jsonl)
- [Cumulative gate and RCA ledger](../evidence/flash100/gates.sql)
- [Evidence checksums](../evidence/flash100/SHA256SUMS.txt)
- [Paid game run](https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/36601511802)
- [Offline comparison verification](https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/36603545565)
