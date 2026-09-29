"""Bounded strict-Whiz baseline. Full observer evidence never enters model prompts."""
from __future__ import annotations
import hashlib,json,os,signal,subprocess,sys,time,urllib.request,urllib.error
from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path
from typing import Any
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import smoke
smoke.CAP=8192  # User-authorized doubling of the prior gameplay cap.
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'evidence';OUT.mkdir(exist_ok=True)
LIMIT=Decimal('3.00')
spent={p:Decimal('0') for p in ['openai','anthropic','gemini','openrouter']}
last_finished:dict[str,float]={}
MODEL_FILE=ROOT.parent/'config/models.lock.json'
RESUME=ROOT/'resume8192'
SOURCE_RUN=36496680649
RULES=('Play strict Whiz Spades to win your partnership game to 100. Four seats; partner opposite. '
       'Bid nil (0) or exactly your spade count. Nil +/-100; no blind nil or table talk. '
       'Positive contracts: at least the team bid, +10/bid trick if made, -10/bid trick if set. '
       'Extra tricks +1 point/bag; ten bags -100. Nil tricks never help partner contract; '
       'failed-nil tricks are bags even when partner is set. Follow suit; spades trump. '
       'Do not lead spades until broken unless only spades remain. Ace high. '
       'Use only your private hand and public information below. Select the zero-based index '
       'of your preferred legal action. Return only {"choice": integer}. No explanation.')

def canonical(x:Any)->bytes:
    return json.dumps(x,sort_keys=True,separators=(',',':')).encode()

def emit(kind:str,value:dict[str,Any])->None:
    value={'utc':datetime.now(timezone.utc).isoformat(),**value}
    with (OUT/(kind+'.jsonl')).open('a') as f:f.write(json.dumps(value,separators=(',',':'))+'\n')

def engine(proc:subprocess.Popen,cmd:dict[str,Any])->dict[str,Any]:
    proc.stdin.write(json.dumps(cmd)+'\n');proc.stdin.flush()
    row=json.loads(proc.stdout.readline())
    if not row.get('ok'):raise ValueError('ENGINE_REJECTED')
    return row['result']

def compact(v:dict[str,Any])->dict[str,Any]:
    if 'deckSeed' in v or any(p['hand'] is not None for p in v['players'] if p['id']!=v['you']):
        raise ValueError('PRIVATE_VIEW_BREACH')
    keys=['you','partner','players','phase','handNumber','trickNumber','scores','bags','spadesBroken','plays','lastTrick','history','legal']
    return {k:v[k] for k in keys}

def request(model:dict[str,Any],v:dict[str,Any])->tuple[str,dict[str,Any]]:
    smoke.PROMPT=RULES+'\n'+canonical(compact(v)).decode()
    smoke.SCHEMA={'type':'object','properties':{'choice':{'type':'integer','enum':list(range(len(v['legal'])))}},'required':['choice'],'additionalProperties':False}
    url,body=smoke.request_spec(model['account'],model['model'])
    if model['account'] in ['openai','anthropic']:
        key='reasoning' if model['account']=='openai' else 'output_config';body[key]['effort']='medium'
    elif model['account']=='gemini':body['generationConfig']['thinkingConfig']['thinkingLevel']='medium'
    elif '2.4t' in model['model']:body['reasoning']={'effort':'medium'}
    return url,body

def headers(provider:str)->dict[str,str]:
    key=os.environ.get(provider.upper()+'_API_KEY','').strip()
    if not key:raise ValueError('MISSING_SECRET')
    h={'Content-Type':'application/json','Accept':'application/json'}
    if provider=='anthropic':h.update({'x-api-key':key,'anthropic-version':'2023-06-01'})
    elif provider=='gemini':h['x-goog-api-key']=key
    else:h['Authorization']='Bearer '+key
    return h

