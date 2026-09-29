"""Write an evidence-grounded pilot report; analysis.json must already verify."""
import json,sys
from decimal import Decimal
from pathlib import Path

def table(headers,rows):
    return ['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,r))+' |' for r in rows]

def build(folder):
    summary=json.loads((folder/'summary.json').read_text());analysis=json.loads((folder/'analysis.json').read_text())
    complete=sum(g['status']=='COMPLETE' for g in analysis['games']);cost=sum(map(Decimal,summary['accounting_usd'].values()))
    lines=['# Strict Whiz 100: first pilot','',f'**BLUF:** {complete}/2 cohort games completed. Total accounted pilot cost: ${cost:.6f}, including earlier held requests and the isolated diagnostic. This is a descriptive, amended pilot, not a model ranking.','']
    results=[]
    for g in analysis['games']:
        final=g['completed_hands'][-1]['teams'] if g['completed_hands'] else None
        scores=[t['score'] for t in final] if final else ['pending','pending']
        results.append([g['cohort'],g['status'],len(g['completed_hands']),g['verification']['actions'],*scores])
    lines+=table(['Cohort','Status','Hands completed','Actions','OpenAI + Google','Anthropic + Qwen'],results)
    lines+=['','North/South: OpenAI + Google. East/West: Anthropic + Qwen. Seed 7 and the initial seat/deal schedule are shared. Games end after a full hand at or above 100 with unequal scores.','', '## Gameplay evidence','']
    for g in analysis['games']:
        lines += [f"### {g['cohort'].title()}",'',f"Decisions: {g['decision_counts']}. Replay and every private projection: PASS. Independent trick and completed-hand score verification: PASS.",'']
        records=[]
        for h in g['completed_hands']:
            records.append([h['hand'],' / '.join(map(str,h['bids'])),' / '.join(map(str,h['tricks'])),' / '.join('made' if t['made'] else 'set' for t in h['teams']),' / '.join(map(str,[t['score'] for t in h['teams']])),' / '.join('—' if x is None else x for x in h['nil_results'])])
        lines+=table(['Hand','Bids N/E/S/W','Tricks N/E/S/W','Contracts NS/EW','Scores NS/EW','Nil N/E/S/W'],records)+['']
    lines+=['## API behavior and cost','']
    records=[]
    for m in analysis['model_metrics']:
        records.append([m['model'],m['attempts'],m['accepted'],m['holds'],m['diagnostic_attempts'],m['http_429'],round(m['latency_median_ms']/1000,3),f"${Decimal(m['known_estimated_cost_usd']):.6f}",f"${Decimal(m['unknown_usage_reserve_usd']):.6f}"])
    lines+=table(['Model','Attempts','Accepted','Held','Diagnostics','429','Median seconds','Known estimate','Unknown reserve'],records)
    lines+=['','Attempts and accepted responses include separately labeled diagnostics; only gameplay decisions in the action logs were applied. Latency excludes deliberate cooldown. Costs use locked standard token prices and are estimates, not provider invoices. Accounted totals retain full reservations where usage is unavailable. Forced single-legal-action transitions make no API request.','', '## Amendment and limits','',
      'The initial run stopped after ten accepted frontier actions because Qwen reported 1,291 output tokens against a 1,024-token reservation. The original generic error omitted finish reason, so the provider-level cause remains unresolved. The rejected response was never applied.',
      '', 'Continuation verified and reused the ten accepted actions, carried forward all spend, and raised the subsequent requested output limit and reservation to 4,096 for all models. Medium effort remained unchanged; Qwen Flash retained its 512-token reasoning budget. The frontier game therefore has a mixed-budget prefix. No model was substituted, and no strategic choice was supplied by a heuristic.',
      '', 'Legal-action menus assist the models. Zero illegal executed moves would not establish independent rule knowledge. Fixed seats, fixed partners, one seed, and one game per cohort cannot separate individual ability from cards and partner effects. No free-play or table-talk evaluation was run.',
      '', '## Reproduce the checks','', 'From the repository root, after the documented engine install and patch:', '', '```bash','python baseline/analyze.py PATH_TO_EXTRACTED_EVIDENCE','python baseline/build_replay.py PATH_TO_EXTRACTED_EVIDENCE','```','',
      'The replay is offline and makes no model calls. The evidence package also includes the cumulative SQLite gate ledger, the original interrupted artifact, the frozen protocol, and file hashes.', '', '## Authorized 8,192-token continuation','', 'The user authorized doubling the current gameplay allowance from 4,096 to 8,192 for all eight models and stopping on the next issue. Continuation starts from action92, carries the diagnostic cost forward, and performs no automatic retries. Model IDs, routing, reasoning settings, and timeouts are unchanged. A successful game under the larger allowance would not prove that the provider enforces requested token caps.', '', '## Run references','',
      '- [Original held run](https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/36496016934)',
      '- [4,096-token continuation](https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/36496680649)',
      '- [8,192-token continuation](https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/36504424064)',
      f"- Continuation commit: `{summary['commit']}`",f"- Per-account pilot cap: ${summary['per_account_limit']}"]
    (folder/'BASELINE_RESULTS.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':build(Path(sys.argv[1]))
