"""SDL polling supports the physical V1 in the background, without grabbing it."""
import os,time
os.environ['SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS']='1'
os.environ['SDL_JOYSTICK_HIDAPI']='0'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
import pygame

class Flightstick:
    def __init__(self):
        pygame.display.init();pygame.joystick.init();self.device=None;self.closed=False
        self.name='V1 disconnected';self.guid='';self.last_scan=0
    def poll(self):
        if self.closed or not pygame.display.get_init():return None
        try:events=pygame.event.get()
        except pygame.error:return None
        for event in events:
            if event.type==pygame.JOYDEVICEREMOVED and self.device and event.instance_id==self.device.get_instance_id():
                self.device.quit();self.device=None
        now=time.monotonic()
        if self.device is None and now-self.last_scan>.5:
            self.last_scan=now
            for i in range(pygame.joystick.get_count()):
                d=pygame.joystick.Joystick(i)
                # Exact original V1 USB VID/PID observed on this hardware. Never capture virtual output or V2.
                if 'f510000055700000' in d.get_guid():
                    self.device=d;self.name=d.get_name();self.guid=d.get_guid();break
        if not self.device:return None
        try:
            d=self.device
            return dict(axes=[d.get_axis(i) for i in range(d.get_numaxes())],
                        buttons=[bool(d.get_button(i)) for i in range(d.get_numbuttons())],
                        hats=[d.get_hat(i) for i in range(d.get_numhats())])
        except pygame.error:self.device=None;return None
    def close(self):
        self.closed=True
        pygame.joystick.quit();pygame.display.quit()
