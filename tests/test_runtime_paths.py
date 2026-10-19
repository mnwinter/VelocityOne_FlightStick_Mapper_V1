import tempfile,unittest,json
from pathlib import Path
from runtime_paths import select_data_root,prepare_user_data
from core import default_profile
from profile_library import save_preset,list_presets
class RuntimePathTests(unittest.TestCase):
 def test_frozen_uses_writable_user_data_not_resource_folder(self):
  self.assertEqual(select_data_root(True,Path('bundle'),Path('local')),Path('local')/'VelocityOneMapper')
  self.assertEqual(select_data_root(False,Path('source'),Path('local')),Path('source'))
  self.assertEqual(select_data_root(True,Path('bundle'),Path('local'),Path('test')),Path('test'))
 def test_migrates_legacy_without_overwriting_user_preset(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);legacy=root/'old';(legacy/'profiles').mkdir(parents=True)
   p=default_profile();p['combo']=8;(legacy/'profiles/old.json').write_text(json.dumps(p))
   data=root/'data';self.assertEqual(prepare_user_data(data,[legacy]),1)
   entries=list_presets(data/'profiles');self.assertEqual(entries[0][0]['combo'],8)
   saved,path=entries[0];saved['combo']=9;save_preset(data/'profiles',saved,replace_path=path)
   self.assertEqual(prepare_user_data(data,[legacy]),0)
   self.assertEqual(list_presets(data/'profiles')[0][0]['combo'],9)
   self.assertTrue((data/'logs').is_dir());self.assertTrue((legacy/'profiles/old.json').exists())
 def test_corrupt_legacy_profile_is_ignored(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);(root/'old/profiles').mkdir(parents=True);(root/'old/profiles/bad.json').write_text('{')
   self.assertEqual(prepare_user_data(root/'data',[root/'old']),0)
