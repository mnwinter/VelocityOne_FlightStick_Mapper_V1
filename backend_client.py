"""Local-only VIIPER 0.9 TCP client. Owns exactly one bus; never touches other clients."""
import json
import socket
import time

class Viiper:
    def __init__(self,port=32422):
        self.port=port;self.bus=None;self.stream=None

    def request(self,command,timeout=2,cancel=None):
        deadline=time.monotonic()+timeout
        with socket.create_connection(('127.0.0.1',self.port),timeout=min(2,timeout)) as s:
            s.sendall(command.encode()+b'\0');chunks=[];size=0
            while True:
                if cancel is not None and cancel.is_set():
                    raise RuntimeError('VIIPER attachment cancelled')
                remaining=deadline-time.monotonic()
                if remaining<=0:raise TimeoutError(f'VIIPER {command.split()[0]} timed out after {timeout:g}s')
                # Poll cancellation without extending the overall response deadline.
                s.settimeout(min(.1,remaining) if cancel is not None else remaining)
                try:b=s.recv(4096)
                except socket.timeout:continue
                if not b:break
                size+=len(b)
                if size>65536:raise RuntimeError('Oversized VIIPER response')
                chunks.append(b)
        result=json.loads(b''.join(chunks).rstrip(b'\0') or b'{}')
        if result.get('status',200)>=400:raise RuntimeError(result.get('detail',str(result)))
        return result

    def connect(self,cancel=None):
        if self.request('ping').get('server')!='VIIPER':raise RuntimeError('Unexpected backend on local port')
        self.bus=self.request('bus/create')['busId']
        try:
            # USB/IP attachment is synchronous and can exceed the normal 2s API wait.
            d=self.request(f'bus/{self.bus}/add '+json.dumps({'type':'xbox360'}),timeout=10,cancel=cancel)
            self.stream=socket.create_connection(('127.0.0.1',self.port),timeout=1)
            self.stream.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
            self.stream.sendall(f"bus/{self.bus}/{d['devId']}\0".encode())
            self.stream.settimeout(.05)
        except Exception:
            self.close();raise

    def send(self,report):
        if not self.stream:raise RuntimeError('Virtual controller not connected')
        self.stream.sendall(report)
        # Rumble is not meaningful for the V1. Drain feedback to avoid back-pressure.
        import select
        if select.select([self.stream],[],[],0)[0]:
            if not self.stream.recv(4096):raise ConnectionError('VIIPER closed the controller stream')

    def close(self):
        if self.stream:
            try:self.stream.sendall(bytes(20))
            except OSError:pass
            self.stream.close();self.stream=None
        if self.bus is not None:
            bus=self.bus;self.bus=None
            try:self.request(f'bus/remove {bus}')
            except (OSError,ValueError,RuntimeError):pass
