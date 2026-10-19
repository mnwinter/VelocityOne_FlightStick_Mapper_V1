import unittest
import json
from core import default_profile, validate_profile, evaluate, AXES

class AnalogAlternativesTests(unittest.TestCase):
    def test_button_override_returns_to_proportional_lever(self):
        for target in ('LT','RT'):
            p=default_profile();p['deadzone']=0
            p['outputs'][target]={'kind':'any','sources':[{'kind':'axis','index':0,'range':'full'},{'kind':'button','index':0}]}
            p=validate_profile(p);s={'axes':[-.4],'buttons':[False],'hats':[]}
            self.assertAlmostEqual(evaluate(p,s)[target],.3)
            s['buttons'][0]=True;self.assertEqual(evaluate(p,s)[target],1)
            s['buttons'][0]=False;self.assertAlmostEqual(evaluate(p,s)[target],.3)
            self.assertEqual(evaluate(p,None)[target],0)

    def test_stick_uses_strongest_signed_input_and_stable_tie(self):
        p=default_profile();p['deadzone']=0
        p['outputs']['LX']={'kind':'any','sources':[{'kind':'axis','index':0},{'kind':'axis','index':1}]}
        p=validate_profile(p)
        for axes,wanted in [([-.8,.4],-.8),([-.2,.7],.7),([-.6,.6],-.6),([0,0],0)]:
            self.assertEqual(evaluate(p,dict(axes=axes,buttons=[],hats=[]))['LX'],wanted)

    def test_trigger_negative_source_cannot_mask_positive_source(self):
        p=default_profile();p['deadzone']=0
        p['outputs']['RT']={'kind':'any','sources':[{'kind':'axis','index':0},{'kind':'axis','index':1}]}
        self.assertEqual(evaluate(validate_profile(p),dict(axes=[-.9,.2],buttons=[],hats=[]))['RT'],.2)

    def test_all_axis_targets_accept_alternative_inputs(self):
        for target in AXES:
            p=default_profile();p['outputs'][target]={'kind':'any','sources':[{'kind':'button','index':0},{'kind':'button','index':1}]}
            p=validate_profile(p)
            self.assertEqual(evaluate(p,dict(axes=[],buttons=[False,True],hats=[]))[target],1)

    def test_analog_list_survives_profile_round_trip(self):
        p=default_profile()
        p['outputs']['LT']={'kind':'any','sources':[{'kind':'axis','index':7,'range':'full'},{'kind':'button','index':9}]}
        loaded=validate_profile(json.loads(json.dumps(p)))
        self.assertEqual(loaded['outputs']['LT'],p['outputs']['LT'])
