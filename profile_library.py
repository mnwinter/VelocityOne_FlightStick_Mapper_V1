"""Atomic user-preset storage grouped by game; legacy flat files remain readable."""
import hashlib,json,os,pathlib,re,tempfile
from core import validate_profile
from game_presets import CUSTOM_GAME

def _segment(text):
    safe=re.sub(r'[^\w .-]','_',text).strip(' .')[:44] or 'preset'
    digest=hashlib.sha256(text.casefold().encode('utf-8')).hexdigest()[:12]
    return 'p-'+safe+'-'+digest

def save_preset(root,profile,replace_path=None):
    p=validate_profile(profile);root=pathlib.Path(root).resolve()
    game=p.get('game',CUSTOM_GAME)
    path=root/_segment(game)/(_segment(p['name'])+'.json')
    if not path.resolve().is_relative_to(root):raise ValueError('Invalid preset path')
    if path.exists() and (replace_path is None or pathlib.Path(replace_path).resolve()!=path.resolve()):
        raise ValueError('A user preset with this name already exists for this game. Choose another name, or load that user preset before editing it.')
    data=json.dumps(p,indent=2,ensure_ascii=False)
    if len(data.encode('utf-8'))>1_000_000:raise ValueError('Preset exceeds 1 MB size limit')
    path.parent.mkdir(parents=True,exist_ok=True)
    # A unique staging file avoids sharing a .tmp file across app instances.
    # Flush the complete destination before removing the old managed preset.
    old=pathlib.Path(replace_path).resolve() if replace_path is not None else None
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,suffix='.tmp',delete=False) as stream:
        temp=pathlib.Path(stream.name)
        try:
            stream.write(data);stream.flush();os.fsync(stream.fileno())
        except BaseException:
            stream.close();temp.unlink(missing_ok=True);raise
    try:
        if old==path.resolve():
            temp.replace(path)
        else:
            # Atomic no-clobber publication: a concurrent/new unrelated file wins.
            try:os.link(temp,path)
            except FileExistsError:raise ValueError('A user preset with this name already exists for this game.')
            if old is not None and old.is_relative_to(root) and old.is_file():
                try:old.unlink()
                except OSError:
                    path.unlink(missing_ok=True)
                    raise
    finally:temp.unlink(missing_ok=True)
    return path

def list_presets(root,game=None):
    root=pathlib.Path(root).resolve();found={}
    for path in root.rglob('*.json'):
        try:
            if not path.resolve().is_relative_to(root) or path.stat().st_size>1_000_000:continue
            p=validate_profile(json.loads(path.read_text(encoding='utf-8')))
            name=p.get('game',CUSTOM_GAME)
            if game is not None and name!=game:continue
            key=(name.casefold(),p['name'].casefold())
            if key not in found or path.stat().st_mtime_ns>found[key][1].stat().st_mtime_ns:found[key]=(p,path)
        except (OSError,ValueError,KeyError,TypeError):continue
    return sorted(found.values(),key=lambda item:(item[0].get('game',CUSTOM_GAME).casefold(),item[0]['name'].casefold()))
