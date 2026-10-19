import unittest
from macros import MacroRunner,validate_macros

def macro(**kw):
 m=dict(name='Test',source=dict(kind='button',index=0),trigger='press',repeat='once',count=2,gap_ms=50,steps=[dict(outputs=['key:65','pad:LT','pad:RT'],duration_ms=100,delay_ms=50),dict(outputs=['key:66'],duration_ms=80,delay_ms=0)])
 m.update(kw);return m

def state(down):return dict(buttons=[down],axes=[],hats=[])
class MacroTests(unittest.TestCase):
 def test_sequence_simultaneous_and_delay(self):
  r=MacroRunner();m=[macro()];r.update(m,state(False),0)
  self.assertEqual(r.update(m,state(True),.01),{'key:65','pad:LT','pad:RT'})
  self.assertEqual(r.update(m,state(True),.111),set())
  self.assertEqual(r.update(m,state(True),.162),{'key:66'})
  self.assertEqual(r.update(m,state(True),.243),set())
  self.assertEqual(r.update(m,state(True),1),set())
 def test_stalled_tick_never_skips_short_next_step(self):
  r=MacroRunner();m=[macro(steps=[dict(outputs=['key:65'],duration_ms=100,delay_ms=0),dict(outputs=['key:66'],duration_ms=40,delay_ms=0)])]
  r.update(m,state(False),0);r.update(m,state(True),.01)
  self.assertFalse(r.update(m,state(True),.111))
  self.assertEqual(r.update(m,state(True),.160),{'key:66'})
  self.assertEqual(r.update(m,state(True),.180),{'key:66'})
 def test_count_and_gap(self):
  r=MacroRunner();m=[macro(repeat='count',steps=[dict(outputs=['key:65'],duration_ms=50,delay_ms=0)])]
  r.update(m,state(False),0);self.assertTrue(r.update(m,state(True),.01))
  self.assertFalse(r.update(m,state(True),.061));self.assertTrue(r.update(m,state(True),.112))
  self.assertFalse(r.update(m,state(True),.163));self.assertFalse(r.update(m,state(True),1))
 def test_while_held_cancels_and_reset_disarms(self):
  r=MacroRunner();m=[macro(repeat='held')];r.update(m,state(False),0)
  self.assertTrue(r.update(m,state(True),.01));self.assertFalse(r.update(m,state(False),.02))
  r.reset();self.assertFalse(r.update(m,state(True),.03))
 def test_toggle_and_release_trigger(self):
  r=MacroRunner();m=[macro(repeat='toggle',trigger='release')]
  r.update(m,state(False),0);r.update(m,state(True),.01)
  self.assertTrue(r.update(m,state(False),.02));r.update(m,state(True),.03)
  self.assertFalse(r.update(m,state(False),.04))
 def test_concurrent_macros_union_and_configuration_reset(self):
  r=MacroRunner();m=[macro(),macro(name='Second')];r.update(m,state(False),0)
  self.assertEqual(r.update(m,state(True),.01),{'key:65','pad:LT','pad:RT'})
  m[0]['name']='Edited';self.assertFalse(r.update(m,state(True),.02))
 def test_disconnect_and_validation(self):
  r=MacroRunner();m=[macro()];r.update(m,state(False),0);r.update(m,state(True),.01)
  self.assertFalse(r.update(m,None,.02))
  for change in [dict(trigger='bad'),dict(repeat='bad'),dict(count=0),dict(steps=[]),dict(steps=[dict(outputs=['pad:INVALID'],duration_ms=100,delay_ms=0)]),dict(steps=[dict(outputs=['key:65'],duration_ms=0,delay_ms=0)])]:
   with self.assertRaises(ValueError):validate_macros([macro(**change)])
 def test_same_key_between_steps_has_release_boundary(self):
  r=MacroRunner();m=[macro(steps=[dict(outputs=['key:65'],duration_ms=50,delay_ms=0),dict(outputs=['key:65'],duration_ms=50,delay_ms=0)])]
  r.update(m,state(False),0);self.assertTrue(r.update(m,state(True),.01))
  self.assertFalse(r.update(m,state(True),.061));self.assertTrue(r.update(m,state(True),.07))
 def test_gamepad_macro_preserves_ordinary_mapping(self):
  from macros import merge_gamepad
  from core import BUTTONS
  out=dict(buttons=BUTTONS['A'],LT=.3,RT=.4)
  self.assertEqual(merge_gamepad(out,{'pad:B','pad:LT','pad:RT','key:65'}),dict(buttons=BUTTONS['A']|BUTTONS['B'],LT=1.,RT=1.))
 def test_profile_roundtrip_and_legacy_default(self):
  import json
  from core import default_profile,validate_profile
  p=default_profile();p.pop('macros');self.assertEqual(validate_profile(p)['macros'],[])
  p['macros']=[macro()];self.assertEqual(validate_profile(json.loads(json.dumps(p)))['macros'],p['macros'])
 def test_shared_key_is_released_only_after_all_owners_finish(self):
  from test_desktop import DesktopTests
  from core import default_profile
  d=DesktopTests().make();p=default_profile();p['keys']=[dict(source=dict(kind='button',index=0),vk=65)]
  d.update(p,state(True),.01,{'key:65','mouse:left'})
  d.update(p,state(False),.01,{'key:65'})
  self.assertIn(65,d.keys);self.assertNotIn(('key',65,False),d.events)
  d.update(p,state(False),.01,set());self.assertEqual(d.events.count(('key',65,False)),1)
  self.assertIn(('mouse','left',False),d.events)
if __name__=='__main__':unittest.main()
