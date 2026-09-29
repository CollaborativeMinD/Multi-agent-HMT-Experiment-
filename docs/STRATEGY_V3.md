# Strategy-guided v3

Hypothesis: explicit partnership objectives may improve action selection relative to rules and score definitions alone. This is exploratory, one new game per candidate, and guidance affects every player. Nondeterminism and diverging histories prevent causal attribution from team scores alone.

The sole player-prompt addition is trials/strategy-v3-prompt.txt, appended after the nil-explicit v2 rules. No engine change, no candidate reasoning change, no extra per-action hints. Both strict games target 100, use seed 707 and fixed partnerships, stop at six hands, and retain 8192 tokens and 240 seconds per request. Pro then Flash, with the second game admitted only if the first completes.

Review opening nil bids, avoidable nil-breaking choices, positive contracts, bags, token adherence, and team outcomes separately. A legal move is not proof of good strategy. Prior Flash v2 remains an incomplete game after Anthropic HTTP 529. No retry of that historical request is authorized or performed here.

Budget carries forward all prior accounted cost and unknown reservations. The original ceilings remain until the announced Anthropic top-up is given a numeric cumulative authorization. No provider balance is inferred from local estimates.

Offline preparation: initial replay tests failed because the fresh clone had no installed engine dependency. Restoring exact locked npm dependencies and applying the existing source-checked patches resolved the environmental failure. Subsequent engine gates and 60 Python tests passed. The new six tests check exact prompt delta, all provider payloads, approved text, source-drift rejection, account-specific dispatch guard, and function length. No paid inference occurred during preparation.
