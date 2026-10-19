import os,copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtWidgets import QApplication
from widgets import OutputInputsDialog,source_text
from core import default_profile,validate_profile
from profile_library import save_preset
class AlternativeEditorTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
 def test_edit_list_preserves_original_until_accepted(self):
  original={'kind':'any','sources':[{'kind':'button','index':3},{'kind':'button','index':4}]};before=copy.deepcopy(original)
  d=OutputInputsDialog('Map L3',lambda:None,original)
  self.assertEqual(d.inputs.count(),2);self.assertIn(' OR ',source_text(d.source()))
  d.inputs.setCurrentRow(1);d.remove_input();self.assertEqual(d.source(),before['sources'][0]);self.assertEqual(original,before)
  d.remove_input();self.assertIsNone(d.source());self.assertFalse(d.edit_button.isEnabled());d.close()
 def test_add_and_edit(self):
  d=OutputInputsDialog('Map R3',lambda:None,{'kind':'button','index':3})
  with patch('widgets.SourceDialog') as dialog:
   dialog.return_value.exec.return_value=1;dialog.return_value.source.return_value={'kind':'button','index':5};d.add_input()
  self.assertEqual(d.source()['sources'][1]['index'],5)
  d.inputs.setCurrentRow(1)
  with patch('widgets.SourceDialog') as dialog:
   dialog.return_value.exec.return_value=1;dialog.return_value.source.return_value={'kind':'button','index':6};d.edit_input()
  self.assertEqual(d.source()['sources'][1]['index'],6);d.close()
 def test_save_reload_alternatives(self):
  p=default_profile();p['outputs']['L3']={'kind':'any','sources':[{'kind':'button','index':3},{'kind':'button','index':4}]}
  with tempfile.TemporaryDirectory() as folder:
   path=save_preset(Path(folder),p);loaded=validate_profile(json.loads(path.read_text(encoding='utf-8')))
  self.assertEqual(loaded['outputs']['L3'],p['outputs']['L3'])
