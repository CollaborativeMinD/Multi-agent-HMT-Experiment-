import ast,copy,unittest
from pathlib import Path
import probe as p
class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.req=p.request(p.MODELS[0],'canary',{'legal':[{},{}]})
        self.row={'case':'canary','input_reserve':1000,'input_price':'.0000004','output_price':'.0000042'}
        self.body={'model':p.MODELS[0],'provider':'Wafer','usage':{'prompt_tokens':12,'completion_tokens':9,'completion_tokens_details':{'reasoning_tokens':0}},'choices':[{'finish_reason':'stop','message':{'content':'{"choice":1}'}}]}
    def test_schema_and_usage(self):
        p.evaluate(self.body,self.req,self.row);self.assertEqual(self.row['status'],'PASS');self.assertEqual(self.row['visible_tokens'],9)
    def test_exact_boundary(self):
        self.body['usage']['completion_tokens']=1024;self.body['choices'][0]['finish_reason']='length'
        p.evaluate(self.body,self.req,self.row);self.assertEqual(self.row['status'],'TRUNCATED_AS_BOUNDED')
    def test_overrun(self):
        self.body['usage']['completion_tokens']=1025
        with self.assertRaisesRegex(ValueError,'OUTPUT_CAP_EXCEEDED'):p.evaluate(self.body,self.req,self.row)
    def test_route(self):
        self.body['provider']='Alibaba'
        with self.assertRaisesRegex(ValueError,'ROUTE_MISMATCH'):p.evaluate(self.body,self.req,self.row)
    def test_duplicate(self):
        self.body['choices'][0]['message']['content']='{"choice":1,"choice":1}'
        with self.assertRaisesRegex(ValueError,'DUPLICATE_KEY'):p.evaluate(self.body,self.req,self.row)
    def test_usage_missing(self):
        self.body['usage'].pop('completion_tokens')
        with self.assertRaisesRegex(ValueError,'USAGE_INVALID'):p.evaluate(self.body,self.req,self.row)
    def test_no_float_choice(self):
        self.body['choices'][0]['message']['content']='{"choice":1.0}'
        with self.assertRaisesRegex(ValueError,'SCHEMA_INVALID'):p.evaluate(self.body,self.req,self.row)
    def test_limits_and_size(self):
        for name,cap in [('canary',1024),('boundary',64),('game',8192)]:
            req=p.request(p.MODELS[0],name,{'legal':[{},{}]});self.assertEqual(req['max_tokens'],cap)
            self.assertFalse(req['provider']['allow_fallbacks'])
        for node in ast.walk(ast.parse(Path(p.__file__).read_text())):
            if isinstance(node,ast.FunctionDef):self.assertLessEqual(node.end_lineno-node.lineno+1,60)
if __name__=='__main__':unittest.main()
