import unittest
from core import evaluate, packet, axis_value, validate_profile, default_profile

class MappingTests(unittest.TestCase):
    def test_combo_preserves_levers(self):
        p=default_profile(); p['combo']=14
        s={'axes':[0,0,0,-0.6,0.4], 'buttons':[False]*24,'hats':[(0,0)]}
        p['outputs']['LT']={'kind':'axis','index':3,'range':'full','invert':False}
        p['outputs']['RT']={'kind':'axis','index':4,'range':'full','invert':False}
        normal=evaluate(p,s); self.assertAlmostEqual(normal['LT'],.2); self.assertAlmostEqual(normal['RT'],.7)
        s['buttons'][14]=True
        self.assertEqual((evaluate(p,s)['LT'],evaluate(p,s)['RT']),(1,1))
        s['buttons'][14]=False
        self.assertEqual(evaluate(p,s),normal)
    def test_axis_and_deadzone(self):
        self.assertEqual(axis_value(.02,.05,False),0)
        self.assertEqual(axis_value(1,.05,True),-1)
        self.assertEqual(axis_value(-1,.05,False),-1)
    def test_neutral_disconnect(self):
        self.assertEqual(packet(evaluate(default_profile(),None)),bytes(20))
    def test_protocol(self):
        import struct
        r={'buttons':0x1000,'LT':1,'RT':0,'LX':-1,'LY':1,'RX':0,'RY':0}
        self.assertEqual(packet(r),struct.pack('<IBBhhhh6x',0x1000,255,0,-32768,32767,0,0))
    def test_validation(self):
        p=default_profile();p['outputs']['LX']['index']=-1
        with self.assertRaises(ValueError):validate_profile(p)
    def test_nonfinite(self):
        self.assertEqual(axis_value(float('nan'),.05,False),0)
    def test_default(self):validate_profile(default_profile())
    def test_invalid_key_label(self):
        p=default_profile();p['keys']=[dict(source=dict(kind='button',index=0),vk=65,label=None)]
        with self.assertRaises(ValueError):validate_profile(p)

if __name__=='__main__':unittest.main()
