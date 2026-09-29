"""Offline evidence verification, replay rendering, ledger, and README projection."""
from __future__ import annotations
import hashlib,json,sqlite3,subprocess,sys
from pathlib import Path
import campaign as c
sys.path.insert(0,str(c.BASE))
import analyze
BEGIN='<!-- WHIZ300:BEGIN -->';END='<!-- WHIZ300:END -->'

def verify_and_render(game:dict)->dict:
    folder=c.OUT/game['id'];records=c.rows(folder/(game['cohort']+'.jsonl'))
    verification=analyze.verify_game(records);hands=analyze.hands(records)
    if verification['final_hash']!=game['final_hash']:raise ValueError('SUMMARY_HASH_MISMATCH')
    if len(hands)!=game['hands']:raise ValueError('HAND_COUNT_MISMATCH')
    if hands and [x['score'] for x in hands[-1]['teams']]!=game['scores']:raise ValueError('SCORE_MISMATCH')
    report={'game':game,'verification':verification,'completed_hands':hands,'metrics':analyze.call_metrics(c.rows(folder/'calls.jsonl'))}
    c.atomic(folder/'analysis.json',report)
    subprocess.run([sys.executable,str(c.BASE/'build_replay.py'),str(folder)],check=True,capture_output=True)
    old=folder/'Whiz_100_Baseline_Replay.html';text=old.read_text()
    text=text.replace('Whiz 100 · Baseline replay','Whiz 300 · '+game['id']).replace('WHIZ / 100','WHIZ / 300')
    text=text.replace('Recorded baseline','Best-of-five series').replace('Pilot result:','Game result:')
    text=text.replace('Fixed partnerships and one game per cohort are not a ranking.','Fixed partnerships and matched seeds do not establish individual rankings.')
    (folder/'replay.html').write_text(text);old.unlink()
    return report

def add_gate(state:dict)->None:
    path=c.OUT/'gate_ledger.sqlite';db=sqlite3.connect(path)
    db.executescript((c.ROOT/'opening-gates.sql').read_text()) if not db.execute("SELECT name FROM sqlite_master WHERE name='cumulative_gate_ledger'").fetchone() else None
    evidence='; '.join(g['id']+':'+g.get('final_hash','unavailable') for g in state['games'])
    db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',(state['updated_utc'],'Whiz 300 best-of-five','WHIZ300-HAND-VERIFY' if state['games'] else 'WHIZ300-PUBLISH-INIT','Replay, private views, and independent score agree' if state['games'] else 'Initial series publication before paid requests','PASS','evidence/whiz300/series.json',evidence))
    if state['status']=='HOLD':
        game=state['games'][-1];reason=state.get('reason') or next((g.get('reason') for g in state['games'] if g['status']=='HOLD'),'unknown')
        db.execute('INSERT INTO reverse_rca_ledger VALUES (?,?,?,?,?,?,?)',(state['updated_utc'],'WHIZ300-HOLD','first issue',str(reason),'Preserved calls and admitted actions; no retry','Offline replay of retained actions','INVESTIGATION_INCOMPLETE; REQUIRES_OPERATOR_ESCALATION'))
    db.commit();assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    (c.OUT/'gates.sql').write_text('\n'.join(db.iterdump())+'\n');db.close()

def render_section(state:dict)->str:
    lines=[BEGIN,'## Strict 300-point best-of-five','',f"Status: **{state['status']}**. Updated {state['updated_utc']}.",'',
           'First partnership to three game wins takes its cohort series. Free Play is **not authorized**.','',
           '| Cohort | OpenAI + Google wins | Anthropic + Qwen wins |','|---|---:|---:|']
    for cohort,w in state['series_wins'].items():lines.append(f'| {cohort} | {w[0]} | {w[1]} |')
    lines+=['','| Game | Status | Hands | N/S score | E/W score | Replay |','|---|---|---:|---:|---:|---|']
    for g in state['games']:
        lines.append(f"| {g['id']} | {g['status']} | {g['hands']} | {g['scores'][0]} | {g['scores'][1]} | [Download HTML](evidence/whiz300/{g['id']}/replay.html) |")
    lines+=['','Replay links open repository files. Download the HTML and open it locally for playback.','',
           '| Account | Cumulative accounted USD |','|---|---:|']
    for p,v in state['accounting_usd'].items():lines.append(f'| {p} | {v} |')
    lines+=['','Accounting includes prior pilot usage and its unresolved $0.06768 timeout reservation. Each account retains a separate $0.02 probe buffer under its original $10 ceiling. Provider invoices are authoritative.','',
           '[Live Actions run](https://github.com/CollaborativeMinD/Multi-agent-HMT-Experiment-/actions/runs/'+str(state.get('run_id',''))+') · [Machine-readable status](evidence/whiz300/series.json) · [Cumulative gates](evidence/whiz300/gates.sql)','',END]
    return '\n'.join(lines)

def main()->int:
    state=c.read(c.OUT/'series.json')
    try:
        for game in state['games']:verify_and_render(game)
        add_gate(state)
    except Exception as exc:
        state.update(status='HOLD',verification='FAILED',verification_error_type=type(exc).__name__)
        c.atomic(c.OUT/'series.json',state)
        raise
    readme=c.ROOT.parent/'README.md';text=readme.read_text();section=render_section(state)
    if BEGIN not in text or END not in text:raise ValueError('README_MARKERS_MISSING')
    start=text.index(BEGIN);end=text.index(END)+len(END);readme.write_text(text[:start]+section+text[end:])
    files=[p for p in c.OUT.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt']
    (c.OUT/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(c.OUT))+'\n' for p in sorted(files)))
    print(json.dumps({'status':state['status'],'games':len(state['games']),'series_wins':state['series_wins']}))
    return 0

if __name__=='__main__':raise SystemExit(main())
