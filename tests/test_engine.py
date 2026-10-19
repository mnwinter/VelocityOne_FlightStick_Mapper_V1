import threading,time,unittest
from unittest.mock import patch,MagicMock
from core import default_profile

class EngineTests(unittest.TestCase):
    def test_stop_during_backend_start_sends_no_stale_report(self):
        import engine
        entered=threading.Event();proceed=threading.Event();connected=threading.Event()
        fake=MagicMock();fake.connect.side_effect=lambda **kwargs:connected.set()
        def launch(_):entered.set();proceed.wait(2)
        with patch.object(engine,'DesktopOutput'),patch.object(engine,'Viiper',return_value=fake),patch.object(engine.Engine,'launch_backend',launch):
            e=engine.Engine('.')
            try:
                p=default_profile();p['combo']=0
                e.snapshot(p,dict(axes=[0]*8,buttons=[True],hats=[(0,0)]));e.start('Xbox gamepad')
                self.assertTrue(entered.wait(1));e.stop();proceed.set();self.assertTrue(connected.wait(1))
                time.sleep(.05);fake.send.assert_not_called()
            finally:proceed.set();e.close()

    def test_old_start_failure_does_not_cancel_new_mode(self):
        import engine
        entered=threading.Event();proceed=threading.Event()
        def launch(_):
            entered.set();proceed.wait(2);raise RuntimeError('Old startup failed')
        with patch.object(engine,'DesktopOutput'),patch.object(engine.Engine,'launch_backend',launch):
            e=engine.Engine('.')
            try:
                e.snapshot(default_profile(),dict(axes=[0,0],buttons=[],hats=[]));e.start('Xbox gamepad')
                self.assertTrue(entered.wait(1))
                e.stop();e.start('Keyboard / mouse');proceed.set()
                deadline=time.monotonic()+1
                while not e.active and time.monotonic()<deadline:time.sleep(.005)
                self.assertTrue(e.active);self.assertTrue(e.want);self.assertEqual(e.error,'')
            finally:proceed.set();e.close()

    def test_backend_uses_private_ports_and_reuses_only_its_own_process(self):
        import engine,tempfile,pathlib
        listeners=[]
        for port in (41001,41002,41003,41004):
            listener=MagicMock();listener.getsockname.return_value=('127.0.0.1',port);listeners.append(listener)
        clients=[]
        def client(port):
            v=MagicMock();clients.append((port,v));return v
        processes=[MagicMock(),MagicMock()]
        for process in processes:process.poll.return_value=None
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);(root/'backend').mkdir();(root/'backend'/'viiper.exe').touch()
            engines=[]
            with patch.object(engine.socket,'socket',side_effect=listeners),patch.object(engine,'Viiper',side_effect=client),patch.object(engine.subprocess,'Popen',side_effect=processes) as spawn:
                try:
                    for _ in range(2):
                        e=engine.Engine.__new__(engine.Engine)
                        e.root=e.resources=root;e.process=e.log=None;e.api_port=e.usb_port=None;e.done=MagicMock();e.done.wait.return_value=False
                        engines.append(e);e.launch_backend()
                    self.assertEqual([(e.api_port,e.usb_port) for e in engines],[(41001,41002),(41003,41004)])
                    for index,call in enumerate(spawn.call_args_list):
                        args=call.args[0]
                        self.assertIn(f'--api.addr=127.0.0.1:{engines[index].api_port}',args)
                        self.assertIn(f'--usb.addr=127.0.0.1:{engines[index].usb_port}',args)
                        self.assertIn('--api.device-handler-connect-timeout=15s',args)
                    engines[0].launch_backend()
                    self.assertEqual(spawn.call_count,2)
                    self.assertEqual([port for port,_ in clients],[41001,41003,41001])
                    for listener in listeners:listener.close.assert_called_once()
                finally:
                    for e in engines:
                        if e.log:e.log.close()

    def test_closing_one_engine_terminates_only_its_private_backend(self):
        import engine
        processes=[MagicMock(),MagicMock()]
        for process in processes:process.poll.return_value=None
        with patch.object(engine,'DesktopOutput'):
            first=engine.Engine('.');second=engine.Engine('.')
            first.process,second.process=processes
            try:
                first.close()
                processes[0].terminate.assert_called_once()
                processes[1].terminate.assert_not_called()
            finally:second.close()
            processes[1].terminate.assert_called_once()

    def test_macro_worker_cancel_restart_edit_and_disconnect(self):
        import engine
        from test_desktop import DesktopTests
        d=DesktopTests().make()
        p=default_profile();p['macros']=[dict(name='Held key',source=dict(kind='button',index=0),trigger='press',repeat='toggle',count=2,gap_ms=100,steps=[dict(outputs=['key:65','mouse:left'],duration_ms=10000,delay_ms=0)])]
        def state(value):return dict(axes=[],buttons=[value],hats=[])
        with patch.object(engine,'DesktopOutput',return_value=d):
            e=engine.Engine('.')
            def until(predicate):
                deadline=time.monotonic()+1
                while not predicate() and time.monotonic()<deadline:time.sleep(.005)
                self.assertTrue(predicate())
            try:
                e.snapshot(p,state(False));e.start('Keyboard / mouse');until(lambda:e.active)
                e.snapshot(p,state(True));until(lambda:65 in d.keys)
                e.stop();until(lambda:not d.keys and not d.buttons)
                e.start('Keyboard / mouse');until(lambda:e.active);time.sleep(.025)
                self.assertFalse(d.keys) # A held trigger is disarmed across restart.
                e.snapshot(p,state(False));time.sleep(.025);e.snapshot(p,state(True));until(lambda:65 in d.keys)
                p['macros'][0]['name']='Edited';e.snapshot(p,state(True));until(lambda:not d.keys)
                e.snapshot(p,state(False));time.sleep(.025);e.snapshot(p,state(True));until(lambda:65 in d.keys)
                e.snapshot(p,None);until(lambda:not d.keys and not d.buttons and not e.want)
            finally:e.close()

if __name__=='__main__':unittest.main()


