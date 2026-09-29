"""Six isolated diagnostic requests. Never applies a model move or resumes games."""
from __future__ import annotations
import hashlib,json,os,signal,sqlite3,subprocess,sys,time,urllib.request,urllib.error
from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'baseline'),str(ROOT/'scripts')]
import runner as r
OUT=ROOT/'evidence/deepseek-diagnostic'
MODELS=['deepseek/deepseek-v4-pro-0813','deepseek/deepseek-v4.1-flash']
EXPECTED='c56589adfbeb3abba88924ba2096b88b30f48ea4eadfcdf6f8df2a42bc8fc84f'
D=Decimal

def now()->str:return datetime.now(timezone.utc).isoformat()
def digest(value:Any)->str:return hashlib.sha256(r.canonical(value)).hexdigest()
def save(name:str,value:Any)->None:
    OUT.mkdir(parents=True,exist_ok=True)
    path=OUT/name;tmp=path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(path)

def checkpoint()->dict[str,Any]:
    path=ROOT/'evidence/whiz300/frontier-g01/frontier.jsonl'
    rows=[json.loads(x) for x in path.read_text().splitlines()]
    proc=subprocess.Popen(['node',str(ROOT/'baseline/engine.mjs')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    try:
        frame=r.engine(proc,{'op':'init','seed':101,'id':'whiz300-frontier-g01','target':300})
        if frame['hash']!=rows[0]['hash']:raise ValueError('INITIAL_MISMATCH')
        count=0
        for row in rows:
            if row['kind']!='ACTION':continue
            frame=r.engine(proc,{'op':'step','action':row['action']});count+=1
            if frame['hash']!=row['hash']:raise ValueError('REPLAY_MISMATCH')
        if count!=102 or frame['hash']!=EXPECTED:raise ValueError('CHECKPOINT_MISMATCH')
        view=r.engine(proc,{'op':'observe'})
        if view['you']!='p4':raise ValueError('SEAT_MISMATCH')
        return r.compact(view)
    finally:
        proc.terminate();proc.wait(timeout=5);proc.stdin.close();proc.stdout.close()

def endpoint(model:str)->dict[str,Any]:
    url='https://openrouter.ai/api/v1/models/'+model+'/endpoints'
    with urllib.request.urlopen(url,timeout=25) as response:data=json.load(response)
    ep=next(x for x in data['data']['endpoints'] if x['tag']=='wafer')
    required={'max_tokens','reasoning','response_format','structured_outputs'}
    if not required<=set(ep['supported_parameters']):raise ValueError('PARAMETERS_UNSUPPORTED')
    if ep['status']!=0:raise ValueError('ENDPOINT_UNAVAILABLE')
    save(model.split('/')[-1]+'-endpoint.json',{'utc':now(),'url':url,'endpoint':ep})
    return ep

def request(model:str,case:str,view:dict[str,Any])->dict[str,Any]:
    choices=list(range(len(view['legal']))) if case=='game' else [0,1,2]
    schema={'type':'object','properties':{'choice':{'type':'integer','enum':choices}},'required':['choice'],'additionalProperties':False}
    prompts={'canary':'Return exactly the JSON object {"choice":1}.',
      'boundary':'Compute the remainder of 987654321987654321 raised to 123456789 modulo 1000000007. Choose 0 if the remainder is even, 1 if odd, or 2 if uncertain. Return only the choice JSON.',
      'game':r.RULES.replace('game to 100.','game to 300.')+'\n'+r.canonical(view).decode()}
    return {'model':model,'messages':[{'role':'user','content':prompts[case]}],
      'max_tokens':{'canary':1024,'boundary':64,'game':8192}[case],
      'reasoning':{'effort':'medium'},'provider':{'only':['wafer'],'allow_fallbacks':False,'require_parameters':True},
      'response_format':{'type':'json_schema','json_schema':{'name':'play_action','strict':True,'schema':schema}}}

def unique(pairs:list[tuple[str,Any]])->dict[str,Any]:
    out={}
    for k,v in pairs:
        if k in out:raise ValueError('DUPLICATE_KEY')
        out[k]=v
    return out

def evaluate(body:dict[str,Any],req:dict[str,Any],row:dict[str,Any])->None:
    usage=body.get('usage',{});ni=usage.get('prompt_tokens');no=usage.get('completion_tokens')
    row.update(returned_model=body.get('model'),returned_provider=body.get('provider'),response_sha256=digest(body))
    if type(ni)is not int or type(no)is not int or min(ni,no)<0:raise ValueError('USAGE_INVALID')
    reasoning=usage.get('completion_tokens_details',{}).get('reasoning_tokens')
    row.update(input_tokens=ni,total_output_tokens=no,reasoning_tokens=reasoning,
      visible_tokens=no-reasoning if type(reasoning)is int and 0<=reasoning<=no else None)
    row['estimated_cost_usd']=str(ni*D(row['input_price'])+no*D(row['output_price']))
    row['accounted_usd']=row['estimated_cost_usd']
    reported=usage.get('cost')
    if type(reported) in (int,float) and reported>=0:
        row['provider_reported_cost_usd']=str(reported)
        row['accounted_usd']=str(max(D(str(reported)),D(row['estimated_cost_usd'])))
    choice=body.get('choices',[{}])[0];finish=choice.get('finish_reason');row['finish_reason']=finish
    if row['returned_model']!=req['model'] or row['returned_provider']!='Wafer':raise ValueError('ROUTE_MISMATCH')
    if no>req['max_tokens']:raise ValueError('OUTPUT_CAP_EXCEEDED')
    if ni>row['input_reserve']:raise ValueError('INPUT_RESERVE_EXCEEDED')
    row['token_adherence']='PASS'
    if finish=='length':
        row.update(status='TRUNCATED_AS_BOUNDED',schema_status='NOT_ASSESSED')
        return
    if finish!='stop':raise ValueError('UNEXPECTED_FINISH')
    value=json.loads(choice.get('message',{}).get('content') or '',object_pairs_hook=unique)
    legal=req['response_format']['json_schema']['schema']['properties']['choice']['enum']
    if type(value)is not dict or set(value)!={'choice'} or type(value['choice'])is not int or value['choice'] not in legal:
        raise ValueError('SCHEMA_INVALID')
    if row['case']=='canary' and value['choice']!=1:raise ValueError('CANARY_WRONG_CHOICE')
    row.update(status='PASS',schema_status='PASS',choice=value['choice'])

def deadline(signum:int,frame:Any)->None:raise TimeoutError('DEADLINE')

def call(req:dict[str,Any],row:dict[str,Any],key:str)->None:
    start=time.monotonic();signal.signal(signal.SIGALRM,deadline);signal.alarm(240)
    try:
        http=urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',data=r.canonical(req),
          headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
        with urllib.request.urlopen(http,timeout=230) as response:
            row['http_status']=response.status;raw=response.read(2097153)
            row['request_id']=response.headers.get('x-request-id')
        if len(raw)>2097152:raise ValueError('RESPONSE_TOO_LARGE')
        body=json.loads(raw);row['generation_id']=body.get('id');evaluate(body,req,row)
    except urllib.error.HTTPError as exc:row.update(status='HOLD',reason='HTTP_ERROR',http_status=exc.code)
    except Exception as exc:
        allowed={'USAGE_INVALID','ROUTE_MISMATCH','OUTPUT_CAP_EXCEEDED','INPUT_RESERVE_EXCEEDED','SCHEMA_INVALID','UNEXPECTED_FINISH','CANARY_WRONG_CHOICE','DUPLICATE_KEY','RESPONSE_TOO_LARGE'}
        reason=str(exc) if str(exc) in allowed else type(exc).__name__
        row.update(status='HOLD',reason=reason)
    finally:
        signal.alarm(0);row['latency_ms']=round((time.monotonic()-start)*1000);row['completed_utc']=now()

def ledger(rows:list[dict[str,Any]],unchanged:bool)->None:
    db=sqlite3.connect(OUT/'gates.sqlite')
    db.executescript((ROOT/'evidence/whiz300/gates.sql').read_text())
    db.executescript((ROOT/'diagnostics/intake-rca.sql').read_text())
    for row in rows:
        ok=row['status']=='PASS' or row['case']=='boundary' and row['status']=='TRUNCATED_AS_BOUNDED'
        db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',
          (now(),'DeepSeek diagnostic',row['id'],'Pinned route, token bound, and case contract','PASS' if ok else 'HOLD','receipts.json',digest(row)))
        if not ok:db.execute('INSERT INTO reverse_rca_ledger VALUES (?,?,?,?,?,?,?)',
          (now(),row['id'],'provider response',row['status'],row.get('reason',row['status']),'No retries; diagnostic only','INVESTIGATION_INCOMPLETE; game remains HOLD'))
    db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',
      (now(),'DeepSeek diagnostic','DIAG-IMMUTABILITY','Game evidence unchanged','PASS' if unchanged else 'HOLD','summary.json',EXPECTED))
    db.commit();(OUT/'gates.sql').write_text('\n'.join(db.iterdump())+'\n');db.close()

