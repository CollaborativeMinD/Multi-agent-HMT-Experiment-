import unittest,ast
from pathlib import Path
from decimal import Decimal as D
import pro_final as q
class FinalTests(unittest.TestCase):
    def test_paired_controls(self):
        specs=list(q.specifications({'legal':[0,1,2]}))
        a,b=specs[0][1],specs[1][1]
        self.assertEqual(a['messages'],b['messages']);self.assertEqual(a['response_format'],b['response_format'])
        self.assertEqual(a['max_tokens'],128);self.assertEqual(b['max_tokens'],128)
        self.assertEqual(a['reasoning'],{'effort':'low'});self.assertEqual(b['reasoning'],{'enabled':False})
        self.assertEqual(specs[2][1]['max_tokens'],8192)
    def test_reservation_accounts_for_overrun(self):
        req=list(q.specifications({'legal':[0]}))[0][1]
        ni,no,cost=q.reserve(req,{'prompt':'0.000001','completion':'0.000004'})
        self.assertGreater(no,24704);self.assertEqual(cost,D(ni)*D('.000001')+D(no)*D('.000004'))
    def test_size(self):
        for n in ast.walk(ast.parse(Path(q.__file__).read_text())):
            if isinstance(n,ast.FunctionDef):self.assertLessEqual(n.end_lineno-n.lineno+1,60)
