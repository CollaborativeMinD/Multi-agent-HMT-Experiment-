import unittest,ast
from pathlib import Path
import flash_low as f
class FlashLowTests(unittest.TestCase):
    def test_request_only_effort_changes(self):
        v={'legal':[{},{}]};a=f.p.request(f.MODEL,'game',v);b=f.request('game',v)
        self.assertEqual(b.pop('reasoning'),{'effort':'low'});a.pop('reasoning');self.assertEqual(a,b)
    def test_inconsistent_usage_holds(self):
        r={'case':'boundary','status':'TRUNCATED_AS_BOUNDED','total_output_tokens':64,'reasoning_tokens':66}
        f.review(r);self.assertEqual(r['admission_status'],'HOLD')
    def test_valid_game_passes(self):
        r={'case':'game','status':'PASS','total_output_tokens':100,'reasoning_tokens':94}
        f.review(r);self.assertEqual(r['admission_status'],'PASS')
    def test_game_truncation_holds(self):
        r={'case':'game','status':'TRUNCATED_AS_BOUNDED','total_output_tokens':8192,'reasoning_tokens':8192}
        f.review(r);self.assertEqual(r['admission_status'],'HOLD')
    def test_unknown_usage_holds(self):
        r={'case':'game','status':'PASS','total_output_tokens':100}
        f.review(r);self.assertEqual(r['admission_status'],'HOLD')
    def test_function_size(self):
        for n in ast.walk(ast.parse(Path(f.__file__).read_text())):
            if isinstance(n,ast.FunctionDef):self.assertLessEqual(n.end_lineno-n.lineno+1,60)
if __name__=='__main__':unittest.main()
