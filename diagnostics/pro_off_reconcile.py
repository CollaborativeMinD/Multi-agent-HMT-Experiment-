"""One reviewed delayed metadata lookup, zero new inference."""
import json,os,sqlite3
from pathlib import Path
import reconcile as r
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/pro-off-eval'

def main()->None:
    if (OUT/'delayed-metadata.json').exists():raise ValueError('RERUN_BLOCKED')
    old=json.loads((OUT/'generation-metadata.json').read_text())
    receipts=json.loads((OUT/'receipts.json').read_text());by_id={x['id']:x for x in receipts}
    revised=[x if x['status']=='PASS' else r.fetch(by_id[x['receipt_id']],os.environ['OPENROUTER_API_KEY']) for x in old]
    r.OUT=OUT;r.save('delayed-metadata.json',revised)
    matched=all(x['status']=='PASS' and x['comparison']['native_completion_matches_receipt'] and x['comparison']['native_reasoning_matches_receipt'] for x in revised)
    summary=json.loads((OUT/'summary.json').read_text())
    ok=matched and summary['passed']==12 and summary['game_evidence_unchanged']
    r.save('qualification.json',{'status':'PASS' if ok else 'HOLD','scope':'Twelve bounded interface checks, not strategic quality or frontier seat admission',
      'metadata_matches':matched,'inference_checks_passed':summary['passed'],'new_inference_calls':0,'original_summary_preserved':True,'run_id':os.environ.get('GITHUB_RUN_ID')})
    db=sqlite3.connect(OUT/'gates.sqlite');now=r.datetime.now(r.timezone.utc).isoformat()
    db.execute('INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)',
      (now,'Pro off qualification','PRO-OFF-METADATA-DELAYED','Native usage receipt reconciliation','PASS' if matched else 'HOLD','delayed-metadata.json',str(matched)))
    db.execute('INSERT INTO reverse_rca_ledger VALUES (?,?,?,?,?,?,?)',
      (now,'PRO-OFF-METADATA-404','Generation metadata lookup','Three newest generation IDs initially returned HTTP 404',
       'Original receipts preserved; one delayed read-only lookup','Compare native completion and reasoning counts',
       ('INVESTIGATION_COMPLETE; SOLUTION_CANDIDATE_APPLIED; delayed records available, internal delay cause unproven' if matched else 'INVESTIGATION_INCOMPLETE; REQUIRES_OPERATOR_ESCALATION; metadata unavailable')))
    db.commit();(OUT/'gates.sql').write_text('\n'.join(db.iterdump())+'\n');db.close()
    (OUT/'SHA256SUMS.txt').write_text(''.join(r.hashlib.sha256(x.read_bytes()).hexdigest()+'  '+x.name+'\n' for x in sorted(OUT.iterdir()) if x.is_file() and x.name!='SHA256SUMS.txt'))
    if not ok:raise ValueError('QUALIFICATION_HOLD')

if __name__=='__main__':main()