def parse(body:dict[str,Any],m:dict[str,Any],n:int,row:dict[str,Any])->int:
    r=smoke.extract(m['account'],body)
    ni,no=smoke.token_count(r['input']),smoke.token_count(r['output'])
    rates=m['standard_text_usd_per_million_tokens']
    actual=(ni*Decimal(str(rates['input']))+no*Decimal(str(rates['output'])))/1000000
    row.update(input_tokens=ni,output_tokens_including_reasoning=no,estimated_cost_usd=str(actual),
               finish_reason=r.get('reason'),returned_model=r.get('model'),returned_provider=r.get('route'),
               response_sha256=hashlib.sha256(canonical(body)).hexdigest())
    if ni>row['input_reserve'] or no>smoke.CAP:raise ValueError('TOKEN_RESERVATION_EXCEEDED')
    if not r['complete']:raise ValueError('INCOMPLETE_OR_REFUSAL')
    if r['model']!=m['model']:raise ValueError('MODEL_ID_MISMATCH')
    if m['account']=='openrouter' and r.get('route')!='Alibaba':raise ValueError('PROVIDER_ROUTE_MISMATCH')
    def unique(pairs:list)->dict:
        d={}
        for k,val in pairs:
            if k in d:raise ValueError('DUPLICATE_KEY')
            d[k]=val
        return d
    answer=json.loads(r['text'],object_pairs_hook=unique)
    if type(answer)is not dict or set(answer)!={'choice'} or type(answer['choice'])is not int or not 0<=answer['choice']<n:
        raise ValueError('ACTION_SCHEMA_INVALID')
    row.update(status='PASS',returned_model=r['model'],choice=answer['choice'])
    return answer['choice']

def call(m:dict[str,Any],v:dict[str,Any],attempt:int)->tuple[int|None,dict[str,Any]]:
    provider=m['account'];url,body=request(m,v);encoded=canonical(body)
    input_reserve=len(encoded)+2048
    rates=m['standard_text_usd_per_million_tokens']
    reserve=(input_reserve*Decimal(str(rates['input']))+smoke.CAP*Decimal(str(rates['output'])))/1000000
    if input_reserve>20000 or spent[provider]+reserve>LIMIT:raise ValueError('BUDGET_OR_INPUT_HOLD')
    h=headers(provider);cool=max(0,30-(time.monotonic()-last_finished.get(provider,-1000))) if provider=='openrouter' else 0
    if cool:time.sleep(cool)
    spent[provider]+=reserve
    row=dict(model=m['model'],provider=provider,hand=v['handNumber'],turn=v['turn'],seat=v['you'],attempt=attempt,
             reserved_usd=str(reserve),input_reserve=input_reserve,output_cap=smoke.CAP,status='HOLD',http_status=None,
             cooldown_seconds=round(cool,3),request_sha256=hashlib.sha256(url.encode()+b'\n'+encoded).hexdigest())
    started=time.monotonic();choice=None
    try:
        signal.signal(signal.SIGALRM,smoke.timeout_handler);signal.alarm(120)
        req=urllib.request.Request(url,data=encoded,headers=h,method='POST')
        with urllib.request.build_opener(smoke.NoRedirect()).open(req,timeout=110) as response:
            row['http_status']=response.status;raw=response.read(1048577)
        if len(raw)>1048576:raise ValueError('RESPONSE_TOO_LARGE')
        choice=parse(json.loads(raw),m,len(v['legal']),row)
    except urllib.error.HTTPError as exc:
        row['http_status']=exc.code;row['reason']='HTTP_ERROR'
    except (urllib.error.URLError,TimeoutError):row['reason']='NETWORK_OR_TIMEOUT'
    except ValueError as exc:
        allowed={'TOKEN_RESERVATION_EXCEEDED','INCOMPLETE_OR_REFUSAL','MODEL_ID_MISMATCH','PROVIDER_ROUTE_MISMATCH',
                 'ACTION_SCHEMA_INVALID','DUPLICATE_KEY','RESPONSE_TOO_LARGE','USAGE_INVALID'}
        row['reason']=str(exc) if str(exc) in allowed else 'MALFORMED_RESPONSE'
    except (TypeError,KeyError,IndexError):row['reason']='RESPONSE_OR_CONTRACT_HOLD'
    finally:
        signal.alarm(0);last_finished[provider]=time.monotonic()
    row['latency_ms']=round((time.monotonic()-started)*1000)
    if 'estimated_cost_usd' in row:spent[provider]+=Decimal(row['estimated_cost_usd'])-reserve
    emit('calls',row)
    return choice,row

def select(m:dict[str,Any],v:dict[str,Any])->tuple[dict[str,Any],dict[str,Any]]:
    if len(v['legal'])==1:return v['legal'][0],{'kind':'FORCED_SINGLE_LEGAL_ACTION'}
    choice,row=call(m,v,1)
    if choice is None:raise ValueError('MODEL_HOLD:'+m['model'])
    return v['legal'][choice],{'kind':'MODEL_CHOICE','call':row}

