"""One user-authorized strict 100-point Pro field trial; no inference retries."""
from __future__ import annotations
import json,os,sys,time,subprocess,sqlite3
from pathlib import Path
from decimal import Decimal as D
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'baseline'),str(ROOT/'scripts'),str(ROOT/'diagnostics')]
import runner as r
import probe as p
import wire_probe as w
import pro_final as q
import hand as h
import analyze
OUT=ROOT/'evidence/pro100';ORIGINAL_SELECT=r.select

def select(model:dict[str,Any],view:dict[str,Any])->tuple[dict,dict]:
    if model['account']!='openrouter' or len(view['legal'])==1:return ORIGINAL_SELECT(model,view)
    req=p.request(p.MODELS[0],'game',r.compact(view));req['messages'][0]['content']=req['messages'][0]['content'].replace('game to 300.','game to 100.')
    req.update(reasoning={'enabled':False},stream=True,debug={'echo_upstream_body':True})
    prices=model['native_prices'];ni,no,reserve=q.reserve(req,prices)
    if ni>20000 or r.spent['openrouter']+reserve>r.LIMIT:raise ValueError('BUDGET_OR_INPUT_HOLD')
    cooldown=max(0,30-(time.monotonic()-r.last_finished.get('openrouter',-1000)))
    if cooldown:time.sleep(cooldown)
    row={'model':model['model'],'provider':'openrouter','case':'game','hand':view['handNumber'],'turn':view['turn'],'seat':view['you'],
      'attempt':1,'output_cap':8192,'input_reserve':ni,'output_reserve':no,'input_price':prices['prompt'],'output_price':prices['completion'],
      'reserved_usd':str(reserve),'accounted_usd':str(reserve),'status':'HOLD','http_status':None,'cooldown_seconds':round(cooldown,3),
      'reasoning':req['reasoning'],'request_sha256':p.digest(req)}
    r.spent['openrouter']+=reserve
    p.save('inflight.json',row)
    w.call(req,row,os.environ['OPENROUTER_API_KEY']);r.last_finished['openrouter']=time.monotonic()
    echo=row.get('upstream',[])
    off=bool(echo) and all(x.get('thinking',{}).get('type')=='disabled' and x.get('max_tokens')==8192 for x in echo)
    ok=row.get('admission_status')=='PASS' and row.get('reasoning_tokens')==0 and off
    row.update(status='PASS' if ok else 'HOLD',output_tokens_including_reasoning=row.get('total_output_tokens',0))
    if 'total_output_tokens' in row:row['estimated_cost_usd']=row['accounted_usd']
    r.spent['openrouter']+=D(row['accounted_usd'])-reserve;r.emit('calls',row)
    p.save('inflight.json',{'status':'RECORDED','request_sha256':row['request_sha256']})
    if not ok:raise ValueError('MODEL_HOLD:'+model['model'])
    return view['legal'][row['choice']],{'kind':'MODEL_CHOICE','call':row}

def report(game:dict[str,Any],opening:dict[str,str],before:dict[str,str])->None:
    folder=OUT/game['id'];records=h.rows(folder/'frontier.jsonl')
    verification=analyze.verify_game(records);hands=analyze.hands(records)
    assert verification['final_hash']==game['final_hash']
    assert not hands or [x['score'] for x in hands[-1]['teams']]==game['scores']
    assert before==p.fingerprints()
    summary={'game':game,'verification':verification,'hands':hands,'metrics':analyze.call_metrics(h.rows(folder/'calls.jsonl')),
      'accounting_usd':{k:str(v) for k,v in r.spent.items()},'opening_accounting_usd':opening,'original_series_unchanged':True,
      'run_id':os.environ.get('GITHUB_RUN_ID'),'source_commit':os.environ.get('GITHUB_SHA')}
    p.save('summary.json',summary)
    subprocess.run([sys.executable,str(ROOT/'baseline/build_replay.py'),str(folder)],check=True,stdout=subprocess.DEVNULL)
    db=sqlite3.connect(OUT/'gates.sqlite')
    if not db.execute("SELECT name FROM sqlite_master WHERE name='cumulative_gate_ledger'").fetchone():db.executescript((ROOT/'evidence/pro-off-eval/gates.sql').read_text())
    db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',(p.now(),'Pro 100 field trial','PRO100-HAND-VERIFY','Replay, private views, score, original-series immutability','PASS','summary.json',game['final_hash']))
    if game['status']=='HOLD':db.execute('INSERT INTO reverse_rca_ledger VALUES (?,?,?,?,?,?,?)',
      (p.now(),'PRO100-HOLD','Gameplay admission',game.get('reason','unknown'),'Saved calls and replay','No automatic retry','INVESTIGATION_INCOMPLETE; REQUIRES_OPERATOR_ESCALATION'))
    db.commit();(OUT/'gates.sql').write_text('\n'.join(db.iterdump())+'\n');db.close()
    for cmd in [['git','add','evidence/pro100'],['git','commit','-m','Publish verified Pro 100-point game checkpoint'],['git','push','origin','HEAD:main']]:
        subprocess.run(cmd,cwd=ROOT,check=True,stdout=subprocess.DEVNULL)

def main()->None:
    if OUT.exists() or os.environ.get('GITHUB_RUN_ATTEMPT','1')!='1':raise ValueError('RERUN_BLOCKED')
    p.OUT=OUT;before=p.fingerprints()
    opening=json.loads((ROOT/'evidence/whiz300/series.json').read_text())['accounting_usd']
    opening['openrouter']=json.loads((ROOT/'evidence/pro-off-eval/summary.json').read_text())['openrouter_cumulative_accounted_usd']
    r.spent={k:D(opening[k]) for k in ['openai','anthropic','gemini','openrouter']};r.LIMIT=D('9.98')
    manifest=json.loads(r.MODEL_FILE.read_text())
    models=[next(m for m in manifest['models'] if m['cohort']=='frontier' and m['account']==k) for k in r.spent]
    prices=p.endpoint(p.MODELS[0])['pricing']
    models[3]={**models[3],'model':p.MODELS[0],'native_prices':prices,'provider':{'only':['wafer'],'allow_fallbacks':False,'require_parameters':True}}
    p.save('plan.json',{'target':100,'seed':707,'max_hands':6,'models':models,'reasoning_pro':{'enabled':False},'output_cap':8192,
      'deadline_seconds':240,'opening_accounting_usd':opening,'user_authorized_gameplay_despite_metadata_hold':True,'free_play':False})
    r.select=select;h.OUT=OUT
    game={'id':'frontier-pro','cohort':'frontier','seed':707,'status':'IN_PROGRESS','hands':0,'actions':0,'scores':[0,0]}
    for _ in range(6):
        game=h.play_hand(game,models,{'max_hands_per_game':6});report(game,opening,before)
        if game['status']!='IN_PROGRESS':break
        time.sleep(30)

if __name__=='__main__':main()
