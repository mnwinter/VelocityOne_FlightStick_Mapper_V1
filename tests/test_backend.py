import json,socket,threading,time,unittest
from backend_client import Viiper

class BackendTests(unittest.TestCase):
    def test_protocol_lifecycle(self):
        server=socket.socket();server.bind(('127.0.0.1',0));server.listen();port=server.getsockname()[1]
        commands=[];packets=[]
        def serve():
            for _ in range(5):
                c,_=server.accept();data=b''
                while not data.endswith(b'\0'):data+=c.recv(1)
                cmd=data[:-1].decode();commands.append(cmd)
                if cmd=='bus/create':c.sendall(b'{"busId":7}')
                elif '/add ' in cmd:c.sendall(b'{"busId":7,"devId":"1"}')
                elif cmd=='bus/7/1':
                    data=b''
                    while len(data)<40:
                        v=c.recv(40-len(data))
                        if not v:break
                        data+=v
                    packets.append(data)
                elif cmd=='ping':c.sendall(b'{"server":"VIIPER"}')
                else:c.sendall(b'{}')
                c.close()
            server.close()
        t=threading.Thread(target=serve,daemon=True);t.start()
        v=Viiper(port);v.connect();v.send(bytes([1])+bytes(19));v.close();t.join(3)
        self.assertFalse(t.is_alive());self.assertEqual(packets,[bytes([1])+bytes(39)])
        self.assertEqual(commands[-1],'bus/remove 7')

class AttachmentTimingTests(unittest.TestCase):
    def test_slow_windows_attachment_keeps_bus_until_response(self):
        server=socket.socket();server.bind(('127.0.0.1',0));server.listen();server.settimeout(5)
        commands=[];errors=[]
        def serve():
            try:
                while True:
                    c,_=server.accept()
                    with c:
                        data=b''
                        while not data.endswith(b'\0'):data+=c.recv(1)
                        cmd=data[:-1].decode();commands.append(cmd)
                        if cmd=='ping':c.sendall(b'{"server":"VIIPER"}')
                        elif cmd=='bus/create':c.sendall(b'{"busId":7}')
                        elif '/add ' in cmd:
                            time.sleep(2.15) # Actual USB/IP attachment takes just over two seconds.
                            c.sendall(b'{"busId":7,"devId":"1"}')
                        elif cmd=='bus/7/1':
                            while c.recv(64):pass
                        else:
                            c.sendall(b'{}');return
            except Exception as e:errors.append(e)
            finally:server.close()
        t=threading.Thread(target=serve,daemon=True);t.start()
        v=Viiper(server.getsockname()[1])
        try:v.connect();self.assertIsNotNone(v.stream)
        finally:v.close();t.join(6)
        self.assertFalse(errors);self.assertFalse(t.is_alive())
        self.assertEqual(commands[-2:],['bus/7/1','bus/remove 7'])

    def test_attachment_wait_can_be_cancelled(self):
        server=socket.socket();server.bind(('127.0.0.1',0));server.listen()
        cancel=threading.Event();received=threading.Event()
        def serve():
            c,_=server.accept()
            with c:
                c.recv(1024);received.set();cancel.wait(2);time.sleep(.2)
            server.close()
        t=threading.Thread(target=serve,daemon=True);t.start()
        timer=threading.Timer(.15,cancel.set);timer.start()
        start=time.monotonic()
        try:
            with self.assertRaisesRegex(RuntimeError,'cancelled'):
                Viiper(server.getsockname()[1]).request('test',timeout=10,cancel=cancel)
            self.assertLess(time.monotonic()-start,.8)
        finally:cancel.set();timer.join();t.join(3)

if __name__=='__main__':unittest.main()
