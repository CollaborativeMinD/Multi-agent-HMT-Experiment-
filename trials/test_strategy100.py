import ast,json,unittest
from pathlib import Path
from unittest.mock import patch
import strategy100 as t
class StrategyTests(unittest.TestCase):
    def test_only_strategy_paragraph_changes(self):
        old=t.r.RULES
        with patch.object(t.r,'RULES',old):
            delta=t.clarify_rules()
            self.assertEqual(delta['old'],old.replace(t.OLD_NIL,t.NEW_NIL))
            self.assertEqual(delta['new'],delta['old']+'\n\n'+t.STRATEGY)
            self.assertNotEqual(delta['old_sha256'],delta['new_sha256'])
    def test_all_players_receive_definition(self):
        with patch.object(t.r,'RULES',t.r.RULES),patch.object(t.r,'compact',lambda v:v):
            t.clarify_rules();view={'legal':[{'type':'BID','bid':0},{'type':'BID','bid':2}]}
            for account,model in [('openai','gpt-6-astra'),('anthropic','claude-fable-5-1'),('gemini','gemini-3.8-flash')]:
                _,body=t.r.request({'account':account,'model':model},view)
                self.assertIn(t.NEW_NIL,json.dumps(body))
                self.assertIn(t.STRATEGY,json.dumps(body,ensure_ascii=False))
            for model in t.p.MODELS:
                body=t.p.request(model,'game',view)
                self.assertIn(t.NEW_NIL,body['messages'][0]['content'])
                self.assertIn(t.STRATEGY,body['messages'][0]['content'])
    def test_source_drift_holds(self):
        with patch.object(t.r,'RULES','changed prompt'):
            with self.assertRaisesRegex(ValueError,'PROMPT_SOURCE_DRIFT'):t.clarify_rules()
    def test_approved_paragraph(self):
        self.assertEqual(t.STRATEGY,Path(t.__file__).with_name('strategy-v3-prompt.txt').read_text().strip())
    def test_account_guard_selected_before_dispatch(self):
        with patch.object(t,'ORIGINAL_SELECT',return_value=('action',{})) as dispatch:
            with patch.object(t,'LIMITS',{'anthropic':t.D('19.98')}),patch.object(t.r,'LIMIT',t.D('9.98')):
                t.select({'account':'anthropic'},{'legal':[1,2]})
                self.assertEqual(t.r.LIMIT,t.D('19.98'))
                dispatch.assert_called_once()
    def test_size(self):
        for n in ast.walk(ast.parse(Path(t.__file__).read_text())):
            if isinstance(n,ast.FunctionDef):self.assertLessEqual(n.end_lineno-n.lineno+1,60)
