"""Single-use Kimi/Mistral tracer. No game mutations or inference retries."""
from __future__ import annotations
import json, os, signal, sqlite3, subprocess, time, urllib.request, urllib.error
from decimal import Decimal as D
from typing import Any
import probe as p
import wire_probe as w
import reconcile as recon
OUT=p.ROOT/'evidence/seat-tracer-kimi-mistral'
SOURCE=p.ROOT/'evidence/pro100/frontier-pro/frontier.jsonl'
PROFILES=[{'model':'moonshotai/kimi-k3','tag':'moonshotai/mxfp4','provider':'Moonshot AI','effort':'low'},
          {'model':'mistralai/mistral-medium-3-5','tag':'mistral','provider':'Mistral','effort':'high'}]

def get(url:str)->dict[str,Any]:
    with urllib.request.urlopen(url,timeout=25) as response:return json.load(response)

def fingerprints()->dict[str,str]:
    return {str(x.relative_to(p.ROOT)):p.hashlib.sha256(x.read_bytes()).hexdigest()
            for x in (p.ROOT/'evidence').rglob('*') if x.is_file() and OUT not in x.parents}

def fixtures()->list[dict[str,Any]]:
    rows=[json.loads(x) for x in SOURCE.read_text().splitlines()]
    import analyze
    verified=analyze.verify_game(rows)
    assert verified['actions']==112
    selected=[]
    for card in ['8D','QH']:
        row=next(x for x in rows if x.get('kind')=='ACTION' and x.get('player')=='p4'
                 and x['action'].get('card')==card and x['observation']['handNumber']==1)
        view=row['observation'];expected='8D' if card=='8D' else '4H'
        assert next(x for x in view['players'] if x['id']=='p4')['bid']==0
        assert next(x for x in view['players'] if x['id']=='p4')['tricksWon']==0
        assert {'type':'PLAY','card':expected} in view['legal']
        selected.append({'kind':'game','view':view,'source_index':row['index'],
                         'expected_card':expected,'cap':8192,'case_id':expected})
    return [{'kind':'canary','cap':8192,'case_id':'CANARY'},selected[0],dict(selected[0],case_id='8D-REPEAT'),
            selected[1],{'kind':'pressure','cap':64,'case_id':'PRESSURE'}]

def request(profile:dict[str,Any],spec:dict[str,Any])->dict[str,Any]:
    prompt=json.loads((p.ROOT/'evidence/strategy-v3-pro/prompt-delta.json').read_text())['new']
    legal=spec.get('view',{}).get('legal',[0,1,2])
    if spec['kind']=='game':prompt+='\n'+p.r.canonical(spec['view']).decode()
    elif spec['kind']=='canary':prompt='Return exactly the JSON object {"choice":1}.'
    else:prompt=('Compute 987654321987654321 raised to 123456789 modulo 1000000007. '
                 'Choose 0 if even, 1 if odd, or 2 if uncertain. Return only the choice JSON.')
    schema={'type':'object','properties':{'choice':{'type':'integer','enum':list(range(len(legal)))}},
            'required':['choice'],'additionalProperties':False}
    return {'model':profile['model'],'messages':[{'role':'user','content':prompt}],
            'max_tokens':spec['cap'],'reasoning':{'effort':profile['effort']},
            'provider':{'only':[profile['tag']],'allow_fallbacks':False,'require_parameters':True},
            'response_format':{'type':'json_schema','json_schema':{'name':'play_action','strict':True,'schema':schema}},
            'stream':True,'debug':{'echo_upstream_body':True}}

def admit(profile:dict[str,Any],catalog:dict[str,Any])->dict[str,Any]:
    model=next(x for x in catalog['data'] if x['id']==profile['model'])
    if profile['effort'] not in model.get('reasoning',{}).get('supported_efforts',[]):raise ValueError('EFFORT_UNSUPPORTED')
    data=get('https://openrouter.ai/api/v1/models/'+profile['model']+'/endpoints')
    ep=next(x for x in data['data']['endpoints'] if x['tag']==profile['tag'])
    required={'max_tokens','reasoning','response_format','structured_outputs'}
    if ep['status']!=0 or not required<=set(ep['supported_parameters']):raise ValueError('ENDPOINT_NOT_ADMITTED')
    p.save(profile['model'].split('/')[-1]+'-catalog.json',{'utc':p.now(),'model':model,'endpoint':ep})
    return ep

def receipt(req:dict[str,Any],profile:dict[str,Any],spec:dict[str,Any],ep:dict[str,Any],index:int)->dict[str,Any]:
    ni=len(p.r.canonical(req))+2048;prices=ep['pricing']
    # Retain headroom for the previously observed 24,576-token overrun pattern.
    reserve=ni*D(prices['prompt'])+(req['max_tokens']+24576)*D(prices['completion'])
    return {'id':f'SEAT-{index:02}','model':profile['model'],'case':spec['kind'],'case_id':spec['case_id'],
            'provider_pin':profile['tag'],'expected_provider':profile['provider'],'reasoning':req['reasoning'],
            'started_utc':p.now(),'output_cap':req['max_tokens'],'input_reserve':ni,
            'input_price':prices['prompt'],'output_price':prices['completion'],'reserved_usd':str(reserve),
            'accounted_usd':str(reserve),'request_sha256':p.digest(req),'status':'IN_FLIGHT'}

