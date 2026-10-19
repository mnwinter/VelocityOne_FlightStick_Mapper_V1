import unittest
from desktop_output import DesktopOutput
from core import default_profile

class DesktopTests(unittest.TestCase):
    def make(self):
        d=DesktopOutput.__new__(DesktopOutput);d.keys=set();d.buttons=set();d.fraction=[0.,0.];d.events=[]
        d.key=lambda key,down:d.events.append(('key',key,down))
        d.mouse=lambda key,down:d.events.append(('mouse',key,down))
        d.send=lambda i:None
        return d
    def test_hold_release_and_disconnect(self):
        d=self.make();p=default_profile();p['keys']=[{'source':{'kind':'button','index':0},'vk':65}]
        s={'axes':[],'hats':[],'buttons':[True]}
        d.update(p,s,.01);d.update(p,s,.01)
        self.assertEqual(d.events,[('key',65,True)])
        d.update(p,None,.01);self.assertEqual(d.events[-1],('key',65,False));self.assertFalse(d.keys)
    def test_partial_failure_retains_ownership(self):
        d=self.make();p=default_profile();p['keys']=[{'source':{'kind':'button','index':0},'vk':k} for k in (65,66)]
        def send(k,down):
            if k==66 and down:raise OSError('blocked')
            d.events.append(('key',k,down))
        d.key=send
        with self.assertRaises(OSError):d.update(p,{'axes':[],'hats':[],'buttons':[True]},.01)
        self.assertIn(65,d.keys);d.release();self.assertIn(('key',65,False),d.events)
    def test_mouse_release(self):
        d=self.make();p=default_profile();p['mouse']=[{'source':{'kind':'button','index':0},'action':'left'}]
        d.update(p,{'axes':[],'hats':[],'buttons':[True]},.01);d.release()
        self.assertEqual(d.events,[('mouse','left',True),('mouse','left',False)])
    def test_failed_release_retries(self):
        d=self.make();d.keys={65};d.buttons={'left'}
        def fail(*_):raise OSError('temporarily blocked')
        d.key=fail;d.mouse=fail;d.release()
        self.assertEqual(d.keys,{65});self.assertEqual(d.buttons,{'left'})
        d.key=lambda *args:None;d.mouse=lambda *args:None;d.release()
        self.assertFalse(d.keys);self.assertFalse(d.buttons)
    def test_chord_modifier_order(self):
        d=self.make();p=default_profile();p['keys']=[{'source':{'kind':'button','index':0},'vk':k} for k in (65,17)]
        d.update(p,{'axes':[],'hats':[],'buttons':[True]},.01);d.update(p,None,.01)
        self.assertEqual(d.events,[('key',17,True),('key',65,True),('key',65,False),('key',17,False)])

if __name__=='__main__':unittest.main()
