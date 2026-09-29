import ast,unittest
from pathlib import Path
import pro_off_eval as e
class OffTests(unittest.TestCase):
    def test_matrix(self):
        views=[{'view':{'legal':[0,1,2]},'hash':str(i)} for i in range(4)]
        specs=e.specs(views);self.assertEqual(len(specs),12)
        reqs=[e.request(x) for x in specs]
        self.assertEqual(reqs[4],reqs[5]);self.assertEqual(reqs[5],reqs[6])
        self.assertTrue(all(x['reasoning']=={'enabled':False} for x in reqs))
    def test_wrong_answer_holds(self):
        row={'upstream':[{'thinking':{'type':'disabled'},'max_tokens':32}],'reasoning_tokens':0,'usage_partition_status':'PASS','status':'PASS','choice':1}
        e.review(row,{'kind':'known','cap':32,'expected':2});self.assertEqual(row['admission_status'],'HOLD')
    def test_expected_truncation(self):
        row={'upstream':[{'thinking':{'type':'disabled'},'max_tokens':1}],'reasoning_tokens':0,'usage_partition_status':'PASS','status':'TRUNCATED_AS_BOUNDED'}
        e.review(row,{'kind':'pressure','cap':1});self.assertEqual(row['admission_status'],'PASS')
        row['reasoning_tokens']=1;e.review(row,{'kind':'pressure','cap':1});self.assertEqual(row['admission_status'],'HOLD')
    def test_size(self):
        for n in ast.walk(ast.parse(Path(e.__file__).read_text())):
            if isinstance(n,ast.FunctionDef):self.assertLessEqual(n.end_lineno-n.lineno+1,60)
