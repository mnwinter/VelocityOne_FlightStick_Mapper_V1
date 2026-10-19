import unittest,copy,json,tempfile
from pathlib import Path
from types import SimpleNamespace
from app import MainWindow
from core import default_profile
from profile_library import save_preset
class ActionLabelTests(unittest.TestCase):
 def test_label_edit_persists_without_rebinding(self):
  p=default_profile();p['game']='Ace Combat 8: Wings of Theve';before=copy.deepcopy(p['outputs'])
  MainWindow.set_action_label(SimpleNamespace(p=p),'LB','Rudder left')
  self.assertEqual(p['outputs'],before)
  with tempfile.TemporaryDirectory() as td:
   path=save_preset(Path(td),p)
   self.assertEqual(json.loads(path.read_text(encoding='utf-8'))['target_roles']['LB'],'Rudder left')

 def test_legacy_caption_upgrade_preserves_bindings_and_custom_names(self):
  from game_presets import upgrade_legacy_action_labels
  p=default_profile();p['game']='Ace Combat 8: Wings of Theve'
  p['target_roles']={'RX':'Yaw / rudder','LB':'My custom yaw','RB':'Utility right'}
  result=upgrade_legacy_action_labels(p)
  self.assertEqual(result['target_roles']['RX'],'Camera X')
  self.assertEqual(result['target_roles']['LB'],'My custom yaw')
  self.assertEqual(result['target_roles']['RB'],'Rudder right')
  self.assertEqual(p['outputs'],result['outputs'])
