"""One isolated limit-semantics tracer. Does not apply a game action."""
import json,os
from pathlib import Path
from decimal import Decimal
import runner as r


def main():
    if os.environ.get('GITHUB_RUN_ATTEMPT','1')!='1':raise ValueError('RERUN_BLOCKED')
    manifest=json.loads(r.MODEL_FILE.read_text())
    m=next(m for m in manifest['models'] if m['model']=='qwen/qwen3.8-2.4t-a95b')
    v=json.loads((r.ROOT/'qwen_limit_view.json').read_text())
    original=r.request
    def diagnostic_request(model,view):
        url,body=original(model,view)
        del body['max_tokens'];body['max_completion_tokens']=1024
        return url,body
    r.request=diagnostic_request
    # Reserve the endpoint's advertised maximum, not the unverified request limit.
    r.smoke.CAP=131072
    r.spent['openrouter']=Decimal('0.244724')
    choice,row=r.call(m,v,1)
    row.update(requested_max_completion_tokens=1024,diagnostic_only=True,action_applied=False)
    tokens=row.get('output_tokens_including_reasoning')
    row['limit_observation']='WITHIN_REQUEST_PLUS_10' if isinstance(tokens,int) and tokens<=1034 else 'NOT_VERIFIED'
    print('LIMIT_TRACER='+json.dumps(row),flush=True)
    (r.OUT/'limit_tracer.json').write_text(json.dumps(row,indent=2))

if __name__=='__main__':main()