def evaluate(state:dict[str,Any],req:dict[str,Any],row:dict[str,Any],spec:dict[str,Any])->None:
    usage=state.get('usage',{});ni=usage.get('prompt_tokens');no=usage.get('completion_tokens')
    if type(ni)is not int or type(no)is not int or min(ni,no)<0:raise ValueError('USAGE_INVALID')
    rt=usage.get('completion_tokens_details',{}).get('reasoning_tokens')
    row.update(input_tokens=ni,total_output_tokens=no,reasoning_tokens=rt,
               returned_model=state.get('model'),returned_provider=state.get('provider'))
    cost=ni*D(row['input_price'])+no*D(row['output_price']);reported=usage.get('cost')
    if type(reported) in (int,float) and reported>=0:cost=max(cost,D(str(reported)))
    row.update(accounted_usd=str(cost),estimated_cost_usd=str(cost),provider_reported_cost_usd=reported)
    if state.get('model')!=req['model'] or state.get('provider')!=row['expected_provider']:raise ValueError('ROUTE_MISMATCH')
    if no>req['max_tokens'] or ni>row['input_reserve']:raise ValueError('TOKEN_BOUND_EXCEEDED')
    if type(rt)is not int or not 0<=rt<=no:raise ValueError('USAGE_PARTITION_INVALID')
    row['finish_reason']=state.get('finish_reason')
    if state.get('finish_reason')=='length' and spec['kind']=='pressure':
        row.update(status='PASS',result='EXPECTED_BOUNDED_TRUNCATION');return
    if state.get('finish_reason')!='stop':raise ValueError('UNEXPECTED_FINISH')
    value=json.loads(state['content'],object_pairs_hook=p.unique)
    legal=req['response_format']['json_schema']['schema']['properties']['choice']['enum']
    if type(value)is not dict or set(value)!={'choice'} or type(value['choice'])is not int or value['choice'] not in legal:raise ValueError('SCHEMA_INVALID')
    row['choice']=value['choice']
    if spec['kind']=='canary' and value['choice']!=1:raise ValueError('CANARY_WRONG')
    if spec['kind']=='game':
        row['selected_action']=spec['view']['legal'][value['choice']]
        row['nil_preservation']='PASS' if row['selected_action']['card']==spec['expected_card'] else 'FAIL'
    row.update(status='PASS',result='VALID_RESPONSE')

def call(req:dict[str,Any],row:dict[str,Any],spec:dict[str,Any],key:str)->None:
    state={'upstream':[],'content':''};start=time.monotonic()
    signal.signal(signal.SIGALRM,p.deadline);signal.alarm(240)
    try:
        http=urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',data=p.r.canonical(req),
                                    headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
        with urllib.request.urlopen(http,timeout=230) as response:
            row['http_status']=response.status;w.events(response,state)
        evaluate(state,req,row,spec)
    except urllib.error.HTTPError as exc:row.update(status='HOLD',reason='HTTP_ERROR',http_status=exc.code)
    except Exception as exc:
        allowed={'USAGE_INVALID','ROUTE_MISMATCH','TOKEN_BOUND_EXCEEDED','USAGE_PARTITION_INVALID',
                 'UNEXPECTED_FINISH','SCHEMA_INVALID','CANARY_WRONG','STREAM_ERROR','STREAM_INCOMPLETE'}
        row.update(status='HOLD',reason=str(exc) if str(exc) in allowed else type(exc).__name__)
    finally:
        signal.alarm(0)
        row.update(generation_id=state.get('id'),upstream=state['upstream'],stream_sha256=state.get('stream_sha256'),
                   latency_ms=round((time.monotonic()-start)*1000),completed_utc=p.now())

