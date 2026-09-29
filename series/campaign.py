"""One strict, checkpointed hand per invocation; no automatic paid retry."""
from __future__ import annotations
import hashlib,json,os,subprocess,sys,time
from decimal import Decimal
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/('baseline' if (ROOT.parent/'baseline').exists() else 'whiz_baseline')
sys.path.insert(0,str(BASE))
import runner as r
OUT=ROOT.parent/'evidence/whiz300'
PLAN=ROOT/'plan.json'

def read(path:Path)->Any:
    return json.loads(path.read_text())

def atomic(path:Path,value:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(path)

def rows(path:Path)->list[dict]:
    return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []

def wins(games:list[dict],cohort:str)->list[int]:
    result=[0,0]
    for game in games:
        if game['cohort']!=cohort or game['status']!='COMPLETE':continue
        ids=game['winners']
        if ids not in [['p1','p3'],['p2','p4']]:raise ValueError('WINNER_CONTRACT_INVALID')
        result[int(ids==['p2','p4'])]+=1
    return result

def next_game(state:dict,plan:dict)->dict|None:
    order=['frontier','mainstream']
    if state['next_cohort']=='mainstream':order.reverse()
    for cohort in order:
        if max(wins(state['games'],cohort))>=3:continue
        group=[g for g in state['games'] if g['cohort']==cohort]
        active=next((g for g in group if g['status']=='IN_PROGRESS'),None)
        if active:return active
        number=len(group)+1
        if number>5:raise ValueError('SERIES_TERMINATION_INVALID')
        game={'id':f'{cohort}-g{number:02d}','cohort':cohort,'number':number,
              'seed':plan['seeds'][number-1],'status':'IN_PROGRESS','hands':0,'actions':0,'scores':[0,0]}
        state['games'].append(game);return game
    return None

def accounting(plan:dict)->dict[str,Decimal]:
    result={p:Decimal(v) for p,v in plan['opening_accounting_usd'].items()}
    for path in sorted(OUT.glob('*/calls.jsonl')):
        for c in rows(path):result[c['provider']]+=Decimal(c.get('estimated_cost_usd',c['reserved_usd']))
    return result

def load_state(plan:dict)->dict:
    path=OUT/'series.json';digest=hashlib.sha256(PLAN.read_bytes()).hexdigest()
    state=read(path) if path.exists() else {'status':'IN_PROGRESS','plan_sha256':digest,'games':[],
      'next_cohort':'frontier','source_commit':os.environ.get('GITHUB_SHA'),'run_id':os.environ.get('GITHUB_RUN_ID')}
    if state['plan_sha256']!=digest:raise ValueError('PLAN_DRIFT')
    return state

def configure(plan:dict)->list[dict]:
    manifest=read(r.MODEL_FILE)
    if hashlib.sha256(r.MODEL_FILE.read_bytes()).hexdigest()!=plan['registry_sha256']:raise ValueError('ROSTER_DRIFT')
    if not all(m['inference_verified'] for m in manifest['models']):raise ValueError('ROSTER_NOT_VERIFIED')
    r.LIMIT=Decimal(plan['per_account_limit_usd']);r.spent=accounting(plan)
    r.RULES=r.RULES.replace('game to 100.','game to 300.')
    return manifest['models']

def start_game(game:dict,models:list[dict])->tuple[Any,dict,int]:
    proc=subprocess.Popen(['node',str(BASE/'engine.mjs')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    frame=r.engine(proc,{'op':'init','seed':game['seed'],'id':'whiz300-'+game['id'],'target':300})
    path=r.OUT/(game['cohort']+'.jsonl');prior=rows(path);count=0
    try:
        if not prior:r.emit(game['cohort'],{'kind':'INITIAL','seed':game['seed'],'target':300,'models':[m['model'] for m in models],**frame})
        else:
            if prior[0]['hash']!=frame['hash'] or prior[0]['models']!=[m['model'] for m in models]:raise ValueError('RESUME_INITIAL_MISMATCH')
            for row in prior:
                if row['kind']!='ACTION':continue
                frame=r.engine(proc,{'op':'step','action':row['action']});count+=1
                if frame['hash']!=row['hash']:raise ValueError('RESUME_STATE_MISMATCH')
            if frame['hash']!=prior[-1]['final_hash']:raise ValueError('RESUME_FINAL_MISMATCH')
            text=''.join(json.dumps(x,separators=(',',':'))+'\n' for x in prior if x['kind']!='FINAL')
            tmp=path.with_suffix('.tmp');tmp.write_text(text);tmp.replace(path)
        return proc,frame,count
    except Exception:
        proc.terminate();proc.wait();proc.stdin.close();proc.stdout.close();raise

def play_hand(game:dict,models:list[dict],plan:dict)->dict:
    r.OUT=OUT/game['id'];r.OUT.mkdir(parents=True,exist_ok=True)
    proc,frame,count=start_game(game,models);result=dict(game);reason=None
    try:
        hand=frame['snapshot']['handNumber']
        while frame['snapshot']['status']!='ended' and count<plan['max_hands_per_game']*56:
            v=r.engine(proc,{'op':'observe'});action,decision=r.select(models[v['activePlayerIndex']],v)
            frame=r.engine(proc,{'op':'step','action':action})
            r.emit(game['cohort'],{'kind':'ACTION','index':count,'player':v['you'],'observation':r.compact(v),
                                  'action':action,'decision':decision,**frame});count+=1
            if any(e['type']=='HAND' for e in frame['newLog']):break
        if frame['snapshot']['status']!='ended' and count>=plan['max_hands_per_game']*56:reason='HAND_LIMIT_HOLD'
    except ValueError as exc:reason=str(exc)
    finally:
        verified=r.engine(proc,{'op':'verify'});snap=frame['snapshot']
        status='HOLD' if reason else 'COMPLETE' if snap['status']=='ended' else 'IN_PROGRESS'
        completed=sum(e['type']=='HAND' for e in verified['log'])
        result.update(status=status,hands=completed,actions=count,scores=snap['scores'],winners=snap.get('winnerIds',[]),
                      final_hash=verified['final_hash'],replay_verified=verified['replay_verified'],reason=reason)
        r.emit(game['cohort'],{'kind':'FINAL',**result})
        proc.terminate();proc.wait(timeout=5);proc.stdin.close();proc.stdout.close()
    return result

def finish(state:dict,plan:dict)->None:
    state['accounting_usd']={p:str(v) for p,v in accounting(plan).items()}
    state['series_wins']={c:wins(state['games'],c) for c in ['frontier','mainstream']}
    if state['status']!='HOLD' and all(max(v)>=3 for v in state['series_wins'].values()):state['status']='COMPLETE'
    state['updated_utc']=r.datetime.now(r.timezone.utc).isoformat();atomic(OUT/'series.json',state)


def main()->int:
    if os.environ.get('GITHUB_RUN_ATTEMPT','1')!='1':raise ValueError('RERUN_BLOCKED')
    plan=read(PLAN);state=load_state(plan)
    if state['status']!='IN_PROGRESS':return 2 if state['status']=='HOLD' else 0
    models=configure(plan);game=next_game(state,plan)
    if game is None:finish(state,plan);return 0
    roster=[next(m for m in models if m['cohort']==game['cohort'] and m['account']==p) for p in r.spent]
    try:
        # Cooldown carries across hand-process boundaries, with a conservative full wait.
        if list(OUT.glob('*/calls.jsonl')):time.sleep(30)
        result=play_hand(game,roster,plan);game.update(result)
        if result['status']=='HOLD':state['status']='HOLD'
        state['next_cohort']='mainstream' if game['cohort']=='frontier' else 'frontier'
    except Exception as exc:
        state.update(status='HOLD',reason='ENGINE_OR_CHECKPOINT_HOLD',exception_type=type(exc).__name__)
    finish(state,plan);print(json.dumps(state),flush=True)
    return 2 if state['status']=='HOLD' else 0

if __name__=='__main__':raise SystemExit(main())
