"""Observe transformed upstream settings and isolate reasoning demand."""
from __future__ import annotations
import json,os,signal,subprocess,time,urllib.request,urllib.error,sqlite3
from decimal import Decimal as D
from typing import Any
import probe as p
import flash_low as f
OUT=p.ROOT/'evidence/router-wire-tracer'
SCALARS={'model','max_tokens','max_completion_tokens','max_output_tokens','thinking_budget','reasoning_effort','budget_tokens','effort','enabled','type','stream','temperature','top_p','top_k','min_p'}
CONTAINERS={'reasoning','thinking','thinking_config','extra_body','chat_template_kwargs','generation_config'}

def controls(body:dict[str,Any])->dict[str,Any]:
    out={}
    for k,v in body.items():
        if k in SCALARS and (v is None or type(v) in (str,int,float,bool)):out[k]=v
        elif k in CONTAINERS and isinstance(v,dict):out[k]=controls(v)
    out['field_names']=sorted(body)
    for k in ['messages','response_format']:
        if k in body:out[k+'_sha256']=p.digest(body[k])
    return out

def consume(chunk:dict[str,Any],state:dict[str,Any])->None:
    if chunk.get('error'):raise ValueError('STREAM_ERROR')
    for k in ['id','model','provider']:
        if chunk.get(k):state[k]=chunk[k]
    upstream=chunk.get('debug',{}).get('echo_upstream_body')
    if isinstance(upstream,dict):state['upstream'].append(controls(upstream))
    if chunk.get('usage'):state['usage']=chunk['usage']
    for choice in chunk.get('choices',[]):
        delta=choice.get('delta',{})
        if isinstance(delta.get('content'),str):state['content']+=delta['content']
        if choice.get('finish_reason'):state['finish_reason']=choice['finish_reason']
    if len(state['content'])>65536:raise ValueError('CONTENT_BOUND')

def events(response:Any,state:dict[str,Any])->None:
    data=[];size=0;hasher=p.hashlib.sha256()
    for raw in response:
        size+=len(raw);hasher.update(raw)
        if size>16777216:raise ValueError('STREAM_BOUND')
        line=raw.decode('utf-8').rstrip('\r\n')
        if line.startswith('data:'):data.append(line[5:].lstrip())
        elif not line and data:
            payload='\n'.join(data);data=[]
            if payload=='[DONE]':state['done']=True;break
            consume(json.loads(payload),state)
    state['stream_sha256']=hasher.hexdigest();state['stream_bytes']=size
    if not state.get('done'):raise ValueError('STREAM_INCOMPLETE')

def call(req:dict[str,Any],row:dict[str,Any],key:str)->None:
    state={'upstream':[],'content':''};start=time.monotonic()
    signal.signal(signal.SIGALRM,p.deadline);signal.alarm(240)
    try:
        http=urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',data=p.r.canonical(req),
          headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
        with urllib.request.urlopen(http,timeout=230) as response:row['http_status']=response.status;events(response,state)
        row.update(generation_id=state.get('id'),upstream=state['upstream'],stream_sha256=state.get('stream_sha256'))
        body={k:state.get(k) for k in ['model','provider','usage']}
        body['choices']=[{'finish_reason':state.get('finish_reason'),'message':{'content':state['content']}}]
        row['visible_content_characters']=len(state['content'])
        p.evaluate(body,req,row)
    except urllib.error.HTTPError as exc:row.update(status='HOLD',reason='HTTP_ERROR',http_status=exc.code)
    except Exception as exc:
        allowed={'OUTPUT_CAP_EXCEEDED','ROUTE_MISMATCH','USAGE_INVALID','INPUT_RESERVE_EXCEEDED','STREAM_ERROR','STREAM_BOUND','CONTENT_BOUND','STREAM_INCOMPLETE','SCHEMA_INVALID','UNEXPECTED_FINISH'}
        row.update(status='HOLD',reason=str(exc) if str(exc) in allowed else type(exc).__name__)
    finally:
        signal.alarm(0);row.update(upstream=state['upstream'],generation_id=state.get('id'),latency_ms=round((time.monotonic()-start)*1000),completed_utc=p.now())
        f.review(row)

