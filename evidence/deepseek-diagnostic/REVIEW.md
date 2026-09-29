# DeepSeek diagnostic review

Run: https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/36518251379
Six requests, zero retries, provider pinned to Wafer. All six HTTP 200 and returned expected model/provider identities. Game evidence hashes unchanged; zero model moves applied.

| Model | Case | Requested output cap | Reported total | Reported reasoning | Seconds | Review |
|---|---|---:|---:|---:|---:|---|
| V4 Pro 0813 | Canary | 1024 | 22 | 16 | 0.780 | Valid expected JSON |
| V4 Pro 0813 | Boundary | 64 | 24640 | 24642 | 143.257 | Total-cap failure; usage partition inconsistent |
| V4 Pro 0813 | Game | 8192 | 15842 | 15836 | 105.372 | Total-cap failure; response not admitted |
| V4.1 Flash | Canary | 1024 | 24 | 18 | 0.504 | Valid expected JSON |
| V4.1 Flash | Boundary | 64 | 64 | 66 | 1.337 | Reported total hit cap and finish=length; usage partition inconsistent |
| V4.1 Flash | Game | 8192 | 8192 | 8193 | 100.760 | Reported total hit cap and finish=length; no complete admitted action; usage partition inconsistent |

Verdict: neither route/configuration qualifies as a drop-in replacement. Flash shows reported-total cap enforcement, but not a usable game response at medium effort under 8192 tokens. Pro fails the requested total-output contract. The total-cap check is distinct from accounting consistency: TRUNCATED_AS_BOUNDED in raw receipts evaluates the reported total and finish reason; it does not certify the reasoning-token breakdown. Differences of one or two tokens could reflect counting conventions, but cause is unproven. Raw response content was not retained; hashes, generation IDs, and relevant usage fields were.

The 64-token Pro response reported 24640 = 24576 + 64 total tokens. This arithmetic pattern is consistent with a separate 24576-token reasoning allocation plus the requested cap, but does not prove provider mapping or identify which layer performed it. The game response used 15836 reasoning plus 6 visible tokens. Qwen is therefore not unique in exceeding our total-output interpretation. Both model and serving provider changed between the Qwen and DeepSeek traces; this is not an isolated causal attribution to OpenRouter, Wafer, or model weights.

Accounted batch cost: $0.17678838, matching provider-reported costs in these receipts, below the authorized $0.50 estimated batch budget. Updated OpenRouter cumulative accounted amount: $0.86862499. These diagnostics are separate from the frozen series ledger and must be added before future paid continuation. Per-call reservations were exceeded by Pro; an after-response guard cannot enforce a server-side billing cap.

Preflight repair: initial run 36518198406 omitted fixture preparation and failed the existing resume regression before inference. Restoring baseline/prepare_checkpoint.py made unchanged regression gates pass. Eight diagnostic unit tests, ten runner tests, six smoke tests, engine gates, and held-state reconstruction passed on the paid run. No tests were suppressed.

Recommended next diagnostic, not executed: test a supported explicit reasoning budget or lower effort on Flash; retain total-cap and usage-consistency gates. Do not silently replace players or relabel the existing series. Free Play remains disabled.
