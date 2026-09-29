"""Bounded thinking-off Pro qualification; diagnostic decisions never applied."""
from __future__ import annotations
import json,os,subprocess,time,sqlite3
from decimal import Decimal as D
from typing import Any
import probe as p
import wire_probe as w
import pro_final as q
import reconcile as m
OUT=p.ROOT/'evidence/pro-off-eval'

def observations()->list[dict[str,Any]]:
    rows=[json.loads(x) for x in (p.ROOT/'evidence/whiz300/frontier-g01/frontier.jsonl').read_text().splitlines()]
    proc=subprocess.Popen(['node',str(p.ROOT/'baseline/engine.mjs')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    views=[]
    try:
        frame=p.r.engine(proc,{'op':'init','seed':101,'id':'whiz300-frontier-g01','target':300})
        assert frame['hash']==rows[0]['hash']
        for row in rows:
            if row['kind']!='ACTION':continue
            v=p.r.compact(p.r.engine(proc,{'op':'observe'}))
            if len(v['legal'])>1:views.append({'hash':frame['hash'],'view':v})
            frame=p.r.engine(proc,{'op':'step','action':row['action']})
            assert frame['hash']==row['hash']
        assert frame['hash']==p.EXPECTED
        # Evenly spaced real decision states, plus the current held decision.
        selected=[views[i] for i in [0,len(views)//2,len(views)-1]]
        selected.append({'hash':frame['hash'],'view':p.r.compact(p.r.engine(proc,{'op':'observe'}))})
        return selected
    finally:
        proc.terminate();proc.wait(timeout=5);proc.stdin.close();proc.stdout.close()

def specs(views:list[dict[str,Any]])->list[dict[str,Any]]:
    out=[]
    tasks=[('What is 17 times 19? Options: 0=323, 1=313, 2=333.',0),
      ('What is 17 times 19? Options: 0=333, 1=313, 2=323.',2),
      ('Spades are trump. Hearts led. You hold 2H, AS, KC. Which must you play to follow suit? Options: 0=AS, 1=2H, 2=KC.',1),
      ('Strict Whiz permits nil or your spade count. You hold exactly four spades. Which non-nil bid is permitted? Options: 0=3, 1=5, 2=4.',2)]
    for i,(prompt,answer) in enumerate(tasks):
        out.append({'kind':'known','cap':[32,32,128,512][i],'prompt':prompt+' Return only the choice JSON.','expected':answer})
    for i in range(3):out.append({'kind':'game','cap':8192,'view':views[-1],'repeat':i})
    for v in views[:3]:out.append({'kind':'game','cap':8192,'view':v})
    for i in range(2):out.append({'kind':'pressure','cap':1,'prompt':'Return exactly the JSON object {"choice":1}.'})
    return out

def request(spec:dict[str,Any])->dict[str,Any]:
    view=spec.get('view',{}).get('view',{'legal':[0,1,2]})
    req=p.request(p.MODELS[0],'game' if spec['kind']=='game' else 'boundary',view)
    if 'prompt' in spec:req['messages']=[{'role':'user','content':spec['prompt']}]
    req.update(max_tokens=spec['cap'],reasoning={'enabled':False},stream=True,debug={'echo_upstream_body':True})
    return req

def review(row:dict[str,Any],spec:dict[str,Any])->None:
    echo=row.get('upstream',[])
    checks={'disabled_echo':bool(echo) and all(x.get('thinking',{}).get('type')=='disabled' and x.get('max_tokens')==spec['cap'] for x in echo),
      'zero_reasoning':row.get('reasoning_tokens')==0,'partition':row.get('usage_partition_status')=='PASS',
      'case':row.get('status')==('TRUNCATED_AS_BOUNDED' if spec['kind']=='pressure' else 'PASS')}
    if spec['kind']=='known':checks['known_answer']=row.get('choice')==spec['expected']
    row['checks']=checks;row['admission_status']='PASS' if all(checks.values()) else 'HOLD'
    row['pressure_only']=spec['kind']=='pressure'

def publish()->None:
    for cmd in [['git','add','evidence/pro-off-eval'],['git','commit','-m','Publish Pro thinking-off qualification checkpoint'],['git','push','origin','HEAD:main']]:
        subprocess.run(cmd,cwd=p.ROOT,check=True,stdout=subprocess.DEVNULL)

def finish(rows:list[dict[str,Any]],opening:D,before:dict[str,str])->None:
    total=sum((D(x['accounted_usd']) for x in rows),D(0));same=before==p.fingerprints()
    metadata=[m.fetch(x,os.environ['OPENROUTER_API_KEY']) for x in rows if x.get('generation_id')]
    p.save('generation-metadata.json',metadata)
    matched=len(metadata)==len(rows) and all(x['status']=='PASS' and x['comparison']['native_completion_matches_receipt'] and x['comparison']['native_reasoning_matches_receipt'] for x in metadata)
    passed=sum(x['admission_status']=='PASS' for x in rows)
    p.save('summary.json',{'calls':len(rows),'planned_calls':12,'passed':passed,'status':'PASS' if passed==12 and same and matched else 'HOLD',
      'accounted_usd':str(total),'openrouter_cumulative_accounted_usd':str(opening+total),'game_evidence_unchanged':same,
      'metadata_matches':matched,'game_actions_applied':0,'retries':0,'run_id':os.environ.get('GITHUB_RUN_ID'),'source_commit':os.environ.get('GITHUB_SHA')})
    db=sqlite3.connect(OUT/'gates.sqlite');db.executescript((p.ROOT/'evidence/pro-final-tracer/gates.sql').read_text())
    for row in rows:
        db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',(p.now(),'Pro off evaluation',row['id'],'Route, ceiling, thinking-off, schema or expected truncation, known answer',row['admission_status'],'receipts.json',p.digest(row)))
        if row['admission_status']!='PASS':db.execute('INSERT INTO reverse_rca_ledger VALUES (?,?,?,?,?,?,?)',
          (p.now(),row['id'],'Response validation',row['status'],json.dumps(row['checks']),'Stop without retry','INVESTIGATION_INCOMPLETE; REQUIRES_OPERATOR_ESCALATION; HOLD'))
    for name,ok in [('UNCHANGED',same),('METADATA',matched)]:
        db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',(p.now(),'Pro off evaluation','PRO-OFF-'+name,name,'PASS' if ok else 'HOLD','summary.json',str(ok)))
    db.commit();(OUT/'gates.sql').write_text('\n'.join(db.iterdump())+'\n');db.close()
    (OUT/'SHA256SUMS.txt').write_text(''.join(p.hashlib.sha256(x.read_bytes()).hexdigest()+'  '+x.name+'\n' for x in sorted(OUT.iterdir()) if x.is_file() and x.name!='SHA256SUMS.txt'))

def main()->None:
    if OUT.exists() or os.environ.get('GITHUB_RUN_ATTEMPT','1')!='1':raise ValueError('RERUN_BLOCKED')
    p.OUT=OUT;before=p.fingerprints();views=observations();plan=specs(views)
    p.save('plan.json',{'specs':plan,'budget_usd':'.50','gap_seconds':30,'deadline_seconds':240,'no_retries':True,'stop_on_unexpected_failure':True})
    prices=p.endpoint(p.MODELS[0])['pricing'];rows=[]
    opening=D(json.loads((p.ROOT/'evidence/pro-final-tracer/summary.json').read_text())['openrouter_cumulative_accounted_usd'])
    for index,spec in enumerate(plan,1):
        req=request(spec);ni,no,reserve=q.reserve(req,prices);spent=sum((D(x['accounted_usd']) for x in rows),D(0))
        if spent+reserve>D('.50') or opening+spent+reserve>D('9.98'):break
        row={'id':f'PRO-OFF-{index:02}','model':p.MODELS[0],'case':'game' if spec['kind']=='game' else 'boundary','kind':spec['kind'],
          'started_utc':p.now(),'output_cap':req['max_tokens'],'input_reserve':ni,'output_reserve':no,'input_price':prices['prompt'],
          'output_price':prices['completion'],'reserved_usd':str(reserve),'accounted_usd':str(reserve),'status':'IN_FLIGHT',
          'reasoning':req['reasoning'],'request_sha256':p.digest(req)}
        p.save(row['id']+'-request.json',req);rows.append(row);p.save('receipts.json',rows)
        w.call(req,row,os.environ['OPENROUTER_API_KEY']);review(row,spec);p.save('receipts.json',rows);publish()
        if row['admission_status']!='PASS':break
        if index<len(plan):time.sleep(30)
    finish(rows,opening,before)

if __name__=='__main__':main()