def publish()->None:
    for cmd in [['git','add','evidence/router-wire-tracer'],['git','commit','-m','Publish router wire tracer checkpoint'],['git','push','origin','HEAD:main']]:
        subprocess.run(cmd,cwd=p.ROOT,check=True,stdout=subprocess.DEVNULL)

def finish(rows:list[dict[str,Any]],opening:D,before:dict[str,str])->None:
    total=sum((D(x['accounted_usd']) for x in rows),D(0));unchanged=before==p.fingerprints()
    p.save('summary.json',{'utc':p.now(),'run_id':os.environ.get('GITHUB_RUN_ID'),'source_commit':os.environ.get('GITHUB_SHA'),
      'calls':len(rows),'accounted_usd':str(total),'openrouter_cumulative_accounted_usd':str(opening+total),
      'game_evidence_unchanged':unchanged,'game_actions_applied':0,'retries':0})
    db=sqlite3.connect(OUT/'gates.sqlite');db.executescript((p.ROOT/'evidence/router-rca/gates.sql').read_text())
    for row in rows:
        db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',
          (p.now(),'Router wire RCA',row['id'],'Observe upstream controls and bounded response',row['admission_status'],'receipts.json',p.digest(row)))
        if row['admission_status']!='PASS':db.execute('INSERT INTO reverse_rca_ledger VALUES (?,?,?,?,?,?,?)',
          (p.now(),row['id'],'Echoed upstream controls',row['status'],row.get('reason',row['usage_partition_status']),
           'Three isolated probes; no retries','INVESTIGATION_INCOMPLETE pending review; no game continuation'))
    db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',
      (p.now(),'Router RCA','WIRE-IMMUTABILITY','Original game evidence unchanged','PASS' if unchanged else 'HOLD','summary.json',p.EXPECTED))
    db.commit();(OUT/'gates.sql').write_text('\n'.join(db.iterdump())+'\n');db.close()
    if not unchanged:raise ValueError('GAME_MUTATION')

def main()->None:
    if OUT.exists() or os.environ.get('GITHUB_RUN_ATTEMPT','1')!='1':raise ValueError('RERUN_BLOCKED')
    p.OUT=OUT;view=p.checkpoint();before=p.fingerprints();p.save('observation.json',view)
    models=p.MODELS;eps={m:p.endpoint(m) for m in models};rows=[]
    opening=D(json.loads((p.ROOT/'evidence/flash-low-tracer/summary.json').read_text())['openrouter_cumulative_accounted_usd'])
    specs=[(models[0],'boundary',{'effort':'medium'}),(models[1],'game',{'effort':'low'}),(models[1],'game',{'enabled':False})]
    for index,(model,case,reasoning) in enumerate(specs,1):
        req=p.request(model,case,view);req.update(reasoning=reasoning,stream=True,debug={'echo_upstream_body':True})
        prices=eps[model]['pricing'];ni=len(p.r.canonical(req))+2048
        reserve=ni*D(prices['prompt'])+req['max_tokens']*D(prices['completion'])
        spent=sum((D(x['accounted_usd']) for x in rows),D(0))
        if spent+reserve>D('.25') or opening+spent+reserve>D('9.98'):raise ValueError('BUDGET_HOLD')
        row={'id':f'WIRE-{index:02}','model':model,'case':case,'started_utc':p.now(),'output_cap':req['max_tokens'],
          'input_reserve':ni,'input_price':prices['prompt'],'output_price':prices['completion'],'reserved_usd':str(reserve),
          'accounted_usd':str(reserve),'status':'IN_FLIGHT','reasoning':reasoning,'request_sha256':p.digest(req)}
        p.save(row['id']+'-request.json',req);rows.append(row);p.save('receipts.json',rows)
        call(req,row,os.environ['OPENROUTER_API_KEY']);p.save('receipts.json',rows);publish()
        if index<3:time.sleep(30)
    finish(rows,opening,before)

if __name__=='__main__':main()
