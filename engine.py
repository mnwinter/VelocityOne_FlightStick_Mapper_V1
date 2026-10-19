"""Output worker: bounded waits, fresh snapshots, neutral cleanup, no GUI calls."""
import copy,os,pathlib,socket,subprocess,threading,time
from backend_client import Viiper
from core import evaluate,packet
from desktop_output import DesktopOutput
from macros import MacroRunner,merge_gamepad

class Engine:
    def __init__(self,root,resources=None):
        self.root=pathlib.Path(root);self.resources=pathlib.Path(resources) if resources is not None else self.root;self.lock=threading.Lock();self.done=threading.Event()
        self.active=False;self.want=False;self.mode='Xbox gamepad';self.status='Output stopped'
        self.profile=None;self.state=None;self.stamp=0.;self.error='';self.gamepad=None
        self.process=None;self.log=None;self.epoch=0;self.api_port=None;self.usb_port=None
        self.thread=threading.Thread(target=self.run,daemon=True);self.thread.start()
    def snapshot(self,profile,state):
        with self.lock:self.profile=copy.deepcopy(profile);self.state=copy.deepcopy(state);self.stamp=time.monotonic()
    def start(self,mode):
        with self.lock:self.mode=mode;self.error='';self.want=True;self.epoch+=1
    def stop(self):
        with self.lock:self.want=False;self.epoch+=1
    def launch_backend(self):
        # A server is private to this Engine: never borrow a different app's bus server.
        if self.process is not None and self.process.poll() is None:
            Viiper(self.api_port).request('ping');return
        if self.log:self.log.close();self.log=None
        exe=self.resources/'backend'/'viiper.exe'
        if not exe.exists():raise RuntimeError('VIIPER executable missing from backend folder')
        env=os.environ.copy()
        extra=[str(p) for base in (pathlib.Path(os.environ.get('ProgramFiles','C:/Program Files')),)
               for p in (base/'USBip',base/'USBip'/'bin')]
        env['PATH']=os.pathsep.join(extra+[env.get('PATH','')])
        (self.root/'logs').mkdir(parents=True,exist_ok=True)
        self.log=open(self.root/'logs'/'backend.log','ab')
        # Reserve both ephemeral ports together so API and USB never select the same port.
        # VIIPER accepts addresses, not inherited sockets, so release immediately before spawn.
        reservations=[]
        try:
            for _ in range(2):
                listener=socket.socket()
                reservations.append(listener)
                if hasattr(socket,'SO_EXCLUSIVEADDRUSE'):
                    listener.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
                listener.bind(('127.0.0.1',0))
            self.api_port,self.usb_port=(listener.getsockname()[1] for listener in reservations)
        finally:
            for listener in reservations:listener.close()
        self.process=subprocess.Popen([str(exe),'server',f'--api.addr=127.0.0.1:{self.api_port}',
            f'--usb.addr=127.0.0.1:{self.usb_port}','--api.device-handler-connect-timeout=15s','--no-tray','--update-notify=none'],
            cwd=exe.parent,env=env,stdout=self.log,stderr=self.log,creationflags=subprocess.CREATE_NO_WINDOW)
        v=Viiper(self.api_port)
        for _ in range(40):
            if self.done.wait(.1):raise RuntimeError('Stopped')
            if self.process.poll() is not None:raise RuntimeError('VIIPER could not start; inspect the app logs/backend.log')
            try:v.request('ping');return
            except OSError:pass
        raise RuntimeError('Timed out starting VIIPER')
    def run(self):
        desktop=DesktopOutput();macros=MacroRunner();v=None;last=time.monotonic();last_mode=None;last_epoch=-1
        try:
            while not self.done.wait(.008):
                now=time.monotonic();dt=min(now-last,.05);last=now
                with self.lock:
                    want=self.want;mode=self.mode;p=self.profile;s=self.state;fresh=now-self.stamp<.25;epoch=self.epoch
                if epoch!=last_epoch:
                    macros.reset();desktop.release();last_epoch=epoch
                if not want or not fresh or s is None:
                    macros.reset()
                    desktop.release()
                    if v:v.close();v=None
                    if want and (not fresh or s is None):
                        with self.lock:
                            if self.epoch==epoch:
                                self.want=False;self.error='Input disconnected or stalled. Reconnect, then Start output again.'
                    with self.lock:
                        if self.epoch==epoch:self.active=False;self.status=self.error or 'Output stopped'
                    continue
                try:
                    if last_mode!=mode:
                        desktop.release()
                        if v:v.close();v=None
                        last_mode=mode
                    if mode=='Xbox gamepad':
                        if v is None:
                            self.status='Starting VIIPER…';self.launch_backend();v=Viiper(self.api_port);v.connect(cancel=self.done)
                        # Startup/attachment can block. Stop, unplug or configuration changes
                        # during it must win over the earlier captured snapshot.
                        with self.lock:
                            valid=self.want and self.epoch==epoch and self.mode==mode and self.state is not None and time.monotonic()-self.stamp<.25
                            p=self.profile;s=self.state
                        if not valid:
                            v.close();v=None;continue
                        tokens=macros.update(p.get('macros',[]),s,time.monotonic())
                        v.send(packet(merge_gamepad(evaluate(p,s),tokens)))
                        desktop.update(dict(p,keys=[],mouse=[]),s,dt,tokens)
                        self.status='Streaming to VIIPER • check Windows controller test for attachment'
                    else:
                        tokens=macros.update(p.get('macros',[]),s,now)
                        desktop.update(p,s,dt,tokens);self.status='Keyboard / mouse output active'
                    self.active=True
                except Exception as e:
                    macros.reset();desktop.release()
                    if v:v.close();v=None
                    # A failed old attachment must not cancel a newer Stop/Start request.
                    with self.lock:
                        if self.epoch==epoch:
                            self.want=False;self.active=False;self.error=str(e);self.status=self.error
        finally:
            desktop.release()
            if v:v.close()
            if self.process and self.process.poll() is None:
                self.process.terminate()
                try:self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:self.process.kill()
            if self.log:self.log.close()
    def close(self):self.done.set();self.thread.join(6)
