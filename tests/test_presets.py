import tempfile,unittest
from pathlib import Path
from game_presets import GAMES,starter_ids,make_starter
from profile_library import list_presets,save_preset
from core import default_profile,validate_profile
class PresetTests(unittest.TestCase):
 def test_all_starters_validate_and_are_independent(self):
  self.assertGreaterEqual(len(GAMES),15)
  for game in GAMES:
   for preset_id in starter_ids(game):
    p=make_starter(game,preset_id);validate_profile(p)
    self.assertEqual(p['game'],game);self.assertEqual(p['preset_status'],'starter-unverified')
    self.assertGreater(len(p['outputs']),12)
    p['outputs'].clear();self.assertTrue(make_starter(game,preset_id)['outputs'])
 def test_ac8_twist_drives_opposite_bumpers_and_h2_is_look(self):
  from core import evaluate,BUTTONS
  for preset_id in ('flight','look'):
   p=make_starter('Ace Combat 8: Wings of Theve',preset_id)
   self.assertEqual(p['outputs']['RX']['index'],3)
   self.assertEqual(p['target_roles']['RX'],'Camera X')
   for twist,target in ((-.9,'LB'),(.9,'RB'),(0,None)):
    state=dict(axes=[0,0,twist,0,0,-1,0,-1],buttons=[False]*24,hats=[(0,0)])
    out=evaluate(p,state)
    self.assertEqual(out['buttons']&(BUTTONS['LB']|BUTTONS['RB']),BUTTONS[target] if target else 0)
    self.assertEqual(out['RX'],0)
 def test_current_graphics_calibration_preserved(self):
  old=default_profile();old['physical']['H2_x']=dict(kind='axis',index=3,invert=True,range='signed')
  p=make_starter('Elite Dangerous','flight',old)
  self.assertTrue(p['physical']['H2_x']['invert']);self.assertNotIn('macros',GAMES['Elite Dangerous'])
  self.assertEqual(old['outputs'],default_profile()['outputs'])
 def test_same_user_name_in_two_games_cannot_overwrite(self):
  with tempfile.TemporaryDirectory() as td:
   a=make_starter('Elite Dangerous','flight');b=make_starter('Star Citizen','flight')
   a['name']=b['name']='Combat';pa=save_preset(Path(td),a);pb=save_preset(Path(td),b)
   self.assertNotEqual(pa,pb);self.assertEqual(list_presets(Path(td),'Elite Dangerous')[0][0]['name'],'Combat')
   self.assertEqual(len(list_presets(Path(td))),2)
 def test_legacy_profiles_and_bad_files(self):
  import json
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);p=default_profile();(root/'old.json').write_text(json.dumps(p))
   (root/'broken.json').write_text('{');items=list_presets(root,'Custom / Other')
   self.assertEqual(len(items),1);self.assertEqual(items[0][0]['name'],p['name'])
 def test_untrusted_names_stay_inside_root(self):
  with tempfile.TemporaryDirectory() as td:
   p=default_profile();p['game']='../../outside';p['name']='CON / ../ test'
   path=save_preset(Path(td),p);self.assertTrue(path.resolve().is_relative_to(Path(td).resolve()))
 def test_presets_do_not_auto_add_macros_or_clear_user_files(self):
  with tempfile.TemporaryDirectory() as td:
   p=make_starter('Star Citizen','flight');self.assertEqual(p['macros'],[])
   path=save_preset(Path(td),p);q=dict(p,name='Landing');save_preset(Path(td),q)
   self.assertTrue(path.exists());self.assertEqual(len(list_presets(Path(td))),2)

 def test_rename_collision_never_overwrites_another_preset(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);a=make_starter('Elite Dangerous','flight');a['name']='A'
   b=make_starter('Elite Dangerous','look');b['name']='B'
   pa=save_preset(root,a);pb=save_preset(root,b);before=pb.read_bytes()
   a['name']='B'
   with self.assertRaises(ValueError):save_preset(root,a,replace_path=pa)
   self.assertEqual(pb.read_bytes(),before)
 def test_builtin_cannot_replace_saved_customized_starter(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);p=make_starter('Star Citizen','flight');p['combo']=8
   path=save_preset(root,p);before=path.read_bytes()
   fresh=make_starter('Star Citizen','flight')
   with self.assertRaises(ValueError):save_preset(root,fresh)
   self.assertEqual(path.read_bytes(),before)
   p['combo']=9;save_preset(root,p,replace_path=path)
   self.assertNotEqual(path.read_bytes(),before)
