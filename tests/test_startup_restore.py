import unittest,tempfile,json
from pathlib import Path
from unittest.mock import patch,MagicMock
from types import SimpleNamespace
import app
from core import default_profile
class StartupRestoreTests(unittest.TestCase):
 def test_restore_reads_saved_selection_without_saving_pending_profile(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);(root/'profiles').mkdir();p=root/'profiles'/'saved.json';p.write_text(json.dumps(default_profile()))
   (root/'state.json').write_text(json.dumps(dict(last_profile='saved.json')))
   fake=SimpleNamespace(load_path=MagicMock())
   with patch.object(app,'ROOT',root):app.MainWindow.restore_profile(fake)
   fake.load_path.assert_called_once_with(p.resolve(),save_pending=False)
 def test_corrupt_remembered_preset_falls_back_to_valid_preset(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);(root/'profiles').mkdir()
   bad=root/'profiles'/'bad.json';bad.write_text('{')
   good=root/'profiles'/'good.json';good.write_text(json.dumps(default_profile()))
   (root/'state.json').write_text(json.dumps(dict(last_profile='bad.json')))
   fake=SimpleNamespace(load_path=MagicMock(side_effect=[False,True]))
   with patch.object(app,'ROOT',root):app.MainWindow.restore_profile(fake)
   self.assertEqual(fake.load_path.call_count,2)
   fake.load_path.assert_any_call(bad.resolve(),save_pending=False)
   fake.load_path.assert_called_with(good.resolve(),save_pending=False)
