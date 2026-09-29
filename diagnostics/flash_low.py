"""Supported low-effort Flash tracer; three isolated calls, no game mutation."""
from __future__ import annotations
import json,os,sqlite3,subprocess,time,urllib.request
from decimal import Decimal as D
from pathlib import Path
from typing import Any
import probe as p
MODEL='deepseek/deepseek-v4.1-flash'
OUT=p.ROOT/'evidence/flash-low-tracer'

def admission()->dict[str,Any]:
    with urllib.request.urlopen('https://openrouter.ai/api/v1/models',timeout=25) as response:data=json.load(response)
    model=next(m for m in data['data'] if m['id']==MODEL)
    p.save('model-metadata.json',{'utc':p.now(),'model':model})
    if 'low' not in model.get('reasoning',{}).get('supported_efforts',[]):raise ValueError('LOW_NOT_ADVERTISED')
    return p.endpoint(MODEL)

def request(case:str,view:dict[str,Any])->dict[str,Any]:
    req=p.request(MODEL,case,view);req['reasoning']={'effort':'low'}
    return req

def review(row:dict[str,Any])->None:
    total=row.get('total_output_tokens');reasoning=row.get('reasoning_tokens')
    valid=type(total)is int and type(reasoning)is int and 0<=reasoning<=total
    row['usage_partition_status']='PASS' if valid else 'UNKNOWN' if reasoning is None else 'HOLD'
    row['case_contract_status']='PASS' if row['status']=='PASS' or row['case']=='boundary' and row['status']=='TRUNCATED_AS_BOUNDED' else 'HOLD'
    row['admission_status']='PASS' if row['case_contract_status']=='PASS' and valid else 'HOLD'

def publish()->None:
    for args in [['git','add','evidence/flash-low-tracer'],['git','commit','-m','Publish isolated Flash low-effort tracer checkpoint'],['git','push','origin','HEAD:main']]:
        subprocess.run(args,cwd=p.ROOT,check=True,stdout=subprocess.DEVNULL)

def ledger(rows:list[dict[str,Any]],unchanged:bool)->None:
    db=sqlite3.connect(OUT/'gates.sqlite')
    db.executescript((p.ROOT/'evidence/deepseek-diagnostic/gates.sql').read_text())
    db.execute('INSERT INTO reverse_rca_ledger VALUES (?,?,?,?,?,?,?)',
      (p.now(),'FLASH-EFFORT-MAPPING','Catalog admission','Prior Flash diagnostic sent medium',
       'Live catalog advertises max/high/low; prior route accepted medium but mapping unknown',
       'Use advertised low; preserve prior receipts','INVESTIGATION_COMPLETE at documented interface boundary; SOLUTION_CANDIDATE_APPLIED'))
    db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',
      (p.now(),'Flash tracer','FLASH-LOW-PREFLIGHT','Existing regression plus low-effort request and usage gates','PASS','GitHub workflow logs',os.environ.get('GITHUB_RUN_ID')))
    for row in rows:
        db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',
          (p.now(),'Flash low tracer',row['id'],'Route, response, total cap, and usage partition',row['admission_status'],'receipts.json',p.digest(row)))
        if row['admission_status']!='PASS':db.execute('INSERT INTO reverse_rca_ledger VALUES (?,?,?,?,?,?,?)',
          (p.now(),row['id'],'Reported response and usage',row['status'],row.get('reason',row['usage_partition_status']),
           'Independent bounded probes; no retries','INVESTIGATION_INCOMPLETE; game remains HOLD'))
    db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',
      (p.now(),'Flash tracer','FLASH-LOW-IMMUTABILITY','Game evidence unchanged','PASS' if unchanged else 'HOLD','summary.json',p.EXPECTED))
    db.commit();assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    (OUT/'gates.sql').write_text('\n'.join(db.iterdump())+'\n');db.close()

