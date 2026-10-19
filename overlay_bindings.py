"""V1 overlay assignments reported by the owner in the Windows live monitor.
Numbers in the UI are one-based; SDL indices are zero-based. These visual
bindings do not change output mappings, macros, or measured axis directions.
"""
import copy

def apply_reported_layout(profile):
    p=copy.deepcopy(profile)
    physical=p.setdefault('physical',{})
    for key,number in {'roll':1,'pitch':2,'twist':3,'H2_x':4,'H2_y':5,'lever_left':6,'lever_right':8}.items():
        physical.setdefault(key,dict(kind='axis',index=number-1,invert=False,range='full' if key.startswith('lever') else 'signed'))
    buttons={'wheel':15,'B16':16,'B17':17,'trigger':18}
    buttons.update(zip(('left_A','left_B','left_X','left_Y','right_A','right_B','right_X','right_Y'),range(1,9)))
    buttons.update({f'front_{i}':i for i in range(20,24)})
    buttons.update({f'slider_end_{i}':i for i in range(9,13)})
    for key,number in buttons.items():physical.setdefault(key,dict(kind='button',index=number-1))
    return p


def front_marker_slots(physical):
    """One marker for each of the four physical front-button positions.

    Learned symbol identities win. Numbered legacy aliases fill only the
    remaining positions, excluding inputs already represented by a name.
    The profile itself is never changed or its custom bindings discarded.
    """
    slots=('system_xbox','system_view','system_menu','system_capture')
    named={key:key for key in slots if physical.get(key)}
    used={physical[key].get('index') for key in named if physical[key].get('kind')=='button'}
    remaining=[f'front_{i}' for i in range(20,24)
               if physical.get(f'front_{i}',{}).get('index',i-1) not in used]
    for slot in slots:
        if slot not in named:named[slot]=remaining.pop(0)
    return named