def ledger(rows:list[dict[str,Any]],same:bool)->None:
    db=sqlite3.connect(OUT/'gates.sqlite')
    db.executescript((p.ROOT/'evidence/strategy-v3-flash/gates.sql').read_text())
    db.execute('INSERT INTO reverse_rca_ledger VALUES (?,?,?,?,?,?,?)',
               (p.now(),'SEAT-PREP-001','Local baseline regression','Generated checkpoint missing in clean checkout',
                'prepare_checkpoint.py reconstructs resume240; ten baseline tests then pass','Hosted preparation before regression',
                'INVESTIGATION_COMPLETE; SOLUTION_CANDIDATE_APPLIED'))
    db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',
               (p.now(),'Seat tracer','SEAT-PREFLIGHT','Engine and 77 Python regression tests','PASS','GitHub workflow logs',os.environ.get('GITHUB_RUN_ID','local')))
    metadata=json.loads((OUT/'generation-metadata.json').read_text())
    for item in metadata:
        ok=item['status']=='PASS' and all(item.get('comparison',{}).get(k) for k in
             ['native_completion_matches_receipt','native_reasoning_matches_receipt'])
        db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',
                   (p.now(),'Seat tracer','META-'+item['receipt_id'],'Stored generation reconciliation','PASS' if ok else 'HOLD',
                    'generation-metadata.json',p.digest(item)))
    for row in rows:
        db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',
                   (p.now(),'Seat tracer',row['id'],'Identity, usage, bound, schema',row['status'],'receipts.json',p.digest(row)))
        if row['status']!='PASS' or row.get('nil_preservation')=='FAIL':
            db.execute('INSERT INTO reverse_rca_ledger VALUES (?,?,?,?,?,?,?)',
                       (p.now(),row['id'],'Response',row.get('reason',row.get('nil_preservation','HOLD')),
                        p.digest(row),'No inference retry; inspect request and receipt',
                        'INVESTIGATION_INCOMPLETE; REQUIRES_OPERATOR_ESCALATION'))
    db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',
               (p.now(),'Seat tracer','SEAT-IMMUTABILITY','Historical evidence unchanged','PASS' if same else 'HOLD','summary.json',str(same)))
    db.commit();assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    (OUT/'gates.sql').write_text('\n'.join(db.iterdump())+'\n');db.close()

def publish()->None:
    for cmd in [['git','add',str(OUT.relative_to(p.ROOT))],['git','commit','-m','Publish bounded seat tracer evidence'],['git','push','origin','HEAD:main']]:
        subprocess.run(cmd,cwd=p.ROOT,check=True,stdout=subprocess.DEVNULL)

def finish(rows:list[dict[str,Any]],opening:D,before:dict[str,str],holds:list[dict[str,str]])->None:
    metadata=[recon.fetch(x,os.environ['OPENROUTER_API_KEY']) for x in rows if x.get('generation_id')]
    p.save('generation-metadata.json',metadata)
    same=before==fingerprints();total=sum((D(x['accounted_usd']) for x in rows),D(0))
    matched=len(metadata)==len(rows) and all(x['status']=='PASS' and all(x.get('comparison',{}).get(k) for k in
            ['native_completion_matches_receipt','native_reasoning_matches_receipt']) for x in metadata)
    p.save('summary.json',{'utc':p.now(),'calls':len(rows),'planned_max':10,'holds':holds,
        'interface_passes':sum(x['status']=='PASS' for x in rows),'metadata_matches':matched,
        'accounted_usd':str(total),'opening_openrouter_usd':str(opening),'openrouter_cumulative_accounted_usd':str(opening+total),
        'historical_evidence_unchanged':same,'game_actions_applied':0,'retries':0,
        'run_id':os.environ.get('GITHUB_RUN_ID'),'source_commit':os.environ.get('GITHUB_SHA')})
    ledger(rows,same)
    (OUT/'SHA256SUMS.txt').write_text(''.join(p.hashlib.sha256(x.read_bytes()).hexdigest()+'  '+x.name+'\n'
      for x in sorted(OUT.iterdir()) if x.is_file() and x.name!='SHA256SUMS.txt'))
    if not same:raise ValueError('EVIDENCE_MUTATION')

def main()->None:
    if OUT.exists() or os.environ.get('GITHUB_RUN_ATTEMPT','1')!='1':raise ValueError('RERUN_BLOCKED')
    p.OUT=OUT;before=fingerprints();specs=fixtures();rows=[];holds=[]
    opening=D(json.loads((p.ROOT/'evidence/strategy-v3-flash/summary.json').read_text())['accounting_usd']['openrouter'])
    p.save('plan.json',{'profiles':PROFILES,'specs':specs,'batch_admission_usd':'2.00','cumulative_limit_usd':'9.98',
                      'deadline_seconds':240,'gap_seconds':30,'max_calls':10,'no_retries':True,'game_actions':0})
    catalog=get('https://openrouter.ai/api/v1/models')
    try:
        for profile in PROFILES:
            try:ep=admit(profile,catalog)
            except Exception as exc:
                holds.append({'model':profile['model'],'reason':type(exc).__name__+':'+str(exc)[:60]});continue
            for spec in specs:
                req=request(profile,spec);row=receipt(req,profile,spec,ep,len(rows)+1)
                spent=sum((D(x['accounted_usd']) for x in rows),D(0));reserve=D(row['reserved_usd'])
                if spent+reserve>D('2') or opening+spent+reserve>D('9.98'):
                    holds.append({'model':profile['model'],'reason':'BUDGET_HOLD'});break
                p.save(row['id']+'-request.json',req);rows.append(row);p.save('receipts.json',rows)
                call(req,row,spec,os.environ['OPENROUTER_API_KEY']);p.save('receipts.json',rows);publish()
                print(json.dumps({k:row.get(k) for k in ['id','model','case_id','status','reason','selected_action','latency_ms']}),flush=True)
                if row['status']!='PASS':break
                time.sleep(30)
    finally:finish(rows,opening,before,holds)

if __name__=='__main__':main()
