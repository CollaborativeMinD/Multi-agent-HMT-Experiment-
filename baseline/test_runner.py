import ast,contextlib,io,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import runner as r

class RunnerTests(unittest.TestCase):
 def model(self):return {'account':'openai','model':'gpt-6-astra','standard_text_usd_per_million_tokens':{'input':10,'output':50}}
 def body(self,choice=0):return {'model':'gpt-6-astra','status':'completed','usage':{'input_tokens':50,'output_tokens':25},'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps({'choice':choice})}]}]}
 def test_parse_identity_usage_action(self):
  row={'input_reserve':500};self.assertEqual(r.parse(self.body(),self.model(),2,row),0)
  self.assertEqual(row['status'],'PASS')
  for value in [True,-1,2,'0']:
   with self.subTest(value=value),self.assertRaises(ValueError):r.parse(self.body(value),self.model(),2,{'input_reserve':500})
  b=self.body();b['model']='wrong'
  with self.assertRaises(ValueError):r.parse(b,self.model(),2,{'input_reserve':500})
  b=self.body();b['usage']['input_tokens']=None
  with self.assertRaises(ValueError):r.parse(b,self.model(),2,{'input_reserve':500})
 def test_8192_all_models_and_boundary(self):
  manifest=json.loads(r.MODEL_FILE.read_text())
  v=json.loads((Path(r.__file__).parent/'qwen_limit_view.json').read_text())
  for m in manifest['models']:
   _,body=r.request(m,v)
   caps=[body.get('max_tokens'),body.get('max_output_tokens'),body.get('generationConfig',{}).get('maxOutputTokens')]
   self.assertEqual([x for x in caps if x is not None],[8192],m['model'])
  for tokens in [5515,8192]:
   body=self.body();body['usage']['output_tokens']=tokens
   self.assertEqual(r.parse(body,self.model(),2,{'input_reserve':500}),0)
  body=self.body();body['usage']['output_tokens']=8193
  with self.assertRaisesRegex(ValueError,'TOKEN_RESERVATION_EXCEEDED'):
   r.parse(body,self.model(),2,{'input_reserve':500})
 def test_private_boundary(self):
  with self.assertRaises(ValueError):r.compact({'deckSeed':7})
  with self.assertRaises(ValueError):r.compact({'you':'p1','players':[{'id':'p2','hand':['AS']}]})
 def test_budget_before_network(self):
  v={'legal':[{},{}]};r.spent['openai']=r.LIMIT
  with patch.object(r,'request',return_value=('https://api.openai.com/v1/responses',{})),patch.object(r,'headers') as h:
   with self.assertRaises(ValueError):r.call(self.model(),v,1)
   h.assert_not_called()
  r.spent['openai']=r.Decimal(0)
 def test_forced_and_stop_first_issue(self):
  with patch.object(r,'call') as c:
   self.assertEqual(r.select(self.model(),{'legal':[{'type':'PLAY','card':'AS'}]})[1]['kind'],'FORCED_SINGLE_LEGAL_ACTION');c.assert_not_called()
  with patch.object(r,'call',return_value=(None,{'http_status':429} )) as c,patch.object(r.time,'sleep') as wait:
   with self.assertRaises(ValueError):r.select(self.model(),{'legal':[{},{}]})
   self.assertEqual(c.call_count,1);wait.assert_not_called()
 def test_function_length(self):
  for n in ast.walk(ast.parse(Path(r.__file__).read_text())):
   if isinstance(n,ast.FunctionDef):self.assertLessEqual(n.end_lineno-n.lineno+1,60,n.name)
 def test_resume_real_prefix(self):
  import subprocess
  root=Path(r.__file__).parent
  with tempfile.TemporaryDirectory() as d,patch.object(r,'OUT',Path(d)):
   proc=subprocess.Popen(['node',str(root/'engine.mjs')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
   try:
    original=[json.loads(x) for x in (r.RESUME/'frontier.jsonl').read_text().splitlines()]
    frame=r.engine(proc,{'op':'init','seed':7,'id':'whiz100-frontier'})
    frame,count=r.restore(proc,'frontier',[{'model':m} for m in original[0]['models']],frame)
    self.assertEqual(count,92);self.assertEqual(frame['hash'],original[-1]['final_hash'])
    self.assertTrue(r.engine(proc,{'op':'verify'})['replay_verified'])
   finally:proc.terminate();proc.wait();proc.stdin.close();proc.stdout.close()
 def test_headless_evidence(self):
  models=[self.model()]*4
  with tempfile.TemporaryDirectory() as d,patch.object(r,'OUT',Path(d)),patch.object(r,'select',side_effect=lambda m,v:(v['legal'][-1],{'kind':'TEST_POLICY'})),contextlib.redirect_stdout(io.StringIO()):
   result=r.game('test',models)
   self.assertTrue(result['replay_verified'])
   frames=[json.loads(x) for x in (Path(d)/'test.jsonl').read_text().splitlines()]
   self.assertGreater(result['actions'],0)
   for frame in frames:
    if frame['kind']=='ACTION':
     v=frame['observation'];self.assertTrue(all(p['hand'] is None for p in v['players'] if p['id']!=v['you']))

if __name__=='__main__':unittest.main()
