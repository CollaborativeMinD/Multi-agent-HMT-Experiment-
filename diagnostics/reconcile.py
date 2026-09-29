"""Read-only reconciliation of existing generation IDs; zero inference requests."""
from __future__ import annotations
import hashlib,json,os,sqlite3,urllib.request,urllib.parse,urllib.error
from pathlib import Path
from typing import Any
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/router-rca'
FIELDS=('id','model','provider_name','request_id','upstream_id','created_at','finish_reason','native_finish_reason',
 'tokens_prompt','tokens_completion','native_tokens_prompt','native_tokens_completion','native_tokens_reasoning',
 'native_tokens_cached','total_cost','upstream_inference_cost','usage','latency','generation_time','cancelled','streamed')

def clean(data:dict[str,Any])->dict[str,Any]:
    return {k:v for k,v in data.items() if k in FIELDS and (v is None or type(v) in (str,int,float,bool))}

def save(name:str,data:Any)->None:
    OUT.mkdir(parents=True,exist_ok=True);(OUT/name).write_text(json.dumps(data,indent=2)+'\n')

def fetch(receipt:dict[str,Any],key:str)->dict[str,Any]:
    gid=receipt['generation_id'];url='https://openrouter.ai/api/v1/generation?'+urllib.parse.urlencode({'id':gid})
    row={'receipt_id':receipt['id'],'generation_id':gid,'model':receipt['model'],'requested_cap':receipt['output_cap'],
      'reported_output':receipt.get('total_output_tokens'),'reported_reasoning':receipt.get('reasoning_tokens'),
      'receipt_cost':receipt.get('provider_reported_cost_usd'),'reasoning_config':receipt['reasoning']}
    try:
        req=urllib.request.Request(url,headers={'Authorization':'Bearer '+key})
        with urllib.request.urlopen(req,timeout=25) as res:data=json.load(res)['data'];row['http_status']=res.status
        row['metadata']=clean(data);row['returned_field_names']=sorted(data)
        row['status']='PASS' if data.get('id')==gid else 'IDENTITY_MISMATCH'
        row['comparison']={
          'native_completion_matches_receipt':data.get('native_tokens_completion')==receipt.get('total_output_tokens'),
          'native_reasoning_matches_receipt':data.get('native_tokens_reasoning')==receipt.get('reasoning_tokens'),
          'normalized_completion_matches_receipt':data.get('tokens_completion')==receipt.get('total_output_tokens')}
    except urllib.error.HTTPError as exc:row.update(status='HOLD',http_status=exc.code)
    except Exception as exc:row.update(status='HOLD',reason=type(exc).__name__)
    return row

def main()->None:
    if OUT.exists() or os.environ.get('GITHUB_RUN_ATTEMPT','1')!='1':raise ValueError('RERUN_BLOCKED')
    key=os.environ['OPENROUTER_API_KEY'];rows=[]
    for folder in ['deepseek-diagnostic','flash-low-tracer']:
        receipts=json.loads((ROOT/'evidence'/folder/'receipts.json').read_text())
        for r in receipts:
            rows.append(fetch(r,key));save('generation-metadata.json',rows)
    now=datetime.now(timezone.utc).isoformat()
    save('summary.json',{'utc':now,'run_id':os.environ.get('GITHUB_RUN_ID'),'records':len(rows),
      'matched_records':sum(x['status']=='PASS' for x in rows),'new_inference_calls':0,'game_actions':0})
    db=sqlite3.connect(OUT/'gates.sqlite');db.executescript((ROOT/'evidence/flash-low-tracer/gates.sql').read_text())
    for row in rows:
        db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',
          (now,'Router RCA','METADATA-'+row['receipt_id'],'Reconcile existing generation ID',row['status'],
           'generation-metadata.json',hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest()))
    db.commit();(OUT/'gates.sql').write_text('\n'.join(db.iterdump())+'\n');db.close()

if __name__=='__main__':main()
