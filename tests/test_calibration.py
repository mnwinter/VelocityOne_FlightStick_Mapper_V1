import unittest
from calibration import CalibrationSession, apply_calibration, clear_unverified_levers
from core import default_profile,evaluate

def state(axes=None):return dict(axes=axes or [0.]*8,buttons=[False]*24,hats=[(0,0)])

class CalibrationTests(unittest.TestCase):
    def test_measures_controls_instead_of_assuming_axis_order(self):
        c=CalibrationSession()
        # Deliberately non-sequential hardware ordering. Right hat is axes 4/5;
        # the actual lever axes are 7/8. Nothing infers one from the other.
        for step,index,change in [(0,0,.8),(1,1,-.8),(2,5,.8),(3,6,-.8),(4,7,.8),(5,3,.8),(6,4,-.8)]:
            c.begin(step,state());s=state();s['axes'][index]=change
            self.assertTrue(c.observe(s))
        p=apply_calibration(default_profile(),c.sources,True)
        self.assertEqual(p['physical']['lever_left']['index'],6)
        self.assertEqual(p['physical']['lever_right']['index'],7)
        self.assertEqual(p['physical']['H2_x']['index'],3)
        self.assertEqual(p['physical']['H2_y']['index'],4)
        base=state();base['axes'][6]=1;base['axes'][7]=-1
        a=evaluate(p,base);base['axes'][3]=.9;base['axes'][4]=-.9;b=evaluate(p,base)
        self.assertEqual((a['LT'],a['RT']),(b['LT'],b['RT']))
        self.assertGreater(b['RX'],0);self.assertGreater(b['RY'],0)
    def test_duplicate_axis_rejected(self):
        c=CalibrationSession();c.begin(0,state());s=state();s['axes'][0]=.8;c.observe(s)
        c.begin(1,state());self.assertFalse(c.observe(s));self.assertIn('already',c.message)
    def test_incomplete_cannot_apply(self):
        with self.assertRaises(ValueError):apply_calibration(default_profile(),{},True)
    def test_no_output_rewrite_when_not_selected(self):
        c={key:dict(kind='axis',index=i,invert=False,range='full' if 'lever' in key else 'signed') for i,key in enumerate(CalibrationSession.keys)}
        p=default_profile();old=p['outputs'].copy();q=apply_calibration(p,c,False)
        self.assertEqual(q['outputs'],old)
    def test_legacy_cleanup_preserves_custom_and_combo(self):
        p=default_profile();p['physical']['lever_left']=dict(kind='axis',index=3,invert=False,range='full')
        p['physical']['lever_right']=dict(kind='axis',index=4,invert=False,range='full')
        p['outputs']['LT']=p['physical']['lever_left'].copy()
        p['outputs']['RT']=dict(kind='button',index=12)
        p['combo']=14
        q,changed=clear_unverified_levers(p)
        self.assertTrue(changed);self.assertNotIn('lever_left',q['physical']);self.assertNotIn('LT',q['outputs'])
        self.assertEqual(q['outputs']['RT'],dict(kind='button',index=12));self.assertEqual(q['combo'],14)

if __name__=='__main__':unittest.main()
