"""Final three-call Pro isolation: cap slope and thinking toggle."""
import json,os,sqlite3,subprocess,time
from decimal import Decimal as D
import probe as p
import wire_probe as w
OUT=p.ROOT/'evidence/pro-final-tracer'

def specifications(view):
    specs=[('boundary',128,{'effort':'low'}),('boundary',128,{'enabled':False}),('game',8192,{'enabled':False})]
    for case,cap,reasoning in specs:
        req=p.request(p.MODELS[0],case,view)
        req.update(max_tokens=cap,reasoning=reasoning,stream=True,debug={'echo_upstream_body':True})
        yield case,req

def reserve(req,prices):
    ni=len(p.r.canonical(req))+2048
    # Admission cushion for the observed additive allowance, not a server-side guarantee.
    output_reserve=32768+req['max_tokens']
    return ni,output_reserve,ni*D(prices['prompt'])+output_reserve*D(prices['completion'])

def publish():
    for cmd in [['git','add','evidence/pro-final-tracer'],['git','commit','-m','Publish final Pro tracer checkpoint'],['git','push','origin','HEAD:main']]:
        subprocess.run(cmd,cwd=p.ROOT,check=True,stdout=subprocess.DEVNULL)

def finish(rows,opening,before):
    total=sum((D(x['accounted_usd']) for x in rows),D(0));unchanged=before==p.fingerprints()
    p.save('summary.json',{'utc':p.now(),'run_id':os.environ.get('GITHUB_RUN_ID'),'source_commit':os.environ.get('GITHUB_SHA'),
      'calls':len(rows),'accounted_usd':str(total),'openrouter_cumulative_accounted_usd':str(opening+total),
      'game_evidence_unchanged':unchanged,'game_actions_applied':0,'retries':0,'admission_budget_usd':'.30',
      'hypothesis':'Thinking-enabled boundary reports 24576 + requested max_tokens; attribution remains unproven',
      'predicted_boundary_total':24704})
    db=sqlite3.connect(OUT/'gates.sqlite');db.executescript((p.ROOT/'evidence/router-wire-tracer/gates.sql').read_text())
    for row in rows:
        db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',
          (p.now(),'Final Pro RCA',row['id'],'Pinned route, output ceiling, usage partition, case contract',row['admission_status'],'receipts.json',p.digest(row)))
        if row['admission_status']!='PASS':db.execute('INSERT INTO reverse_rca_ledger VALUES (?,?,?,?,?,?,?)',
          (p.now(),row['id'],'Thinking toggle and cap slope',row['status'],row.get('reason',row['usage_partition_status']),
           'Three isolated probes without retries','HOLD; attribution pending evidence review'))
    db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',
      (p.now(),'Final Pro RCA','PRO-IMMUTABILITY','Original game evidence unchanged','PASS' if unchanged else 'HOLD','summary.json',p.EXPECTED))
    db.commit();(OUT/'gates.sql').write_text('\n'.join(db.iterdump())+'\n');db.close()
    p.save('manifest.json',{x.name:p.hashlib.sha256(x.read_bytes()).hexdigest() for x in OUT.iterdir() if x.is_file()})
    if not unchanged:raise ValueError('GAME_MUTATION')

def main():
    if OUT.exists() or os.environ.get('GITHUB_RUN_ATTEMPT','1')!='1':raise ValueError('RERUN_BLOCKED')
    p.OUT=OUT;view=p.checkpoint();before=p.fingerprints();p.save('observation.json',view)
    prices=p.endpoint(p.MODELS[0])['pricing'];rows=[]
    opening=D(json.loads((p.ROOT/'evidence/router-wire-tracer/summary.json').read_text())['openrouter_cumulative_accounted_usd'])
    for index,(case,req) in enumerate(specifications(view),1):
        ni,no,held=reserve(req,prices);spent=sum((D(x['accounted_usd']) for x in rows),D(0))
        if spent+held>D('.30') or opening+spent+held>D('9.98'):raise ValueError('BUDGET_HOLD')
        row={'id':f'PRO-{index:02}','model':p.MODELS[0],'case':case,'started_utc':p.now(),'output_cap':req['max_tokens'],
          'input_reserve':ni,'output_reserve':no,'input_price':prices['prompt'],'output_price':prices['completion'],
          'reserved_usd':str(held),'accounted_usd':str(held),'status':'IN_FLIGHT','reasoning':req['reasoning'],'request_sha256':p.digest(req)}
        p.save(row['id']+'-request.json',req);rows.append(row);p.save('receipts.json',rows)
        w.call(req,row,os.environ['OPENROUTER_API_KEY']);p.save('receipts.json',rows);publish()
        if index<3:time.sleep(30)
    finish(rows,opening,before)

if __name__=='__main__':main()
