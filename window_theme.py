"""Per-window Windows 11 frame colors; native sizing and caption buttons retained.
Reference: https://learn.microsoft.com/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute
"""
import ctypes,sys
from ctypes import wintypes
from PySide6.QtCore import QObject,QEvent
from PySide6.QtWidgets import QWidget,QApplication

def apply_dark_titlebar(handle):
    if sys.platform!='win32':return False
    try:
        dwm=ctypes.WinDLL('dwmapi')
        setter=dwm.DwmSetWindowAttribute
        setter.argtypes=[wintypes.HWND,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD]
        setter.restype=ctypes.c_long
        # BOOL and COLORREF are 32-bit, even when HWND is 64-bit.
        colors={20:1,34:0x201811,35:0x201811,36:0xf2e5dc}
        results=[]
        for attribute,value in colors.items():
            data=ctypes.c_uint32(value)
            results.append(setter(wintypes.HWND(handle),attribute,ctypes.byref(data),ctypes.sizeof(data)))
        return all(result==0 for result in results)
    except (OSError,AttributeError):return False

class DarkWindowFrames(QObject):
    def eventFilter(self,obj,event):
        if (event.type()==QEvent.Type.Show and isinstance(obj,QWidget)
                and obj.isWindow() and QApplication.platformName()=='windows'):
            apply_dark_titlebar(int(obj.winId()))
        return False
