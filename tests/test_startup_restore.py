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
