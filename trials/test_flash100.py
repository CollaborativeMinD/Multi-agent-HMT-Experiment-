import ast,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from decimal import Decimal as D
import flash100 as t
class TrialTests(unittest.TestCase):
    def test_hundred_point_hand_replay(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(t.h,'OUT',Path(folder)),patch.object(t.r,'select',lambda m,v:(v['legal'][0],{'kind':'MODEL_CHOICE','call':{'choice':0}})):
            game={'id':'offline','cohort':'frontier','seed':707,'status':'IN_PROGRESS'}
            models=[{'model':'offline-'+str(i)} for i in range(4)]
            result=t.h.play_hand(game,models,{'max_hands_per_game':6})
            records=t.h.rows(Path(folder)/'offline/frontier.jsonl')
            self.assertEqual(records[0]['target'],100);self.assertEqual(result['hands'],1)
            self.assertEqual(t.analyze.verify_game(records)['actions'],56)
            self.assertEqual(len(t.analyze.hands(records)),1)
    def test_pro_disabled_request_and_admission(self):
        v={'legal':[{'type':'PLAY','card':'2H'},{'type':'PLAY','card':'AS'}],'handNumber':1,'turn':1,'you':'p4'}
        m={'account':'openrouter','model':t.p.MODELS[1],'native_prices':{'prompt':'.0000004','completion':'.0000042'}}
        def fake(req,row,key):
            self.assertEqual(req['model'],t.p.MODELS[1]);self.assertEqual(req['reasoning'],{'enabled':False});self.assertIn('game to 100.',req['messages'][0]['content'])
            row.update(admission_status='PASS',reasoning_tokens=0,upstream=[{'thinking':{'type':'disabled'},'max_tokens':8192}],choice=1,total_output_tokens=7,accounted_usd='.001')
        with patch.object(t.r,'compact',lambda x:x),patch.object(t.p,'save'),patch.object(t.r,'emit'),patch.object(t.w,'call',fake),patch.dict(t.os.environ,{'OPENROUTER_API_KEY':'fake'}),patch.object(t.r,'spent',{'openrouter':D(0)}),patch.object(t.r,'last_finished',{}):
            self.assertEqual(t.select(m,v)[0],v['legal'][1])
    def test_sizes(self):
        for mod in (t,t.h):
            for n in ast.walk(ast.parse(Path(mod.__file__).read_text())):
                if isinstance(n,ast.FunctionDef):self.assertLessEqual(n.end_lineno-n.lineno+1,60)

