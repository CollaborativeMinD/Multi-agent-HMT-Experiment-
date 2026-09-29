import contextlib,io,json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import campaign as c
import recover_flash as recovery

class RecoveryTests(unittest.TestCase):
 def checkpoint(self,target):
  fixture=json.loads((Path(__file__).parent/'recovery_fixture.json').read_text())
  for name,text in fixture['files'].items():
   path=target/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
 def test_one_request_success_then_duplicate_block(self):
  with tempfile.TemporaryDirectory() as d:
   target=Path(d)/'evidence';self.checkpoint(target)
   with patch.object(c,'OUT',target),patch.object(recovery,'sleep') as wait,patch.object(c.r,'call',return_value=(0,{'status':'PASS','choice':0,'output_cap':8192})) as call:
    self.assertEqual(recovery.recovery(),0);self.assertEqual(call.call_count,1);self.assertEqual(call.call_args.args[2],2);wait.assert_called_once_with(60)
    state=c.read(target/'series.json');self.assertEqual(state['games'][1]['actions'],3);self.assertEqual(state['status'],'IN_PROGRESS')
    with self.assertRaisesRegex(ValueError,'RECOVERY_NOT_ADMITTED'):recovery.recovery()
 def test_repeated_failure_preserves_action_and_hold(self):
  with tempfile.TemporaryDirectory() as d:
   target=Path(d)/'evidence';self.checkpoint(target)
   with patch.object(c,'OUT',target),patch.object(recovery,'sleep'),patch.object(c.r,'call',return_value=(None,{'http_status':429})) as call:
    self.assertEqual(recovery.recovery(),2);self.assertEqual(call.call_count,1)
    state=c.read(target/'series.json');self.assertEqual(state['games'][1]['actions'],2);self.assertEqual(state['status'],'HOLD')
    self.assertEqual(state['games'][1]['final_hash'],recovery.EXPECTED)

if __name__=='__main__':unittest.main()
