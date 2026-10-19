import copy,json,os,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock,patch
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtWidgets import QApplication,QWidget,QMessageBox,QLineEdit,QDoubleSpinBox
from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import QTimer,QCoreApplication,QEvent
from shiboken6 import isValid
import app
from core import default_profile,validate_profile
from game_presets import make_starter,upgrade_legacy_action_labels
from profile_library import save_preset,list_presets
from widgets import SourceDialog

class ProfileLifecycleTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
 def test_activation_preserves_high_deadzone_without_edit_signals(self):
  for value in (.9,.949,.95):
   p=default_profile();p['deadzone']=value;validate_profile(p)
   spin=QDoubleSpinBox();spin.setRange(0,.95)
   changed=MagicMock();spin.valueChanged.connect(changed)
   fake=SimpleNamespace(deadzone=spin,name=QLineEdit(),mode=MagicMock(),refresh=MagicMock(),reload_profiles=MagicMock(),profile_signature=MagicMock(return_value='baseline'),notice=MagicMock(),remember_profile=MagicMock())
   app.MainWindow.activate_profile(fake,p,'Loaded')
   self.assertEqual(fake.p['deadzone'],value);changed.assert_not_called()
   self.assertFalse(spin.signalsBlocked())
   self.assertEqual(fake._baseline,'baseline')
 def test_deadzone_editor_maximum_is_valid(self):
  p=default_profile();p['deadzone']=.95
  self.assertEqual(validate_profile(p)['deadzone'],.95)
 def test_close_dirty_cancel_and_failed_save_preserve_window(self):
  for answer,saved in ((QMessageBox.StandardButton.Cancel,True),(QMessageBox.StandardButton.Save,False)):
   fake=SimpleNamespace(closing=False,has_pending_changes=lambda:True,save_profile=MagicMock(return_value=saved),timer=MagicMock(),engine=MagicMock(),device=MagicMock())
   event=QCloseEvent()
   with patch.object(app.QMessageBox,'question',return_value=answer):app.MainWindow.closeEvent(fake,event)
   self.assertFalse(event.isAccepted());self.assertFalse(fake.closing);fake.engine.close.assert_not_called()
 def test_close_discard_and_clean_shutdown_without_saving(self):
  for dirty in (False,True):
   fake=SimpleNamespace(closing=False,has_pending_changes=lambda:dirty,save_profile=MagicMock(),timer=MagicMock(),engine=MagicMock(),device=MagicMock())
   event=QCloseEvent()
   with patch.object(app.QMessageBox,'question',return_value=QMessageBox.StandardButton.Discard) as prompt:app.MainWindow.closeEvent(fake,event)
   self.assertTrue(event.isAccepted());fake.engine.close.assert_called_once();fake.save_profile.assert_not_called();self.assertEqual(prompt.call_count,int(dirty))
 def test_action_editor_property_change_is_in_save_signature(self):
  editor=QLineEdit();editor.setText('Fire secondary')
  p=default_profile();fake=SimpleNamespace(p=p,target_labels={'B':editor},name=QLineEdit('Pilot'),mode=SimpleNamespace(currentText=lambda:'Xbox gamepad'))
  fake.sync_action_labels=lambda:app.MainWindow.sync_action_labels(fake)
  self.assertEqual(json.loads(app.MainWindow.profile_signature(fake))['target_roles']['B'],'Fire secondary')
 def test_save_reads_action_editor_without_text_edited_signal(self):
  with tempfile.TemporaryDirectory() as td:
   editor=QLineEdit();editor.setText('Fire secondary')
   fake=SimpleNamespace(p=default_profile(),target_labels={'B':editor},name=QLineEdit('Pilot'),mode=SimpleNamespace(currentText=lambda:'Xbox gamepad'),current_path=None,remember_profile=MagicMock(),notice=MagicMock())
   fake.sync_action_labels=lambda:app.MainWindow.sync_action_labels(fake)
   fake.profile_signature=lambda:app.MainWindow.profile_signature(fake)
   with patch.object(app,'ROOT',Path(td)):
    self.assertTrue(app.MainWindow._save_profile(fake,update_browser=False))
   self.assertEqual(json.loads(fake.current_path.read_text())['target_roles']['B'],'Fire secondary')
 def test_rename_removes_only_previous_managed_profile(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);p=default_profile();old=save_preset(root,p);p['name']='Renamed';new=save_preset(root,p,replace_path=old)
   self.assertTrue(new.exists());self.assertFalse(old.exists());self.assertEqual(len(list_presets(root)),1)
 def test_import_source_outside_library_is_never_removed(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/'external.json';p=default_profile();source.write_text(json.dumps(p));save_preset(root/'library',p,replace_path=source)
   self.assertTrue(source.exists())
 def test_ac8_confirmed_captions_and_exact_legacy_upgrade(self):
  game='Ace Combat 8: Wings of Theve';expected={'B':'Fire secondary','X':'Cycle weapons','Y':'Change target'}
  for preset in ('flight','look'):
   p=make_starter(game,preset)
   self.assertEqual({k:p['target_roles'][k] for k in expected},expected)
  p=default_profile();p.update(game=game,target_roles={'B':'Target select','X':'Secondary weapon','Y':'My custom label'})
  upgraded=upgrade_legacy_action_labels(p)
  self.assertEqual(upgraded['target_roles'],{'B':'Fire secondary','X':'Cycle weapons','Y':'My custom label'});self.assertEqual(p['outputs'],upgraded['outputs'])
 def test_finished_source_dialog_stops_timer_and_schedules_cleanup(self):
  parent=QWidget();dialog=SourceDialog('test',lambda:None,parent=parent)
  dialog.reject();self.assertFalse(dialog.timer.isActive())
  parent.deleteLater()
 def test_exec_preserves_result_then_deletes_ephemeral_dialog(self):
  parent=QWidget();dialog=SourceDialog('test',lambda:None,parent=parent)
  QTimer.singleShot(0,dialog.accept)
  self.assertTrue(dialog.exec());self.assertEqual(dialog.source()['index'],0)
  self.assertFalse(dialog.timer.isActive())
  QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
  self.assertFalse(isValid(dialog));parent.deleteLater()
 def test_failed_destination_write_preserves_old_preset(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);p=default_profile();old=save_preset(root,p);before=old.read_bytes();p['name']='Renamed'
   with patch('profile_library.os.fsync',side_effect=OSError('disk full')):
    with self.assertRaises(OSError):save_preset(root,p,replace_path=old)
   self.assertEqual(old.read_bytes(),before);self.assertEqual(len(list_presets(root)),1)
 def test_rename_collision_preserves_both_profiles(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);p=default_profile();old=save_preset(root,p);p['name']='Taken';other=save_preset(root,p);before=other.read_bytes()
   with self.assertRaises(ValueError):save_preset(root,p,replace_path=old)
   self.assertTrue(old.exists());self.assertEqual(other.read_bytes(),before)
 def test_close_save_success_saves_before_shutdown(self):
  calls=[]
  fake=SimpleNamespace(closing=False,has_pending_changes=lambda:True,save_profile=lambda:calls.append('save') or True,timer=MagicMock(),engine=SimpleNamespace(close=lambda:calls.append('close')),device=MagicMock())
  event=QCloseEvent()
  with patch.object(app.QMessageBox,'question',return_value=QMessageBox.StandardButton.Save):app.MainWindow.closeEvent(fake,event)
  self.assertTrue(event.isAccepted());self.assertEqual(calls,['save','close'])
