import ast,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import kimi100 as t

class KimiTests(unittest.TestCase):
    def view(self):
        rows=t.h.rows(t.ROOT/'evidence/pro100/frontier-pro/frontier.jsonl')
        row=next(x for x in rows if x.get('player')=='p4' and x.get('action',{}).get('card')=='8D')
        return dict(row['observation'],turn=row['index'])

    def test_request_preserves_v3_private_view(self):
        prompt=json.loads((t.ROOT/'evidence/strategy-v3-pro/prompt-delta.json').read_text())['new']
        with patch.object(t.r,'RULES',prompt):req=t.make_request(self.view())
        self.assertEqual(req['reasoning'],{'effort':'low'})
        self.assertEqual(req['provider']['only'],['moonshotai/mxfp4'])
        self.assertFalse(req['provider']['allow_fallbacks'])
        self.assertEqual(req['max_tokens'],8192)

    def dispatch(self,status='PASS',reason=None):
        view=self.view();model={'account':'openrouter','native_prices':{'prompt':'0.000003','completion':'0.000015'}}
        def call(req,row,spec,key):
            row.update(status=status,choice=0,total_output_tokens=113,reasoning_tokens=93,accounted_usd='0.004',reason=reason)
        prompt=json.loads((t.ROOT/'evidence/strategy-v3-pro/prompt-delta.json').read_text())['new']
        with patch.object(t.r,'RULES',prompt),patch.object(t,'LIMITS',{'openrouter':t.D('9.98')}),patch.object(t.r,'spent',{'openrouter':t.D('1')}),patch.object(t.r,'last_finished',{}),patch.object(t.p,'save'),patch.object(t.r,'emit') as emit,patch.object(t.tracer,'call',side_effect=call) as calls,patch.dict(os.environ,{'OPENROUTER_API_KEY':'fixture'}):
            if status=='PASS':
                action,_=t.select(model,view);self.assertEqual(action,view['legal'][0]);self.assertEqual(t.r.spent['openrouter'],t.D('1.004'))
            else:
                with self.assertRaisesRegex(ValueError,'MODEL_HOLD'):t.select(model,view)
                self.assertGreater(t.r.spent['openrouter'],t.D('1.004'))
            calls.assert_called_once();self.assertEqual(emit.call_args.args[1]['status'],status)

    def test_admitted_action_and_accounting(self):self.dispatch()
    def test_uncertain_usage_retains_reserve_and_no_move(self):self.dispatch('HOLD','USAGE_PARTITION_INVALID')

    def test_budget_blocks_before_call(self):
        with patch.object(t,'LIMITS',{'openrouter':t.D('1')}),patch.object(t.r,'spent',{'openrouter':t.D('1')}),patch.object(t,'make_request',return_value={'max_tokens':8192,'reasoning':{'effort':'low'}}),patch.object(t.tracer,'call') as call:
            with self.assertRaisesRegex(ValueError,'BUDGET_OR_INPUT_HOLD'):
                t.select({'account':'openrouter','native_prices':{'prompt':'0.000003','completion':'0.000015'}},self.view())
            call.assert_not_called()

    def test_cumulative_tracer_spend(self):
        self.assertEqual(t.opening_accounting()['openrouter'],'1.1915020684')
        self.assertEqual(t.opening_accounting()['anthropic'],'11.142030')

    def test_size(self):
        for n in ast.walk(ast.parse(Path(t.__file__).read_text())):
            if isinstance(n,ast.FunctionDef):self.assertLessEqual(n.end_lineno-n.lineno+1,60)
