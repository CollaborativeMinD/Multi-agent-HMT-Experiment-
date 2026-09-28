"""Offline verification and descriptive pilot metrics. Never calls a model API."""
import hashlib,json,statistics,subprocess,sys
from collections import Counter
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def rows(path):
    return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []

def transact(proc,cmd):
    proc.stdin.write(json.dumps(cmd)+'\n');proc.stdin.flush()
    value=json.loads(proc.stdout.readline());assert value['ok'],value
    return value['result']

def verify_game(records):
    proc=subprocess.Popen(['node',str(ROOT/'engine.mjs')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    try:
        first=records[0];frame=transact(proc,{'op':'init','seed':first['seed'],'id':first['snapshot']['id']})
        assert frame['hash']==first['hash']
        for row in records:
            if row['kind']!='ACTION':continue
            visible=transact(proc,{'op':'observe'})
            assert row['observation']=={k:visible[k] for k in row['observation']}
            decision=row['decision'];legal=visible['legal']
            if decision['kind']=='MODEL_CHOICE':assert row['action']==legal[decision['call']['choice']]
            elif decision['kind']=='FORCED_SINGLE_LEGAL_ACTION':assert legal==[row['action']]
            frame=transact(proc,{'op':'step','action':row['action']})
            assert frame['hash']==row['hash'] and frame['snapshot']==row['snapshot']
        last=transact(proc,{'op':'verify'})
        assert last['final_hash']==records[-1]['final_hash']
        return {'replay':'PASS','private_projections':'PASS','all_frame_hashes':'PASS',
                'actions':last['actions'],'final_hash':last['final_hash']}
    finally:
        proc.terminate();proc.wait();proc.stdin.close();proc.stdout.close()

def score_team(bids,wins,team,score,old_bags):
    seats=[team,team+2];positive=[i for i in seats if bids[i]>0]
    contract=sum(bids[i] for i in positive);tricks=sum(wins[i] for i in positive)
    made=tricks>=contract;nil=sum(100 if wins[i]==0 else -100 for i in seats if bids[i]==0)
    bags=sum(wins[i] for i in seats)-contract if made else sum(wins[i] for i in seats if bids[i]==0)
    penalty=((old_bags+bags)//10)*100
    return {'contract':contract,'contract_tricks':tricks,'made':made,'nil_points':nil,
            'bags_earned':bags,'bag_penalty':-penalty,'bags':(old_bags+bags)%10,
            'score':score+(10*contract if made else -10*contract)+nil+bags-penalty}

def hands(records):
    bids=[None]*4;wins=[0]*4;scores=[0,0];bags=[0,0];completed=[];trick=[]
    for row in records:
        if row['kind']!='ACTION':continue
        seat=int(row['player'][1:])-1;a=row['action']
        if a['type']=='BID':bids[seat]=a['bid']
        if a['type']=='PLAY':trick.append((seat,a['card']))
        for event in row['newLog']:
            if event['type']=='TRICK':
                led=trick[0][1][1]
                winner=max(trick,key=lambda p:(2 if p[1][1]=='S' else 1 if p[1][1]==led else 0,'23456789TJQKA'.index(p[1][0])))[0]
                assert event['payload']['winnerId']=='p'+str(winner+1)
                wins[winner]+=1;trick=[]
            if event['type']=='HAND':
                assert sum(wins)==13 and len(trick)==0
                teams=[score_team(bids,wins,t,scores[t],bags[t]) for t in [0,1]]
                scores=[t['score'] for t in teams];bags=[t['bags'] for t in teams]
                assert scores==event['payload']['scores'] and bags==event['payload']['bags']
                completed.append({'hand':event['payload']['handNumber'],'bids':bids,'tricks':wins,
                                  'nil_results':[None if bids[i] else 'made' if wins[i]==0 else 'failed' for i in range(4)],'teams':teams})
                bids=[None]*4;wins=[0]*4
    return completed

def call_metrics(calls):
    result=[]
    for model in dict.fromkeys(c['model'] for c in calls):
        group=[c for c in calls if c['model']==model];lat=[c['latency_ms'] for c in group]
        result.append({'model':model,'attempts':len(group),'accepted':sum(c['status']=='PASS' for c in group),
                       'holds':sum(c['status']!='PASS' for c in group),'http_429':sum(c['http_status']==429 for c in group),
                       'latency_median_ms':statistics.median(lat),'latency_max_ms':max(lat),
                       'cooldown_seconds':round(sum(c['cooldown_seconds'] for c in group),3),
                       'input_tokens':sum(c.get('input_tokens',0) for c in group),
                       'output_tokens':sum(c.get('output_tokens_including_reasoning',0) for c in group),
                       'known_estimated_cost_usd':str(sum((Decimal(c.get('estimated_cost_usd','0')) for c in group),Decimal(0))),
                       'unknown_usage_reserve_usd':str(sum((Decimal(c['reserved_usd']) for c in group if 'estimated_cost_usd' not in c),Decimal(0)))})
    return result

def main(folder):
    calls=rows(folder/'prior_calls.jsonl')+rows(folder/'calls.jsonl');report={'games':[],'model_metrics':call_metrics(calls)}
    for cohort in ['frontier','mainstream']:
        records=rows(folder/(cohort+'.jsonl'))
        if not records:continue
        verification=verify_game(records);scored=hands(records)
        report['games'].append({'cohort':cohort,'status':records[-1]['status'],'verification':verification,
          'completed_hands':scored,'decision_counts':dict(Counter(r['decision']['kind'] for r in records if r['kind']=='ACTION'))})
    (folder/'analysis.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main(Path(sys.argv[1]))
