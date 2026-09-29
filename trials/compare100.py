"""Offline matched-game comparison and cumulative evidence seal; no API calls."""
import json,sys,sqlite3,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'baseline'))
import analyze
OUT=ROOT/'evidence/flash100'

def read(path:Path):
    return json.loads(path.read_text())

def deals(rows:list)->dict:
    result={}
    for row in rows:
        snap=row.get('snapshot')
        if snap and snap['handNumber'] not in result:result[snap['handNumber']]=[x['hand'] for x in snap['players']]
    return result

def main()->None:
    groups={name:analyze.rows(ROOT/f'evidence/{name}/frontier-pro/frontier.jsonl') for name in ['pro100','flash100']}
    summary={name:read(ROOT/f'evidence/{name}/summary.json') for name in groups}
    plans={name:read(ROOT/f'evidence/{name}/plan.json') for name in groups}
    for name,rows in groups.items():
        assert analyze.verify_game(rows)['final_hash']==summary[name]['game']['final_hash']
        assert analyze.hands(rows)==summary[name]['hands']
    a,b=groups.values();aa=[x for x in a if x['kind']=='ACTION'];bb=[x for x in b if x['kind']=='ACTION']
    first=next(i for i,(x,y) in enumerate(zip(aa,bb)) if x['action']!=y['action'])
    fingerprints=read(OUT/'pro-evidence-fingerprints.json')
    checks={'same_initial_state':a[0]['snapshot']==b[0]['snapshot'],'same_deals':deals(a)==deals(b),
      'same_other_models':a[0]['models'][:3]==b[0]['models'][:3],
      'same_client_limits':all(plans['pro100'][k]==plans['flash100'][k] for k in ['target','seed','max_hands','output_cap','deadline_seconds','free_play']),
      'first_divergence_same_observation':aa[first]['observation']==bb[first]['observation'],
      'pro_evidence_unchanged':all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in fingerprints.items())}
    result={'checks':checks,'first_divergence':{'index':first,'player':aa[first]['player'],'pro':aa[first]['action'],'flash':bb[first]['action'],
      'observation_sha256':hashlib.sha256(json.dumps(aa[first]['observation'],sort_keys=True).encode()).hexdigest()},
      'results':{k:{'scores':v['game']['scores'],'hands':v['hands'],'metrics':v['metrics']} for k,v in summary.items()},
      'limitations':['One game per configuration; paths diverge after first differing action','Shared prompt leaves nil zero-trick condition implicit',
      'Pro echo includes temperature/top_p; Flash echo omits them; effective backend sampling parity unproven','No inference retried; no causal claim about thinking mode']}
    (OUT/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    db=sqlite3.connect(OUT/'gates.sqlite');now=datetime.now(timezone.utc).isoformat()
    for name,ok in checks.items():
        db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',
          (now,'Pro Flash comparison','COMPARE100-'+name,name,'PASS' if ok else 'HOLD','comparison.json',str(ok)))
    for incident,observed in [('NIL-PROMPT','Nil +/-100 omits explicit zero-trick success definition'),('SAMPLING-ECHO','Pro has temperature/top_p; Flash omits these fields')]:
        db.execute('INSERT INTO reverse_rca_ledger VALUES (?,?,?,?,?,?,?)',
          (now,'COMPARE100-'+incident,'Interpretation boundary',observed,'Shared prompt and upstream receipt inspection','Matched trial retained unchanged',
           'INVESTIGATION_INCOMPLETE; REQUIRES_OPERATOR_ESCALATION; no correction or new inference in this trial'))
    db.commit();assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    (OUT/'gates.sql').write_text('\n'.join(db.iterdump())+'\n');db.close()
    (OUT/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(x.read_bytes()).hexdigest()+'  '+str(x.relative_to(OUT))+'\n' for x in sorted(OUT.rglob('*')) if x.is_file() and x.name!='SHA256SUMS.txt'))
    if not all(checks.values()):raise ValueError('COMPARISON_HOLD')

if __name__=='__main__':main()
