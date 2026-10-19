import unittest
from overlay_bindings import apply_reported_layout
from core import default_profile,source_value
class OverlayTests(unittest.TestCase):
 def test_reported_numbers(self):
  physical=apply_reported_layout(default_profile())['physical']
  expected={'lever_left':5,'lever_right':7,'H2_x':3,'H2_y':4,'wheel':14,'B16':15,'B17':16,'trigger':17,'front_20':19,'front_21':20,'front_22':21,'front_23':22}
  for key,index in expected.items():self.assertEqual(physical[key]['index'],index,key)
  self.assertEqual([physical[k]['index'] for k in ('left_A','left_B','left_X','left_Y','right_A','right_B','right_X','right_Y')],list(range(8)))
 def test_preserves_outputs_and_custom_calibration(self):
  p=default_profile();p['physical']['H2_x']=dict(kind='axis',index=3,invert=True,range='signed');p['combo']=14
  updated=apply_reported_layout(p)
  self.assertEqual(updated['outputs'],p['outputs']);self.assertEqual(updated['combo'],14)
  self.assertTrue(updated['physical']['H2_x']['invert']);self.assertNotIn('front_20',p['physical'])
 def test_button_isolation(self):
  physical=apply_reported_layout(default_profile())['physical']
  keys=['wheel','B16','B17','trigger','front_20','front_21','front_22','front_23','left_A','left_B','left_X','left_Y','right_A','right_B','right_X','right_Y']
  for key in keys:
   state=dict(axes=[0]*8,buttons=[False]*24,hats=[(0,0)]);state['buttons'][physical[key]['index']]=True
   self.assertEqual([k for k in keys if source_value(physical[k],state)>.5],[key])
 def test_h2_slider_isolation(self):
  physical=apply_reported_layout(default_profile())['physical'];state=dict(axes=[0,0,0,1,-1,-1,0,-1],buttons=[False]*24,hats=[])
  self.assertEqual(source_value(physical['H2_x'],state),1)
  self.assertEqual(source_value(physical['H2_y'],state),-1)
  self.assertEqual(source_value(physical['lever_left'],state),0)
  self.assertEqual(source_value(physical['lever_right'],state),0)

 def test_slider_end_buttons_are_independent_of_analog_axes(self):
  physical=apply_reported_layout(default_profile())['physical']
  for number in range(9,13):
   key=f'slider_end_{number}';self.assertEqual(physical[key],dict(kind='button',index=number-1))
   state=dict(axes=[1]*8,buttons=[False]*24,hats=[])
   self.assertEqual(source_value(physical[key],state),0)
   state['buttons'][number-1]=True;self.assertEqual(source_value(physical[key],state),1)
   for other in range(9,13):self.assertEqual(source_value(physical[f'slider_end_{other}'],state),float(other==number))
 def test_slider_ends_drive_output_combo_and_macros(self):
  from core import evaluate,BUTTONS
  from macros import MacroRunner
  p=apply_reported_layout(default_profile());p['outputs']['A']=p['physical']['slider_end_9'];p['combo']=9
  state=dict(axes=[0]*8,buttons=[False]*24,hats=[])
  state['buttons'][8]=True;self.assertTrue(evaluate(p,state)['buttons']&BUTTONS['A'])
  state['buttons'][9]=True;self.assertEqual(evaluate(p,state)['LT'],1);self.assertEqual(evaluate(p,state)['RT'],1)
  for number in (11,12):
   m=dict(name='Slider end',source=p['physical'][f'slider_end_{number}'],trigger='press',repeat='once',count=1,gap_ms=50,steps=[dict(outputs=['key:65'],duration_ms=100,delay_ms=0)])
   r=MacroRunner();r.update([m],state,0);state['buttons'][number-1]=True
   self.assertEqual(r.update([m],state,.01),{'key:65'})

 def test_exactly_four_front_markers_with_learned_names_and_legacy_aliases(self):
  from overlay_bindings import front_marker_slots
  physical=apply_reported_layout(default_profile())['physical']
  for key,index in [('system_xbox',19),('system_view',20),('system_capture',21),('system_menu',22)]:physical[key]=dict(kind='button',index=index)
  markers=front_marker_slots(physical)
  self.assertEqual(len(markers),4)
  self.assertEqual(set(markers.values()),{'system_xbox','system_view','system_menu','system_capture'})
 def test_four_front_markers_before_and_during_learning(self):
  from overlay_bindings import front_marker_slots
  physical=apply_reported_layout(default_profile())['physical']
  self.assertEqual(len(set(front_marker_slots(physical).values())),4)
  physical['system_view']=dict(kind='button',index=21)
  markers=front_marker_slots(physical)
  self.assertEqual(len(markers),4);self.assertIn('system_view',markers.values());self.assertNotIn('front_22',markers.values())
