"""One reviewed recovery request at the held bid; no retry loop or policy widening."""
from __future__ import annotations
import os
from time import sleep
import campaign as c

EXPECTED='87e9708f1c74d5105da73266f70a1af607223a1c1852af10777bb55218421914'

def recovery()->int:
    if os.environ.get('GITHUB_RUN_ATTEMPT','1')!='1':raise ValueError('RERUN_BLOCKED')
    plan=c.read(c.PLAN);state=c.load_state(plan)
    if state['status']!='HOLD' or state.get('recovery_attempted'):raise ValueError('RECOVERY_NOT_ADMITTED')
    game=next(g for g in state['games'] if g['id']=='mainstream-g01')
    if game['actions']!=2 or game['final_hash']!=EXPECTED:raise ValueError('RECOVERY_CHECKPOINT_MISMATCH')
    all_models=c.configure(plan);models=[next(m for m in all_models if m['cohort']=='mainstream' and m['account']==p) for p in c.r.spent]
    c.r.OUT=c.OUT/game['id'];proc,frame,count=c.start_game(game,models)
    state['recovery_attempted']=True;state['recovery_source_run']=36510344003;state['run_id']=os.environ.get('GITHUB_RUN_ID')
    reason=None
    try:
        view=c.r.engine(proc,{'op':'observe'});model=models[view['activePlayerIndex']]
        if model['model']!='qwen/qwen3.8-flash' or view['turn']!=2:raise ValueError('RECOVERY_PLAYER_MISMATCH')
        sleep(60)
        choice,receipt=c.r.call(model,view,2)
        if choice is None:reason='RECOVERY_HOLD:qwen/qwen3.8-flash'
        else:
            action=view['legal'][choice];frame=c.r.engine(proc,{'op':'step','action':action})
            c.r.emit('mainstream',{'kind':'ACTION','index':count,'player':view['you'],'observation':c.r.compact(view),
                     'action':action,'decision':{'kind':'MODEL_CHOICE','call':receipt},**frame});count+=1
    except ValueError as exc:reason=str(exc)
    finally:
        verified=c.r.engine(proc,{'op':'verify'})
        game.update(status='HOLD' if reason else 'IN_PROGRESS',actions=count,final_hash=verified['final_hash'],reason=reason)
        c.r.emit('mainstream',{'kind':'FINAL',**game});proc.terminate();proc.wait(timeout=5);proc.stdin.close();proc.stdout.close()
        state.update(status=game['status'],next_cohort='mainstream',recovery_commit=os.environ.get('GITHUB_SHA'))
        c.finish(state,plan)
    return 2 if reason else 0

if __name__=='__main__':raise SystemExit(recovery())
