"""Pure mapping: SDL sources -> normalized Xbox state. No hardware side effects."""
import math
import struct
import copy

BUTTONS={'A':0x1000,'B':0x2000,'X':0x4000,'Y':0x8000,'LB':0x100,'RB':0x200,
         'Menu':0x10,'View':0x20,'Guide':0x400,'L3':0x40,'R3':0x80,'Up':1,'Down':2,'Left':4,'Right':8}
AXES=('LX','LY','RX','RY','LT','RT')

def default_profile():
    axis=lambda i,inv=False,r='signed':dict(kind='axis',index=i,invert=inv,range=r)
    return dict(version=1,name='My flight profile',mode='Xbox gamepad',deadzone=.05,combo=None,
                outputs={'LX':axis(0),'LY':axis(1,True)},keys=[],mouse=[],macros=[],
                physical={'roll':axis(0),'pitch':axis(1)})

def axis_value(value,deadzone=0,invert=False):
    if not math.isfinite(value):return 0.
    v=max(-1.,min(1.,value))*(-1 if invert else 1)
    return 0. if abs(v)<=deadzone else math.copysign((abs(v)-deadzone)/(1-deadzone),v)

def source_value(src,state,deadzone=0):
    if not src or state is None:return 0.
    i=src['index'];kind=src['kind']
    try:
        if kind=='button':return float(bool(state['buttons'][i]))
        if kind=='hat':
            x,y=state['hats'][i];d=src.get('direction','up')
            return float({'up':y>0,'down':y<0,'left':x<0,'right':x>0}[d])
        v=state['axes'][i]
        if not math.isfinite(v):return 0.
        inv=src.get('invert',False);r=src.get('range','signed')
        if r=='full':return max(0.,min(1.,(1+(-v if inv else v))/2))
        if r=='positive':return max(0.,axis_value(v,deadzone,inv))
        if r=='negative':return max(0.,-axis_value(v,deadzone,inv))
        return axis_value(v,deadzone,inv)
    except (IndexError,KeyError,TypeError):return 0.

def evaluate(profile,state):
    out=dict(buttons=0,**{a:0. for a in AXES})
    if state is None:return out
    for target,src in profile['outputs'].items():
        v=source_value(src,state,profile['deadzone'])
        if target in AXES:out[target]=max(0.,v) if target in ('LT','RT') else v
        elif v>.5:out['buttons']|=BUTTONS[target]
    combo=profile.get('combo')
    if combo is not None and combo<len(state['buttons']) and state['buttons'][combo]:
        out['LT']=out['RT']=1.
    return out

def packet(out):
    signed=lambda v:round(max(-1,min(1,v))*(32767 if v>=0 else 32768))
    return struct.pack('<IBBhhhh6x',out['buttons'],round(out['LT']*255),round(out['RT']*255),
                       *(signed(out[a]) for a in ('LX','LY','RX','RY')))

def validate_profile(p):
    if not isinstance(p,dict) or p.get('version')!=1:raise ValueError('Unsupported profile format')
    if not isinstance(p.get('name'),str) or not 1<=len(p['name'])<=80:raise ValueError('Profile name must be 1–80 characters')
    if p.get('mode','Xbox gamepad') not in ('Xbox gamepad','Keyboard / mouse'):raise ValueError('Invalid output mode')
    if 'game' in p and (not isinstance(p['game'],str) or not 1<=len(p['game'])<=120):raise ValueError('Game name must be 1-120 characters')
    if 'target_roles' in p:
        roles=p['target_roles']
        if not isinstance(roles,dict) or any(k not in (*AXES,*BUTTONS) or not isinstance(v,str) or len(v)>80 for k,v in roles.items()):raise ValueError('Invalid action labels')
    dz=p.get('deadzone')
    if not isinstance(dz,(int,float)) or not math.isfinite(dz) or not 0<=dz<.95:raise ValueError('Invalid dead zone')
    def source(s):
        if not isinstance(s,dict) or s.get('kind') not in ('axis','button','hat'):raise ValueError('Invalid input source')
        if type(s.get('index')) is not int or not 0<=s['index']<128:raise ValueError('Input index out of range')
        if s.get('range','signed') not in ('signed','full','positive','negative'):raise ValueError('Invalid axis range')
        if type(s.get('invert',False)) is not bool:raise ValueError('Invalid inversion')
        if s.get('direction','up') not in ('up','down','left','right'):raise ValueError('Invalid hat direction')
    if not isinstance(p.get('outputs'),dict):raise ValueError('Missing mappings')
    for target,s in p['outputs'].items():
        if target not in (*AXES,*BUTTONS):raise ValueError('Unknown output')
        source(s)
    if p.get('combo') is not None and (type(p['combo']) is not int or not 0<=p['combo']<128):raise ValueError('Invalid combo button')
    if not isinstance(p.get('physical',{}),dict):raise ValueError('Invalid graphic assignments')
    for s in p.get('physical',{}).values():source(s)
    for field in ('keys','mouse'):
        if not isinstance(p.get(field,[]),list) or len(p.get(field,[]))>128:raise ValueError('Invalid bindings')
        for b in p.get(field,[]):
            source(b['source'])
            if field=='keys' and (type(b.get('vk')) is not int or not 1<=b['vk']<=254):raise ValueError('Invalid key')
            if field=='keys' and 'label' in b and (not isinstance(b['label'],str) or len(b['label'])>80):raise ValueError('Invalid key label')
            if field=='mouse' and b.get('action') not in ('x','y','left','right','middle'):raise ValueError('Invalid mouse action')
            if field=='mouse' and not 1<=b.get('speed',600)<=3000:raise ValueError('Invalid mouse speed')
    from macros import validate_macros
    validate_macros(p.get('macros',[]))
    result=copy.deepcopy(p)
    for field in ('keys','mouse'):result.setdefault(field,[])
    result.setdefault('macros',[])
    result.setdefault('physical',{});result.setdefault('combo',None)
    return result
