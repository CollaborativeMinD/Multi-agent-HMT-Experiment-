"""Reused checkpointed-hand implementation, isolated 100-point Pro trial."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
from typing import Any
import runner as r
BASE=Path(__file__).resolve().parents[1]/"baseline"
OUT=BASE.parent/"evidence/pro100"
def rows(path:Path)->list[dict]:
    return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []

def start_game(game:dict,models:list[dict])->tuple[Any,dict,int]:
    proc=subprocess.Popen(['node',str(BASE/'engine.mjs')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    frame=r.engine(proc,{'op':'init','seed':game['seed'],'id':'pro100-'+game['id'],'target':100})
    path=r.OUT/(game['cohort']+'.jsonl');prior=rows(path);count=0
    try:
        if not prior:r.emit(game['cohort'],{'kind':'INITIAL','seed':game['seed'],'target':100,'models':[m['model'] for m in models],**frame})
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