def restore(proc:subprocess.Popen,cohort:str,models:list,frame:dict)->tuple[dict,int]:
    source=RESUME/f'{cohort}.jsonl'
    if not source.exists():
        emit(cohort,{'kind':'INITIAL','seed':7,'models':[m['model'] for m in models],**frame})
        return frame,0
    rows=[json.loads(x) for x in source.read_text().splitlines()]
    if rows[0]['hash']!=frame['hash'] or rows[0]['models']!=[m['model'] for m in models]:
        raise ValueError('RESUME_INITIAL_MISMATCH')
    count=0
    for row in rows:
        if row['kind']=='ACTION':
            frame=engine(proc,{'op':'step','action':row['action']})
            if frame['hash']!=row['hash']:raise ValueError('RESUME_STATE_MISMATCH')
            count+=1
        if row['kind'] in ['INITIAL','ACTION','RESUME']:emit(cohort,row)
    emit(cohort,{'kind':'RESUME','source_run':SOURCE_RUN,'actions':count,'output_cap':smoke.CAP})
    return frame,count


def game(cohort:str,models:list[dict[str,Any]])->dict[str,Any]:
    proc=subprocess.Popen(['node',str(ROOT/'engine.mjs')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    frame=engine(proc,{'op':'init','seed':7,'id':'whiz100-'+cohort})
    frame,start=restore(proc,cohort,models,frame)
    result={'cohort':cohort,'status':'HOLD','models':[m['model'] for m in models]}
    try:
        for i in range(start,6*56):
            if frame['snapshot']['status']=='ended':break
            v=engine(proc,{'op':'observe'});m=models[v['activePlayerIndex']]
            action,decision=select(m,v)
            frame=engine(proc,{'op':'step','action':action})
            emit(cohort,{'kind':'ACTION','index':i,'player':v['you'],'observation':compact(v),
                          'action':action,'decision':decision,**frame})
            if frame['newLog'] and any(x['type']=='HAND' for x in frame['newLog']):
                print('HAND_PROGRESS='+json.dumps({'cohort':cohort,'hand':v['handNumber'],'scores':frame['snapshot']['scores']}),flush=True)
        result.update(status='COMPLETE' if frame['snapshot']['status']=='ended' else 'HAND_LIMIT_HOLD',
                      hands=frame['snapshot']['handNumber'],scores=frame['snapshot']['scores'],
                      winners=frame['snapshot'].get('winnerIds',[]))
    except ValueError as exc:result['reason']=str(exc)
    finally:
        verify=engine(proc,{'op':'verify'});result.update(verify)
        # Keep engine state distinct from campaign completion status.
        result['engine_status']=verify['status'];result['status']='COMPLETE' if verify['status']=='ended' else 'HOLD'
        emit(cohort,{'kind':'FINAL',**result});proc.terminate();proc.wait(timeout=5);proc.stdin.close();proc.stdout.close()
    return result

def main()->int:
    if os.environ.get('GITHUB_RUN_ATTEMPT','1')!='1':raise ValueError('RERUN_BLOCKED')
    manifest=json.loads(MODEL_FILE.read_text());results=[]
    prior=RESUME/'summary.json'
    if prior.exists():
        for p,cost in json.loads(prior.read_text())['accounting_usd'].items():spent[p]=Decimal(cost)
        (OUT/'prior_calls.jsonl').write_bytes((RESUME/'calls.jsonl').read_bytes())
    if not all(m['inference_verified'] for m in manifest['models']):raise ValueError('ROSTER_NOT_VERIFIED')
    for cohort in ['frontier','mainstream']:
        models=[next(m for m in manifest['models'] if m['cohort']==cohort and m['account']==p) for p in spent]
        result=game(cohort,models);results.append({k:v for k,v in result.items() if k!='log'})
        if result['status']!='COMPLETE':break
    report=dict(utc=datetime.now(timezone.utc).isoformat(),commit=os.environ.get('GITHUB_SHA'),
                target=100,mode='strict_whiz',seed=7,results=results,output_cap=smoke.CAP,
                resumed_from_run=SOURCE_RUN if prior.exists() else None,
                accounting_usd={p:str(v) for p,v in spent.items()},per_account_limit=str(LIMIT),
                nonclaims=['single unrotated partnership game per cohort','legal-action-assisted','not general intelligence ranking'])
    (OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print('BASELINE_RECEIPT='+json.dumps(report),flush=True)
    return int(len(results)!=2 or any(r['status']!='COMPLETE' for r in results))

if __name__=='__main__':raise SystemExit(main())
