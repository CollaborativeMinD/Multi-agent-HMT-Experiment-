import io,json,unittest,ast
from pathlib import Path
import wire_probe as w
class WireTests(unittest.TestCase):
    def test_debug_allowlist(self):
        x=w.controls({'max_tokens':64,'thinking':{'budget_tokens':24576,'secret':'x'},'authorization':'secret','messages':[{'content':'private'}]})
        self.assertEqual(x['max_tokens'],64);self.assertNotIn('authorization',x);self.assertNotIn('secret',x['thinking']);self.assertNotIn('messages',x)
    def test_stream_usage_and_finish(self):
        chunks=[{'debug':{'echo_upstream_body':{'max_tokens':64}},'choices':[]},
          {'choices':[{'delta':{'content':'{"choice":1}'},'finish_reason':'stop'}]},
          {'usage':{'completion_tokens':6},'choices':[]}]
        data=''.join('data: '+json.dumps(c)+'\n\n' for c in chunks)+'data: [DONE]\n\n'
        s={'upstream':[],'content':''};w.events(io.BytesIO(data.encode()),s)
        self.assertTrue(s['done']);self.assertEqual(s['content'],'{"choice":1}');self.assertEqual(s['usage']['completion_tokens'],6)
    def test_missing_done_holds(self):
        with self.assertRaisesRegex(ValueError,'STREAM_INCOMPLETE'):w.events(io.BytesIO(b''),{'upstream':[],'content':''})
    def test_stream_error_holds(self):
        with self.assertRaisesRegex(ValueError,'STREAM_ERROR'):w.consume({'error':{'message':'secret'}},{})
    def test_function_size(self):
        for n in ast.walk(ast.parse(Path(w.__file__).read_text())):
            if isinstance(n,ast.FunctionDef):self.assertLessEqual(n.end_lineno-n.lineno+1,60)
if __name__=='__main__':unittest.main()
