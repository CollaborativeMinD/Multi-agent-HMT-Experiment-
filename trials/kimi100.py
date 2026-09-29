"""Authorized Kimi cohort-1 field evaluation using the verified v3 game harness."""
from __future__ import annotations
import json, os, sys, time
from decimal import Decimal as D
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'trials'),str(ROOT/'diagnostics'),str(ROOT/'baseline'),str(ROOT/'scripts')]
import strategy100 as base
import seat_tracer as tracer
r,p,h=base.r,base.p,base.h
OUT=ROOT/'evidence/kimi100'
PROFILE=tracer.PROFILES[0]
ORIGINAL_SELECT=base.ORIGINAL_SELECT
LIMITS:dict[str,D]={}


def fingerprints()->dict[str,str]:
    return {str(x.relative_to(ROOT)):p.hashlib.sha256(x.read_bytes()).hexdigest()
            for x in (ROOT/'evidence').rglob('*') if x.is_file() and OUT not in x.parents}


def opening_accounting()->dict[str,str]:
    opening=json.loads((ROOT/'evidence/strategy-v3-flash/summary.json').read_text())['accounting_usd']
    last=json.loads((ROOT/'evidence/seat-tracer-kimi-mistral/summary.json').read_text())
    opening['openrouter']=last['openrouter_cumulative_accounted_usd']
    return opening


def make_request(view:dict)->dict:
    req=tracer.request(PROFILE,{'kind':'game','cap':8192,'view':r.compact(view)})
    expected=r.RULES+'\n'+r.canonical(r.compact(view)).decode()
    if req['messages'][0]['content']!=expected:raise ValueError('PROMPT_PARITY_HOLD')
    return req


def select(model:dict,view:dict)->tuple[dict,dict]:
    r.LIMIT=LIMITS[model['account']]
    if model['account']!='openrouter' or len(view['legal'])==1:return ORIGINAL_SELECT(model,view)
    req=make_request(view);spec={'kind':'gameplay','case_id':'GAME','cap':8192}
    row=tracer.receipt(req,PROFILE,spec,{'pricing':model['native_prices']},view['turn'])
    reserve=D(row['reserved_usd'])
    if row['input_reserve']>20000 or r.spent['openrouter']+reserve>r.LIMIT:raise ValueError('BUDGET_OR_INPUT_HOLD')
    cooldown=max(0,30-(time.monotonic()-r.last_finished.get('openrouter',-1000)))
    if cooldown:time.sleep(cooldown)
    row.update(provider='openrouter',hand=view['handNumber'],turn=view['turn'],seat=view['you'],attempt=1,
               cooldown_seconds=round(cooldown,3),output_reserve=8192+24576)
    r.spent['openrouter']+=reserve;p.save('inflight.json',row)
    tracer.call(req,row,spec,os.environ['OPENROUTER_API_KEY'])
    r.last_finished['openrouter']=time.monotonic()
    if row.get('reason') in ['USAGE_INVALID','USAGE_PARTITION_INVALID']:row['accounted_usd']=str(reserve)
    row['output_tokens_including_reasoning']=row.get('total_output_tokens',0)
    if row.get('status')=='PASS':row['estimated_cost_usd']=row['accounted_usd']
    r.spent['openrouter']+=D(row['accounted_usd'])-reserve;r.emit('calls',row)
    p.save('inflight.json',{'status':'RECORDED','request_sha256':row['request_sha256']})
    if row['status']!='PASS':raise ValueError('MODEL_HOLD:'+str(row.get('reason','UNKNOWN')))
    return view['legal'][row['choice']],{'kind':'MODEL_CHOICE','call':row}


def update_readme(summary:dict)->None:
    path=ROOT/'README.md';text=path.read_text();g=summary['game']
    start='<!-- KIMI100:BEGIN -->';end='<!-- KIMI100:END -->'
    block='\n'.join([start,'## Kimi cohort-1 field evaluation','',
      'Strict 100-point game; seed 707; v3 guidance; Moonshot AI mxfp4; low reasoning.',
      f"Status: **{g['status']}**. Hands: {g['hands']}. OpenAI + Google: {g['scores'][0]}; Anthropic + Kimi: {g['scores'][1]}.",
      '[Summary](evidence/kimi100/summary.json) · [Replay](evidence/kimi100/frontier-pro/Whiz_100_Baseline_Replay.html)',
      'Prior tracer metadata HOLDs remain preserved. One game is not a general ranking or permanent seat assignment.',
      'Cumulative accounting: '+json.dumps(summary['accounting_usd']),end])
    if start in text:text=text[:text.index(start)]+block+text[text.index(end)+len(end):]
    else:text+='\n\n'+block+'\n'
    path.write_text(text)


def prepare()->tuple[list[dict],dict[str,str],dict[str,str]]:
    global LIMITS
    if OUT.exists() or os.environ.get('GITHUB_RUN_ATTEMPT','1')!='1':raise ValueError('RERUN_BLOCKED')
    p.OUT=OUT;base.OUT=OUT;base.PREVIOUS=ROOT/'evidence/kimi100-preparation';h.OUT=OUT
    before=fingerprints();delta=base.clarify_rules()
    p.save('prompt-delta.json',delta);p.save('pro-evidence-fingerprints.json',before)
    limits=json.loads((ROOT/'config/strategy-v3-budget.json').read_text())
    LIMITS={k:D(v)-D('.02') for k,v in limits['cumulative_ceilings_usd'].items()}
    opening=opening_accounting();r.spent={k:D(v) for k,v in opening.items()}
    manifest=json.loads(r.MODEL_FILE.read_text())
    models=[next(m for m in manifest['models'] if m['cohort']=='frontier' and m['account']==k) for k in opening]
    ep=tracer.admit(PROFILE,tracer.get('https://openrouter.ai/api/v1/models'));prices=ep['pricing']
    models[3]={**models[3],'model':PROFILE['model'],'native_prices':prices,
      'provider':{'only':[PROFILE['tag']],'allow_fallbacks':False,'require_parameters':True}}
    models[3]['standard_text_usd_per_million_tokens']={k:str(D(prices[v])*1000000) for k,v in [('input','prompt'),('output','completion')]}
    p.save('plan.json',{'target':100,'seed':707,'max_hands':6,'max_actions':336,'models':models,
      'reasoning_candidate':{'effort':'low'},'output_cap':8192,'deadline_seconds':240,'opening_accounting_usd':opening,
      'prompt_version':delta['version'],'prompt_sha256':delta['new_sha256'],'budget':limits,'free_play':False,
      'user_authorized_gameplay_despite_metadata_hold':True,'no_retries':True,'permanent_seat_assignment':False})
    base.pro_fingerprints=fingerprints;base.update_readme=update_readme;r.select=select
    return models,opening,before


def main()->None:
    models,opening,before=prepare()
    game={'id':'frontier-pro','cohort':'frontier','seed':707,'status':'IN_PROGRESS','hands':0,'actions':0,'scores':[0,0]}
    for _ in range(6):
        game=h.play_hand(game,models,{'max_hands_per_game':6})
        assert fingerprints()==before
        base.report(game,opening,p.fingerprints())
        if game['status']!='IN_PROGRESS':break
        time.sleep(30)
    if game['status']!='COMPLETE':raise SystemExit(2)

if __name__=='__main__':main()
