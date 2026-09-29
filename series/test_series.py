import ast,contextlib,io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import campaign as c
import report as p

class SeriesTests(unittest.TestCase):
 def plan(self):return c.read(c.PLAN)
 def models(self):
  return [dict(account=x,model='TEST_POLICY_NOT_AI',standard_text_usd_per_million_tokens={'input':0,'output':0}) for x in ['openai','anthropic','gemini','openrouter']]
 def game(self):return dict(id='frontier-g01',cohort='frontier',number=1,seed=101,status='IN_PROGRESS',hands=0,actions=0,scores=[0,0])
 def policy(self,m,v):return v['legal'][-1],{'kind':'TEST_POLICY_NOT_AI'}
 def test_first_to_three_and_no_extra_game(self):
  for outcomes in [[0,0,0],[0,1,0,1,1]]:
   state={'games':[],'next_cohort':'frontier'}
   for i,win in enumerate(outcomes):
    g=c.next_game(state,self.plan());self.assertEqual(g['number'],i+1)
    g.update(status='COMPLETE',winners=['p1','p3'] if win==0 else ['p2','p4'])
   self.assertEqual(max(c.wins(state['games'],'frontier')),3)
   self.assertEqual(c.next_game(state,self.plan())['cohort'],'mainstream')
 def test_checkpoint_resume_and_300_score(self):
  with tempfile.TemporaryDirectory() as d,patch.object(c,'OUT',Path(d)),patch.object(c.r,'select',side_effect=self.policy):
   game=self.game();first=c.play_hand(game,self.models(),self.plan());self.assertEqual(first['actions'],56)
   game.update(first);second=c.play_hand(game,self.models(),self.plan());self.assertEqual(second['actions'],112)
   game.update(second)
   for _ in range(18):
    if game['status']=='COMPLETE':break
    game.update(c.play_hand(game,self.models(),self.plan()))
   self.assertEqual(game['status'],'COMPLETE');self.assertGreaterEqual(max(game['scores']),300)
   rec=c.rows(Path(d)/game['id']/'frontier.jsonl');self.assertEqual(sum(x['kind']=='INITIAL' for x in rec),1)
   self.assertEqual(sum(x['kind']=='FINAL' for x in rec),1)
   verify=p.analyze.verify_game(rec);self.assertEqual(verify['actions'],game['actions'])
   self.assertEqual([x['score'] for x in p.analyze.hands(rec)[-1]['teams']],game['scores'])
 def test_first_failure_retains_evidence(self):
  with tempfile.TemporaryDirectory() as d,patch.object(c,'OUT',Path(d)),patch.object(c.r,'select',side_effect=ValueError('MODEL_HOLD:test')) as select:
   result=c.play_hand(self.game(),self.models(),self.plan())
   self.assertEqual(result['status'],'HOLD');self.assertEqual(select.call_count,1)
   self.assertTrue(result['replay_verified']);self.assertEqual(result['actions'],0)
 def test_unknown_reservation_and_opening_carry(self):
  with tempfile.TemporaryDirectory() as d,patch.object(c,'OUT',Path(d)):
   folder=Path(d)/'frontier-g01';folder.mkdir()
   (folder/'calls.jsonl').write_text(json.dumps({'provider':'openrouter','reserved_usd':'0.10'})+'\n')
   self.assertEqual(c.accounting(self.plan())['openrouter'],c.Decimal('0.51923340'))
 def test_corrupted_resume_rejected(self):
  with tempfile.TemporaryDirectory() as d,patch.object(c,'OUT',Path(d)),patch.object(c.r,'select',side_effect=self.policy):
   g=self.game();c.play_hand(g,self.models(),self.plan());path=Path(d)/g['id']/'frontier.jsonl'
   rec=c.rows(path);rec[1]['hash']='bad';path.write_text('\n'.join(json.dumps(x) for x in rec)+'\n')
   with self.assertRaisesRegex(ValueError,'RESUME_STATE_MISMATCH'):c.play_hand(g,self.models(),self.plan())
 def test_roster_budget_and_strict_profile(self):
  with tempfile.TemporaryDirectory() as d,patch.object(c,'OUT',Path(d)):
   models=c.configure(self.plan());self.assertEqual(len(models),8);self.assertEqual(c.r.LIMIT,c.Decimal('9.98'))
   self.assertIn('game to 300.',c.r.RULES);self.assertNotIn('game to 100.',c.r.RULES)
   self.assertFalse(self.plan()['free_play_authorized']);self.assertEqual(c.r.REQUEST_DEADLINE,240);self.assertEqual(c.r.smoke.CAP,8192)
 def test_readme_projection_and_synthetic_report(self):
  with tempfile.TemporaryDirectory() as d,patch.object(c,'OUT',Path(d)/'evidence'),patch.object(c.r,'select',side_effect=self.policy):
   game=c.play_hand(self.game(),self.models(),self.plan());report=p.verify_and_render(game)
   self.assertEqual(report['verification']['replay'],'PASS')
   state={'status':'IN_PROGRESS','updated_utc':'test','series_wins':{'frontier':[0,0],'mainstream':[0,0]},'games':[game],'accounting_usd':self.plan()['opening_accounting_usd']}
   text=p.render_section(state);self.assertIn('Free Play is **not authorized**',text);self.assertIn('frontier-g01',text)
   self.assertIn('WHIZ / 300',(c.OUT/game['id']/'replay.html').read_text())
 def test_full_publisher_preserves_readme_and_ledger(self):
  import shutil,sqlite3
  with tempfile.TemporaryDirectory() as d,patch.object(c,'OUT',Path(d)/'evidence'),patch.object(c.r,'select',side_effect=self.policy):
   root=Path(d)/'series';root.mkdir();shutil.copyfile(c.ROOT/'opening-gates.sql',root/'opening-gates.sql')
   readme=Path(d)/'README.md';readme.write_text('KEEP\n'+p.BEGIN+'\nold\n'+p.END+'\nKEEP_END')
   game=c.play_hand(self.game(),self.models(),self.plan())
   state={'status':'IN_PROGRESS','updated_utc':'test','series_wins':{'frontier':[0,0],'mainstream':[0,0]},'games':[game],'accounting_usd':self.plan()['opening_accounting_usd']}
   c.atomic(c.OUT/'series.json',state)
   with patch.object(c,'ROOT',root),contextlib.redirect_stdout(io.StringIO()):self.assertEqual(p.main(),0)
   self.assertTrue(readme.read_text().startswith('KEEP'));self.assertTrue(readme.read_text().endswith('KEEP_END'))
   db=sqlite3.connect(c.OUT/'gate_ledger.sqlite');self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok');db.close()
 def test_function_size(self):
  for source in [Path(c.__file__),Path(p.__file__)]:
   for n in ast.walk(ast.parse(source.read_text())):
    if isinstance(n,ast.FunctionDef):self.assertLessEqual(n.end_lineno-n.lineno+1,60,n.name)

if __name__=='__main__':unittest.main()
