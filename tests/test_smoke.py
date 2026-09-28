import ast
from pathlib import Path
import contextlib
import io
import json
import os
import unittest
import urllib.error
from unittest.mock import patch
import smoke

class SmokeTests(unittest.TestCase):
    def test_budget_and_roster(self):
        totals=smoke.preflight()
        self.assertEqual(set(totals), {'openai','anthropic','gemini','openrouter'})
        self.assertTrue(all(float(v)<.25 for v in totals.values()))
        self.assertEqual(len(smoke.SPECS), 8)

    def test_legal_and_schema(self):
        self.assertEqual(smoke.action_check('{"action":"play","card":"2H"}')['card'],'2H')
        for raw in ['{}','[]','null','{"action":"play","card":"AS"}',
                    '{"action":"play","card":"2H","extra":1}',
                    '{"action":"play","card":"2H","card":"AS"}',
                    '{"action":"play","card":true}','not json']:
            with self.subTest(raw=raw), self.assertRaises((ValueError, TypeError)):
                smoke.action_check(raw)

    def test_positive_adapters(self):
        text='{"action":"play","card":"2H"}'
        fixtures={
          'openai': {'model':'m','status':'completed','usage':{'input_tokens':40,'output_tokens':25},
            'output':[{'type':'message','content':[{'type':'output_text','text':text}]}]},
          'anthropic': {'model':'m','stop_reason':'end_turn','usage':{'input_tokens':40,'output_tokens':25},
            'content':[{'type':'text','text':text}]},
          'gemini': {'modelVersion':'m','usageMetadata':{'promptTokenCount':40,'candidatesTokenCount':10,'thoughtsTokenCount':15},
            'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':text}]}}]},
          'openrouter': {'model':'m','provider':'Alibaba','usage':{'prompt_tokens':40,'completion_tokens':25},
            'choices':[{'finish_reason':'stop','message':{'content':text}}]}}
        for p,b in fixtures.items():
            row={};smoke.validate_result(p,'m',b,row,('10','50'))
            self.assertEqual(row['status'],'PASS')
            self.assertEqual(row['output_tokens_including_reasoning'],25)
        fixtures['openrouter']['provider']='Other'
        with self.assertRaisesRegex(ValueError,'PROVIDER_ROUTE_MISMATCH'):
            smoke.validate_result('openrouter','m',fixtures['openrouter'],{},('10','50'))
        fixtures['openai']['model']='other'
        with self.assertRaisesRegex(ValueError,'MODEL_ID_MISMATCH'):
            smoke.validate_result('openai','m',fixtures['openai'],{},('10','50'))

    def test_http_timeout_no_retry_no_secret(self):
        for error in [TimeoutError(),urllib.error.HTTPError('url',429,'secret-TEST',{},None),
                      urllib.error.HTTPError('url',500,'secret-TEST',{},None)]:
            with patch.dict(os.environ,{'OPENAI_API_KEY':'secret-TEST'}), patch('smoke.urllib.request.build_opener') as op:
                op.return_value.open.side_effect=error
                row=smoke.probe(smoke.SPECS[0])
                self.assertEqual(op.return_value.open.call_count,1)
                self.assertEqual(row['status'],'HOLD')
                self.assertNotIn('secret-TEST',json.dumps(row))

    def test_missing_and_rerun_zero_calls(self):
        with patch.dict(os.environ,{},clear=True),patch('smoke.urllib.request.build_opener') as op:
            self.assertEqual(smoke.probe(smoke.SPECS[0])['reason'],'MISSING_SECRET')
            op.assert_not_called()
        with patch.dict(os.environ,{'GITHUB_RUN_ATTEMPT':'2'}),patch('smoke.probe') as call,contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(smoke.main(),1);call.assert_not_called()

    def test_function_bounds(self):
        tree=ast.parse(Path(smoke.__file__).read_text())
        for n in ast.walk(tree):
            if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
                self.assertLessEqual(n.end_lineno-n.lineno+1,60,n.name)

if __name__=='__main__':unittest.main()
