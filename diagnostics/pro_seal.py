"""Read-only generation reconciliation and final Pro RCA evidence seal."""
import json,os,sqlite3,hashlib
from pathlib import Path
import reconcile as r
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence/pro-final-tracer'

def main():
    if (OUT/'generation-metadata.json').exists():raise ValueError('ALREADY_SEALED')
    receipts=json.loads((OUT/'receipts.json').read_text());r.OUT=OUT
    rows=[r.fetch(x,os.environ['OPENROUTER_API_KEY']) for x in receipts]
    r.save('generation-metadata.json',rows)
    matched=all(x['status']=='PASS' and x['comparison']['native_completion_matches_receipt'] and x['comparison']['native_reasoning_matches_receipt'] for x in rows)
    a,b,c=receipts
    checks={'native_metadata_matches':matched,'cap_slope_matches_prediction':a['total_output_tokens']==24576+128,
      'paired_messages':a['upstream'][0]['messages_sha256']==b['upstream'][0]['messages_sha256'],
      'paired_schema':a['upstream'][0]['response_format_sha256']==b['upstream'][0]['response_format_sha256'],
      'disabled_cases_pass':all(x['admission_status']=='PASS' and x['reasoning_tokens']==0 for x in (b,c)),
      'game_unchanged':json.loads((OUT/'summary.json').read_text())['game_evidence_unchanged']}
    r.save('review-verification.json',{'checks':checks,'new_inference_calls':0,'run_id':os.environ.get('GITHUB_RUN_ID')})
    db=sqlite3.connect(OUT/'gates.sqlite')
    for name,ok in checks.items():
        db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',
          (r.datetime.now(r.timezone.utc).isoformat(),'Final Pro review','PRO-REVIEW-'+name,name,'PASS' if ok else 'HOLD','review-verification.json',str(ok)))
    db.execute('INSERT INTO reverse_rca_ledger VALUES (?,?,?,?,?,?,?)',
      (r.datetime.now(r.timezone.utc).isoformat(),'PRO-ADDITIVE-24576','Cap slope and thinking toggle','128 requested; 24704 reported; disabled cases 7 and 6',
       'Echo preserves cap; thinking toggle removes observed excess; provider attribution unresolved','Paired boundary hashes and native generation receipts',
       'Thinking-on HOLD; thinking-off candidate only; no seat substitution'))
    db.commit();(OUT/'gates.sql').write_text('\n'.join(db.iterdump())+'\n');db.close()
    files=sorted(x for x in OUT.iterdir() if x.is_file() and x.name!='SHA256SUMS.txt')
    (OUT/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(x.read_bytes()).hexdigest()+'  '+x.name+'\n' for x in files))
    if not all(checks.values()):raise ValueError('REVIEW_HOLD')

if __name__=='__main__':main()
