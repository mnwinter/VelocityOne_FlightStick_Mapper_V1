# Public release: onefile by default; V1_BUILD_KIND=portable creates replaceable libraries.
from pathlib import Path
import os
root=Path(SPECPATH)
onefile=os.environ.get('V1_BUILD_KIND','onefile')=='onefile'
datas=[(str(root/'assets'),'assets'),(str(root/'licenses'),'licenses'),(str(root/'docs'),'docs'),
       (str(root/'backend'/'VIIPER-v0.9.0-source.zip'),'backend')]
for name in ('README.md','THIRD_PARTY.md','LICENSE','COPYRIGHT','dependencies.lock.json'):
    datas.append((str(root/name),'.'))
for file in list(root.glob('*.py'))+[root/'requirements.txt',root/'build.ps1',root/'VelocityOneMapper.spec']:
    datas.append((str(file),'source'))
for folder in ('tests','scripts'):
    datas.append((str(root/folder),'source/'+folder))
excluded=['PySide6.QtWebEngineCore','PySide6.QtWebEngineWidgets','PySide6.QtPdf',
          'PySide6.QtQml','PySide6.QtQuick','PySide6.QtOpenGL','PySide6.QtVirtualKeyboard',
          'pygame.mixer','pygame.mixer_music','pygame.font','pygame.freetype','pygame._freetype',
          'pygame.ftfont','pygame.sysfont','pygame.imageext','pygame.midi','pygame.pypm','pygame._sdl2.mixer']
a=Analysis([str(root/'app.py')],pathex=[str(root)],
    binaries=[(str(root/'backend'/'viiper.exe'),'backend'),(str(root/'backend'/'USBip-0.9.8.1-x64.exe'),'backend')],
    datas=datas,hiddenimports=[],hookspath=[],hooksconfig={},runtime_hooks=[],excludes=excluded,noarchive=False,optimize=0)
codec_dlls={'sdl2_image.dll','sdl2_mixer.dll','sdl2_ttf.dll','freetype.dll','libjpeg-62.dll','libogg-0.dll',
    'libopus-0.dll','libopusfile-0.dll','libpng16-16.dll','libtiff-5.dll','libwavpack-1.dll','libwebp-7.dll',
    'libwebpdemux-2.dll','libxmp.dll','portmidi.dll'}
qt_keep={'qt6core.dll','qt6gui.dll','qt6widgets.dll','qt6network.dll'}
def wanted(entry):
    target=entry[0].replace('\\','/').lower();name=target.rsplit('/',1)[-1]
    if name.startswith(('vcruntime','msvcp','concrt','api-ms-win')) or name in {'ucrtbase.dll','icuuc.dll','icudt78.dll'}:return False
    if name in codec_dlls:return False
    if '/plugins/' in target and name not in {'qwindows.dll','qoffscreen.dll','qico.dll'}:return False
    if name.startswith('qt6') and name.endswith('.dll') and name not in qt_keep:return False
    return True
a.binaries=[entry for entry in a.binaries if wanted(entry)]
a.datas=[entry for entry in a.datas if not entry[0].lower().endswith(('freesansbold.ttf','.pyc')) and '/__pycache__/' not in entry[0].replace(chr(92),'/')]
pyz=PYZ(a.pure)
if onefile:
    exe=EXE(pyz,a.scripts,a.binaries,a.datas,[],name='VelocityOneMapper',debug=False,
        bootloader_ignore_signals=False,strip=False,upx=False,console=False,icon=str(root/'assets'/'controlstation.ico'))
else:
    exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name='VelocityOneMapper',debug=False,
        bootloader_ignore_signals=False,strip=False,upx=False,console=False,icon=str(root/'assets'/'controlstation.ico'))
    coll=COLLECT(exe,a.binaries,a.datas,strip=False,upx=False,name='VelocityOneMapper')


