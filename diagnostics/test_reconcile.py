import unittest
import reconcile as r
class ReconcileTests(unittest.TestCase):
    def test_allowlist(self):
        self.assertEqual(r.clean({'id':'gen-test','native_tokens_completion':64,'native_tokens_reasoning':69,
          'api_key':'SECRET','prompt':'PRIVATE','provider_responses':[{'secret':'x'}]}),
          {'id':'gen-test','native_tokens_completion':64,'native_tokens_reasoning':69})
    def test_nested_rejected(self):
        self.assertEqual(r.clean({'model':{'unexpected':'x'}}),{})
if __name__=='__main__':unittest.main()
