"""Rendered assignment state follows the same mapping evaluation as the preview."""
import unittest
from types import SimpleNamespace
from PySide6.QtWidgets import QApplication,QPushButton
from app import MainWindow
from core import default_profile,evaluate,BUTTONS

class AssignmentActivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def test_mapped_button_and_hat_release_disconnect_and_remap(self):
        ui=SimpleNamespace(rows={key:QPushButton() for key in BUTTONS})
        p=default_profile();p['outputs'].update(X=dict(kind='button',index=15),Up=dict(kind='hat',index=0,direction='up'),Right=dict(kind='hat',index=0,direction='right'))
        state=dict(axes=[0,0],buttons=[False]*24,hats=[(1,1)])
        state['buttons'][15]=True
        def update(s):MainWindow.update_assignment_activity(ui,evaluate(p,s))
        update(state)
        self.assertTrue(ui.rows['X'].property('liveActive'))
        self.assertTrue(ui.rows['Up'].property('liveActive'))
        self.assertTrue(ui.rows['Right'].property('liveActive'))
        self.assertFalse(ui.rows['A'].property('liveActive'))
        p['outputs'].pop('X');update(state)
        self.assertFalse(ui.rows['X'].property('liveActive'))
        state['hats']=[(0,0)];update(state)
        self.assertFalse(ui.rows['Up'].property('liveActive'))
        update(None)
        self.assertTrue(all(not b.property('liveActive') for b in ui.rows.values()))

    def test_axis_trigger_and_button_to_trigger_feedback_clears(self):
        from core import AXES
        ui=SimpleNamespace(rows={key:QPushButton('Axis 1') for key in AXES})
        p=default_profile();p['outputs']['LT']=dict(kind='button',index=9)
        p['outputs']['RT']=dict(kind='axis',index=5,range='full')
        state=dict(axes=[-.7,.4,0,0,0,1],buttons=[False]*24,hats=[])
        state['buttons'][9]=True
        MainWindow.update_assignment_activity(ui,evaluate(p,state))
        for key in ('LX','LY','LT','RT'):self.assertTrue(ui.rows[key].property('liveActive'))
        self.assertIn('100%',ui.rows['LT'].text())
        self.assertIn('-0.68',ui.rows['LX'].text())
        MainWindow.update_assignment_activity(ui,evaluate(p,None))
        self.assertTrue(all(not b.property('liveActive') for b in ui.rows.values()))
        self.assertIn('0%',ui.rows['LT'].text())
