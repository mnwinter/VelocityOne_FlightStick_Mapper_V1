"""Identify physical controls by measured movement, independent of SDL axis order."""
import copy
import math

class CalibrationSession:
    keys=('roll','pitch','twist','lever_left','lever_right','H2_x','H2_y')
    def __init__(self):
        self.sources={};self.baseline=None;self.step=0;self.message=''
    def begin(self,step,state):
        if state is None:raise ValueError('Connect the original V1 in PC mode first.')
        self.step=step;self.baseline=list(state['axes']);self.message='Listening for one axis…'
        self.sources.pop(self.keys[step],None)
    def observe(self,state):
        if self.baseline is None or state is None:return False
        changes=[(abs(v-old),i,v-old) for i,(v,old) in enumerate(zip(state['axes'],self.baseline))
                 if math.isfinite(v) and math.isfinite(old)]
        changes.sort(reverse=True)
        if not changes or changes[0][0]<.45:return False
        if len(changes)>1 and changes[1][0]>.25:
            self.message='Several axes moved. Return to the start position, then Capture again.';return False
        _,i,delta=changes[0];key=self.keys[self.step]
        used=next((k for k,s in self.sources.items() if k!=key and s['index']==i),None)
        if used:
            self.message=f'Axis {i+1} is already assigned to {used}. Move only the requested control.';return False
        self.sources[key]=dict(kind='axis',index=i,invert=delta<0,
                               range='full' if key.startswith('lever') else 'signed')
        self.baseline=None;self.message=f'Captured Axis {i+1}'+(' · inverted' if delta<0 else '')
        return True

def apply_calibration(profile,sources,standard):
    if any(k not in sources for k in CalibrationSession.keys):raise ValueError('Identify all seven controls first.')
    if len({sources[k]['index'] for k in CalibrationSession.keys})!=7:raise ValueError('Controls must use separate axes.')
    p=copy.deepcopy(profile);p['physical'].update(copy.deepcopy(sources));p['calibration_version']=1
    if standard:
        for target,key in dict(LX='roll',LY='pitch',RT='lever_left',LT='lever_right',RX='H2_x',RY='H2_y').items():
            p['outputs'][target]=copy.deepcopy(sources[key])
    return p

def clear_unverified_levers(profile):
    """Remove only exact legacy starter bindings. Never guess their replacements."""
    p=copy.deepcopy(profile);changed=False
    if p.get('calibration_version')==1:return p,False
    for key,i in (('lever_left',3),('lever_right',4)):
        old=dict(kind='axis',index=i,invert=False,range='full')
        if p.get('physical',{}).get(key)==old:
            del p['physical'][key];changed=True
            for target in ('LT','RT'):
                if p['outputs'].get(target)==old:del p['outputs'][target]
    return p,changed