def finish(rows:list[dict[str,Any]],opening:D,before:dict[str,str])->None:
    total=sum((D(x['accounted_usd']) for x in rows),D(0));unchanged=before==p.fingerprints()
    p.save('summary.json',{'utc':p.now(),'run_id':os.environ.get('GITHUB_RUN_ID'),'source_commit':os.environ.get('GITHUB_SHA'),
      'calls':len(rows),'accounted_usd':str(total),'openrouter_cumulative_accounted_usd':str(opening+total),
      'game_evidence_unchanged':unchanged,'game_actions_applied':0,'retries':0,'provider':'Wafer','reasoning_effort':'low',
      'game_probes_admitted':sum(x['admission_status']=='PASS' and x['case']=='game' for x in rows)})
    ledger(rows,unchanged)
    table='\n'.join(f"| {x['id']} | {x['case']} | {x['status']} | {x.get('total_output_tokens','?')}/{x['output_cap']} | {x.get('reasoning_tokens','?')} | {x['latency_ms']/1000:.2f} | {x['admission_status']} |" for x in rows)
    note='\n\n## Flash supported low-effort tracer\n\nSame Wafer route, held observation, and 8192 game cap. Prior medium effort is not advertised in the live model catalog. Exact reasoning budget not advertised; this tracer uses supported low. No game moves applied.\n\n| Probe | Case | Response | Total/cap | Reasoning | Seconds | Admission |\n|---|---|---|---:|---:|---:|---|\n'+table
    note+='\n\nCost accounted: $'+str(total)+'. OpenRouter cumulative including both diagnostic batches: $'+str(opening+total)+'. [Receipts](evidence/flash-low-tracer/receipts.json). Three probes cannot establish general reliability or move quality. Original series remain on HOLD.\n'
    path=p.ROOT/'README.md';path.write_text(path.read_text()+note)
    p.save('manifest.json',{x.name:p.hashlib.sha256(x.read_bytes()).hexdigest() for x in OUT.iterdir() if x.is_file()})
    if not unchanged:raise ValueError('GAME_EVIDENCE_CHANGED')

def main()->None:
    if os.environ.get('GITHUB_RUN_ATTEMPT','1')!='1' or OUT.exists():raise ValueError('RERUN_BLOCKED')
    p.OUT=OUT;before=p.fingerprints();view=p.checkpoint();p.save('observation.json',view)
    old=json.loads((p.ROOT/'evidence/deepseek-diagnostic/observation.json').read_text())
    if p.digest(view)!=p.digest(old):raise ValueError('OBSERVATION_DRIFT')
    ep=admission();prices=ep['pricing'];rows=[];key=os.environ['OPENROUTER_API_KEY']
    opening=D(json.loads((p.ROOT/'evidence/deepseek-diagnostic/summary.json').read_text())['openrouter_cumulative_accounted_usd'])
    for index,case in enumerate(['boundary','game','game'],1):
        req=request(case,view);ni=len(p.r.canonical(req))+2048
        reserve=ni*D(prices['prompt'])+req['max_tokens']*D(prices['completion'])
        spent=sum((D(x['accounted_usd']) for x in rows),D(0))
        if spent+reserve>D('.10') or opening+spent+reserve>D('9.98'):raise ValueError('BUDGET_HOLD')
        row={'id':f'FLASH-LOW-{index:02}','case':case,'model':MODEL,'provider_pin':'wafer','started_utc':p.now(),
          'input_reserve':ni,'output_cap':req['max_tokens'],'input_price':prices['prompt'],'output_price':prices['completion'],
          'reserved_usd':str(reserve),'accounted_usd':str(reserve),'status':'IN_FLIGHT','request_sha256':p.digest(req),'reasoning':req['reasoning']}
        p.save(row['id']+'-request.json',req);rows.append(row);p.save('receipts.json',rows)
        p.call(req,row,key);review(row);p.save('receipts.json',rows);publish()
        print(json.dumps({k:row.get(k) for k in ['id','status','reason','total_output_tokens','reasoning_tokens','latency_ms','admission_status']}),flush=True)
        if index<3:time.sleep(30)
    finish(rows,opening,before)

if __name__=='__main__':main()