def fingerprints()->dict[str,str]:
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'evidence/whiz300').rglob('*') if p.is_file()}

def main()->None:
    if os.environ.get('GITHUB_RUN_ATTEMPT','1')!='1' or OUT.exists():raise ValueError('RERUN_BLOCKED')
    before=fingerprints();view=checkpoint();save('observation.json',view)
    key=os.environ['OPENROUTER_API_KEY'];rows=[];opening=D(json.loads((ROOT/'evidence/whiz300/series.json').read_text())['accounting_usd']['openrouter'])
    eps={m:endpoint(m) for m in MODELS}
    for model in MODELS:
        for case in ['canary','boundary','game']:
            req=request(model,case,view);ep=eps[model];p=ep['pricing']
            ni=len(r.canonical(req))+2048;reserve=ni*D(p['prompt'])+req['max_tokens']*D(p['completion'])
            spent=sum((D(x['accounted_usd']) for x in rows),D(0))
            if spent+reserve>D('.50') or opening+spent+reserve>D('9.98'):raise ValueError('BUDGET_HOLD')
            row={'id':f'DIAG-{len(rows)+1:02}','case':case,'model':model,'provider_pin':'wafer','started_utc':now(),
              'input_reserve':ni,'output_cap':req['max_tokens'],'input_price':p['prompt'],'output_price':p['completion'],
              'reserved_usd':str(reserve),'accounted_usd':str(reserve),'status':'IN_FLIGHT','request_sha256':digest(req),'reasoning':req['reasoning']}
            save(row['id']+'-request.json',req);rows.append(row);save('receipts.json',rows)
            call(req,row,key);save('receipts.json',rows)
            print(json.dumps({k:row.get(k) for k in ['id','model','case','status','reason','total_output_tokens','latency_ms']}),flush=True)
            if len(rows)<6:time.sleep(30)
    unchanged=before==fingerprints();total=sum((D(x['accounted_usd']) for x in rows),D(0))
    summary={'utc':now(),'run_id':os.environ.get('GITHUB_RUN_ID'),'source_commit':os.environ.get('GITHUB_SHA'),
      'calls':len(rows),'game_evidence_unchanged':unchanged,'game_actions_applied':0,'accounted_usd':str(total),
      'openrouter_cumulative_accounted_usd':str(opening+total),'budget_usd':'.50','provider_pin':'wafer','automatic_retries':0}
    save('summary.json',summary);ledger(rows,unchanged)
    table='\n'.join(f"| {x['model'].split('/')[-1]} | {x['case']} | {x['status']} | {x.get('total_output_tokens','unknown')}/{x['output_cap']} | {x['latency_ms']/1000:.2f} |" for x in rows)
    note='\n\n## DeepSeek isolated diagnostic batch\n\nNo game moves applied. Both series remain on HOLD. Provider: Wafer; retries: zero.\n\n| Model | Case | Result | Output/cap | Seconds |\n|---|---|---|---:|---:|\n'+table
    note+='\n\nDiagnostic accounted cost: $'+str(total)+'. Separate from frozen series accounting. [Receipts](evidence/deepseek-diagnostic/receipts.json). Truncation tests the boundary, not a usable game action. One probe per condition cannot establish reliability.\n'
    path=ROOT/'README.md';path.write_text(path.read_text()+note)
    save('manifest.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file()})
    if not unchanged:raise ValueError('GAME_EVIDENCE_CHANGED')

if __name__=='__main__':main()
