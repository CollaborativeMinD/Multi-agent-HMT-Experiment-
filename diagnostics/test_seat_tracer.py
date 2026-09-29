import ast,copy,json,unittest
from pathlib import Path
from unittest.mock import patch
import seat_tracer as t
class SeatTracerTests(unittest.TestCase):
    def setUp(self):
        self.spec=t.fixtures()[1];self.profile=t.PROFILES[0]
        self.req=t.request(self.profile,self.spec)
        self.row=t.receipt(self.req,self.profile,self.spec,{'pricing':{'prompt':'.000003','completion':'.000015'}},1)
        self.state={'model':self.profile['model'],'provider':'Moonshot AI','usage':{'prompt_tokens':100,'completion_tokens':20,'completion_tokens_details':{'reasoning_tokens':10}},'content':'{"choice":0}','finish_reason':'stop'}
    def test_exact_v3_prompt_and_repeat(self):
        prompt=json.loads((t.p.ROOT/'evidence/strategy-v3-pro/prompt-delta.json').read_text())['new']
        self.assertTrue(self.req['messages'][0]['content'].startswith(prompt+'\n'))
        self.assertEqual(self.req,t.request(self.profile,t.fixtures()[2]))
    def test_nil_good_and_bad_separate_from_interface(self):
        t.evaluate(self.state,self.req,self.row,self.spec)
        self.assertEqual(self.row['nil_preservation'],'PASS')
        self.state['content']='{"choice":1}'
        t.evaluate(self.state,self.req,self.row,self.spec)
        self.assertEqual(self.row['status'],'PASS');self.assertEqual(self.row['nil_preservation'],'FAIL')
    def test_route_mismatch(self):
        self.state['provider']='Wafer'
        with self.assertRaisesRegex(ValueError,'ROUTE_MISMATCH'):t.evaluate(self.state,self.req,self.row,self.spec)
    def test_cap_and_usage(self):
        self.state['usage']['completion_tokens']=8193
        with self.assertRaisesRegex(ValueError,'TOKEN_BOUND_EXCEEDED'):t.evaluate(self.state,self.req,self.row,self.spec)
        self.state['usage']['completion_tokens']=5
        with self.assertRaisesRegex(ValueError,'USAGE_PARTITION_INVALID'):t.evaluate(self.state,self.req,self.row,self.spec)
    def test_malformed_choice(self):
        for text in ['{"choice":true}','{"choice":3}','{"choice":0,"extra":1}']:
            self.state['content']=text
            with self.assertRaises(ValueError):t.evaluate(self.state,self.req,self.row,self.spec)
    def test_expected_pressure_not_game_truncation(self):
        self.state['finish_reason']='length'
        with self.assertRaisesRegex(ValueError,'UNEXPECTED_FINISH'):t.evaluate(self.state,self.req,self.row,self.spec)
        t.evaluate(self.state,self.req,self.row,{'kind':'pressure'})
        self.assertEqual(self.row['result'],'EXPECTED_BOUNDED_TRUNCATION')
    def test_timeout_no_retry_retains_reserve(self):
        reserve=self.row['accounted_usd']
        with patch.object(t.urllib.request,'urlopen',side_effect=TimeoutError) as fake:
            t.call(self.req,self.row,self.spec,'fake')
        self.assertEqual(fake.call_count,1);self.assertEqual(self.row['accounted_usd'],reserve)
        self.assertEqual(self.row['status'],'HOLD')
    def test_function_size(self):
        for n in ast.walk(ast.parse(Path(t.__file__).read_text())):
            if isinstance(n,ast.FunctionDef):self.assertLessEqual(n.end_lineno-n.lineno+1,60)
if __name__=='__main__':unittest.main()
