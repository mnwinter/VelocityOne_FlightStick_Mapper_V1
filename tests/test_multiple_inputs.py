import unittest
from core import default_profile,validate_profile,evaluate,BUTTONS
class MultipleInputTests(unittest.TestCase):
 def test_shared_and_independent_stick_clicks(self):
  p=default_profile();p['outputs'].update(L3={'kind':'any','sources':[{'kind':'button','index':3},{'kind':'button','index':4}]},R3={'kind':'any','sources':[{'kind':'button','index':3},{'kind':'button','index':5}]})
  p=validate_profile(p);s=dict(axes=[0,0],buttons=[False]*24,hats=[])
  for pressed,wanted in [([3],BUTTONS['L3']|BUTTONS['R3']),([4],BUTTONS['L3']),([5],BUTTONS['R3']),([3,4],BUTTONS['L3']|BUTTONS['R3']),([4,5],BUTTONS['L3']|BUTTONS['R3']),([],0)]:
   s['buttons']=[i in pressed for i in range(24)];self.assertEqual(evaluate(p,s)['buttons'],wanted)
  self.assertEqual(evaluate(p,None)['buttons'],0)
 def test_invalid_alternatives(self):
  for target,src in [('LX',{'kind':'any','sources':[{'kind':'button','index':1}]}),('L3',{'kind':'any','sources':[]}),('L3',{'kind':'any','sources':[{'kind':'any','sources':[]}]}),('L3',{'kind':'any','sources':[{'kind':'button','index':999}]})]:
   p=default_profile();p['outputs'][target]=src
   with self.assertRaises(ValueError):validate_profile(p)
 def test_existing_single_source_still_supported(self):
  p=default_profile();p['outputs']['L3']={'kind':'button','index':2};self.assertEqual(validate_profile(p)['outputs']['L3'],p['outputs']['L3'])
