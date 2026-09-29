import ast,json,unittest
from pathlib import Path
from unittest.mock import patch
import nil100 as t
class NilTests(unittest.TestCase):
    def test_only_nil_clause_changes(self):
        old=t.r.RULES
        with patch.object(t.r,'RULES',old):
            delta=t.clarify_rules()
            self.assertEqual(delta['new'].replace(t.NEW_NIL,t.OLD_NIL),old)
            self.assertIn('takes zero tricks',delta['new']);self.assertIn('takes one or more tricks',delta['new'])
            self.assertNotEqual(delta['old_sha256'],delta['new_sha256'])
    def test_all_players_receive_definition(self):
        with patch.object(t.r,'RULES',t.r.RULES),patch.object(t.r,'compact',lambda v:v):
            t.clarify_rules();view={'legal':[{'type':'BID','bid':0},{'type':'BID','bid':2}]}
            for account,model in [('openai','gpt-6-astra'),('anthropic','claude-fable-5-1'),('gemini','gemini-3.8-flash')]:
                _,body=t.r.request({'account':account,'model':model},view)
                self.assertIn(t.NEW_NIL,json.dumps(body))
            for model in t.p.MODELS:
                body=t.p.request(model,'game',view)
                self.assertIn(t.NEW_NIL,body['messages'][0]['content'])
    def test_source_drift_holds(self):
        with patch.object(t.r,'RULES','changed prompt'):
            with self.assertRaisesRegex(ValueError,'PROMPT_SOURCE_DRIFT'):t.clarify_rules()
    def test_size(self):
        for n in ast.walk(ast.parse(Path(t.__file__).read_text())):
            if isinstance(n,ast.FunctionDef):self.assertLessEqual(n.end_lineno-n.lineno+1,60)
