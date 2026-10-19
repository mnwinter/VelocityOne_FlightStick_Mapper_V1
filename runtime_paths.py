"""Keep embedded resources read-only and persistent user data outside extraction folders."""
import hashlib,os,pathlib,shutil
from profile_library import list_presets,save_preset

def select_data_root(frozen,source_dir,local_appdata,override=None):
    if override is not None:return pathlib.Path(override)
    return pathlib.Path(local_appdata)/'VelocityOneMapper' if frozen else pathlib.Path(source_dir)

def prepare_user_data(root,legacy_roots=()):
    root=pathlib.Path(root).resolve();(root/'profiles').mkdir(parents=True,exist_ok=True);(root/'logs').mkdir(exist_ok=True)
    copied=0
    for legacy in legacy_roots:
        legacy=pathlib.Path(legacy).resolve()
        if legacy==root:continue
        for profile,source_path in list_presets(legacy/'profiles'):
            try:
                target=save_preset(root/'profiles',profile)
                original=source_path.stat();os.utime(target,ns=(original.st_atime_ns,original.st_mtime_ns))
                copied+=1
            except ValueError:pass # Existing user presets always win over legacy copies.
    return copied

def stage_driver_installer(resources,user_data):
    source=pathlib.Path(resources)/'backend'/'USBip-0.9.8.1-x64.exe'
    target=pathlib.Path(user_data)/'setup'/source.name
    expected=hashlib.sha256(source.read_bytes()).digest()
    target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists() or hashlib.sha256(target.read_bytes()).digest()!=expected:
        temp=target.with_suffix('.tmp');shutil.copyfile(source,temp);temp.replace(target)
    if hashlib.sha256(target.read_bytes()).digest()!=expected:raise OSError('Bundled driver installer integrity check failed')
    return target
