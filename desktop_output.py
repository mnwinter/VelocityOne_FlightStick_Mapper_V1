"""Balanced Windows input injection; only keys/buttons owned by this app are released."""
import ctypes as C
from ctypes import wintypes as W
from core import source_value

class MOUSEINPUT(C.Structure):
    _fields_=[('dx',W.LONG),('dy',W.LONG),('mouseData',W.DWORD),('dwFlags',W.DWORD),('time',W.DWORD),('dwExtraInfo',C.c_size_t)]
class KEYBDINPUT(C.Structure):
    _fields_=[('wVk',W.WORD),('wScan',W.WORD),('dwFlags',W.DWORD),('time',W.DWORD),('dwExtraInfo',C.c_size_t)]
class HARDWAREINPUT(C.Structure):
    _fields_=[('uMsg',W.DWORD),('wParamL',W.WORD),('wParamH',W.WORD)]
class INPUTUNION(C.Union):
    _fields_=[('mi',MOUSEINPUT),('ki',KEYBDINPUT),('hi',HARDWAREINPUT)]
class INPUT(C.Structure):
    _anonymous_=('u',);_fields_=[('type',W.DWORD),('u',INPUTUNION)]

class DesktopOutput:
    def __init__(self):
        self.user=C.WinDLL('user32',use_last_error=True)
        self.user.SendInput.argtypes=[W.UINT,C.POINTER(INPUT),C.c_int];self.user.SendInput.restype=W.UINT
        self.keys=set();self.buttons=set();self.fraction=[0.,0.]
    def send(self,i):
        if self.user.SendInput(1,C.byref(i),C.sizeof(INPUT))!=1:
            raise OSError('Windows rejected input injection; elevated games may require equal privileges.')
    def key(self,vk,down):
        scan=self.user.MapVirtualKeyW(vk,0)
        extended=vk in (0x21,0x22,0x23,0x24,0x25,0x26,0x27,0x28,0x2d,0x2e,0xa3,0xa5,0x5b,0x5c)
        flags=8|(0 if down else 2)|(1 if extended else 0)
        self.send(INPUT(type=1,ki=KEYBDINPUT(0,scan,flags,0,0)))
    def mouse(self,action,down):
        flags={'left':(2,4),'right':(8,16),'middle':(32,64)}[action][0 if down else 1]
        self.send(INPUT(type=0,mi=MOUSEINPUT(0,0,0,flags,0,0)))
    def update(self,p,state,dt,macro_outputs=()):
        wanted={b['vk'] for b in p.get('keys',[]) if source_value(b['source'],state,p['deadzone'])>.5}
        wanted.update(int(t[4:]) for t in macro_outputs if t.startswith('key:'))
        modifiers={16,17,18,0xa0,0xa1,0xa2,0xa3,0xa4,0xa5,0x5b,0x5c}
        # Chords must press modifiers before ordinary keys and release them last.
        for k in sorted(self.keys-wanted,key=lambda k:(k in modifiers,k)):self.key(k,False);self.keys.remove(k)
        for k in sorted(wanted-self.keys,key=lambda k:(k not in modifiers,k)):self.key(k,True);self.keys.add(k)
        wanted_mouse=set();delta=[0.,0.]
        for b in p.get('mouse',[]):
            v=source_value(b['source'],state,p['deadzone']);a=b['action']
            if a in ('x','y'):delta[0 if a=='x' else 1]+=v*b.get('speed',600)*dt
            elif v>.5:wanted_mouse.add(a)
        wanted_mouse.update(t[6:] for t in macro_outputs if t.startswith('mouse:'))
        for b in self.buttons-wanted_mouse:self.mouse(b,False);self.buttons.remove(b)
        for b in wanted_mouse-self.buttons:self.mouse(b,True);self.buttons.add(b)
        self.fraction=[self.fraction[i]+delta[i] for i in (0,1)]
        xy=[int(v) for v in self.fraction];self.fraction=[self.fraction[i]-xy[i] for i in (0,1)]
        if any(xy):self.send(INPUT(type=0,mi=MOUSEINPUT(*xy,0,1,0,0)))
    def release(self):
        for k in sorted(self.keys,key=lambda k:(k in {16,17,18,0xa0,0xa1,0xa2,0xa3,0xa4,0xa5,0x5b,0x5c},k)):
            try:self.key(k,False);self.keys.remove(k)
            except OSError:pass
        for b in list(self.buttons):
            try:self.mouse(b,False);self.buttons.remove(b)
            except OSError:pass
        self.fraction=[0.,0.]
