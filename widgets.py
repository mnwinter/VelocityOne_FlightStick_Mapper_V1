"""V1 schematic instrumentation and explicit source learning; no synthetic live data."""
import copy,time
from PySide6.QtCore import Qt,QTimer,QRectF,QPointF,Signal
from PySide6.QtGui import QPainter,QPixmap,QColor,QPen,QFont
from PySide6.QtWidgets import (QWidget,QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,
    QSpinBox,QCheckBox,QPushButton,QDialogButtonBox,QFormLayout)
from core import source_value
from overlay_bindings import front_marker_slots

def source_text(s):
    if not s:return 'Unassigned'
    text=f"{s['kind'].title()} {s['index']+1}"
    if s['kind']=='axis':text+=' · '+s.get('range','signed')+(' · inverted' if s.get('invert') else '')
    if s['kind']=='hat':text+=' · '+s.get('direction','up')
    return text

class SourceDialog(QDialog):
    def __init__(self,title,provider,source=None,parent=None,button_only=False):
        super().__init__(parent);self.setWindowTitle(title);self.setMinimumWidth(430)
        self.provider=provider;self.baseline=None;self.learning=False;self.deadline=0
        self.button_only=button_only
        l=QVBoxLayout(self);intro=QLabel('Press Learn, then move one axis or press one button.\nNumbers below are SDL inputs, starting at 1.');l.addWidget(intro)
        slider_row=QHBoxLayout()
        slider_row.addWidget(QLabel('Slider ends:'))
        for number in range(9,13):
            pick=QPushButton(f'B{number}')
            pick.setObjectName(f'sliderPick{number}')
            pick.setToolTip('Digital slider-end input past min/max; independent of its analog axis.')
            pick.clicked.connect(lambda checked=False,n=number:self.pick_slider_end(n))
            slider_row.addWidget(pick)
        l.addLayout(slider_row)
        f=QFormLayout();self.kind=QComboBox();self.kind.addItems(['button'] if button_only else ['axis','button','hat'])
        self.index=QSpinBox();self.index.setRange(1,128);self.range=QComboBox();self.range.addItems(['signed','full','positive','negative'])
        self.invert=QCheckBox('Invert axis');self.direction=QComboBox();self.direction.addItems(['up','down','left','right'])
        for name,w in [('Input type',self.kind),('Input number',self.index),('Axis range',self.range),('Hat direction',self.direction),('',self.invert)]:f.addRow(name,w)
        l.addLayout(f)
        note=QLabel('signed: centered stick  •  full: entire lever travel\npositive / negative: one half of a centered axis');note.setWordWrap(True);l.addWidget(note)
        self.notice=QLabel('Ready to learn');self.notice.setWordWrap(True);l.addWidget(self.notice)
        b=QPushButton('Learn from Flightstick');b.clicked.connect(self.learn);l.addWidget(b)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject);l.addWidget(buttons)
        if source:
            self.kind.setCurrentText(source['kind']);self.index.setValue(source['index']+1)
            self.range.setCurrentText(source.get('range','signed'));self.invert.setChecked(source.get('invert',False));self.direction.setCurrentText(source.get('direction','up'))
        self.timer=QTimer(self);self.timer.timeout.connect(self.tick);self.timer.start(25)
        self.finished.connect(self.timer.stop)
    def exec(self):
        try:return super().exec()
        finally:
            self.timer.stop()
            # Deferred deletion preserves immediate source() access by the caller.
            self.deleteLater()
    def pick_slider_end(self,number):
        self.learning=False
        self.kind.setCurrentText('button')
        self.index.setValue(number) # source() converts the one-based UI number to SDL.
        self.notice.setText(f'Slider end Button {number} selected. Confirm with OK.')
    def source(self):return dict(kind=self.kind.currentText(),index=self.index.value()-1,range=self.range.currentText(),invert=self.invert.isChecked(),direction=self.direction.currentText())
    def learn(self):
        self.baseline=copy.deepcopy(self.provider())
        if self.baseline is None:self.notice.setText('Connect the V1 in PC mode first.');return
        self.learning=True;self.deadline=time.monotonic()+10;self.notice.setText('Listening… move one control. Keep other controls still.')
    def tick(self):
        if not self.learning:return
        s=self.provider()
        if s is None or time.monotonic()>self.deadline:
            self.learning=False;self.notice.setText('No input captured. Press Learn to retry.');return
        for i,(old,new) in enumerate(zip(self.baseline['buttons'],s['buttons'])):
            if new and not old:self.kind.setCurrentText('button');self.index.setValue(i+1);break
        else:
            if self.button_only:return
            changed=[(abs(v-self.baseline['axes'][i]),i) for i,v in enumerate(s['axes'])]
            if changed and max(changed)[0]>.35:
                self.kind.setCurrentText('axis');self.index.setValue(max(changed)[1]+1)
            else:
                for i,(x,y) in enumerate(s['hats']):
                    if (x,y)!=(0,0) and (x,y)!=tuple(self.baseline['hats'][i]):
                        self.kind.setCurrentText('hat');self.index.setValue(i+1)
                        self.direction.setCurrentText('up' if y>0 else 'down' if y<0 else 'right' if x>0 else 'left');break
                else:return
        self.learning=False;self.notice.setText('Captured '+source_text(self.source())+'. Review range and inversion, then OK.')

# Illustration coordinates refer to the original 2400×1350 V1 top photograph.
# Clickable labels are physical regions; sources must be learned rather than guessed.
REGIONS={
 'roll':('Roll',(1160,700)), 'pitch':('Pitch',(1160,420)), 'twist':('Twist',(1160,790)),
 'lever_left':('Left lever',(795,551)), 'lever_right':('Right lever',(1506,551)),
 'H1':('H1 hat',(1108,530)), 'H2':('H2 / B19',(1208,530)),
 'B16':('B16',(1108,585)), 'B17':('B17',(1210,585)), 'wheel':('Thumb wheel',(1160,606)),
 'trigger':('Trigger · rear (not visible)',(1160,390)),
 'left_A':('Left A',(814,716)), 'left_B':('Left B',(814,783)),
 'left_X':('Left X',(814,850)), 'left_Y':('Left Y',(814,918)),
 'right_A':('Right A',(1503,716)), 'right_B':('Right B',(1503,783)),
 'right_X':('Right X',(1503,850)), 'right_Y':('Right Y',(1503,918)),
 'system_xbox':('Xbox / Guide',(1160,996)),
 'system_view':('View · overlapping squares',(1110,1031)),
 'system_menu':('Menu · three lines',(1209,1031)),
 'system_capture':('Capture / Share',(1160,1052))}

# Numeric front-button callouts avoid guessing Xbox/View/Menu/Capture identity.
REGIONS.update({f'front_{i}':(f'Front button {i}',(0,0)) for i in range(20,24)})
REGIONS.update({f'slider_end_{i}':(f'Slider end B{i} · past min/max',(0,0)) for i in range(9,13)})

# Only mark controls actually visible in the front illustration. Base buttons and the
# rear trigger remain configurable in the list; they are not drawn on fake locations.
FRONT_POINTS={
 'roll':(1167,950),'pitch':(1167,520),'twist':(1167,715),
 'lever_left':(810,845),'lever_right':(1512,845),
 'H1':(1120,210),'H2':(1210,205),'B16':(1117,285),
 'B17':(1213,285),'wheel':(1168,322),
 'system_xbox':(1168,983),'system_view':(1123,998),
 'system_menu':(1213,998),'system_capture':(1168,1010)}

class ControllerView(QWidget):
    selected=Signal(str)
    def __init__(self,path):
        super().__init__();self.front_photo=QPixmap(str(path));self.top_photo=QPixmap(str(path.with_name('v1-top.png')))
        self.photo=self.front_photo;self.view_index=0;self.state=None;self.profile=None;self.points={};self.hit_rects={};self.hover_key=None
        self.setMinimumSize(320,240);self.setMouseTracking(True)
        self.setToolTip('Click a physical control marker to learn its input. Illustration: original V1 control layout.\nLive overlays show measured input; the layout illustration is static.')
    def set_view(self,index):
        self.view_index=index;self.photo=self.front_photo if index==0 else self.top_photo
        self.points={};self.hit_rects={};self.hover_key=None;self.update()
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(),QColor('#0d1118'))
        crop=QRectF(675,140,1000,1040) if self.view_index==0 else QRectF(630,310,1060,800)
        scale=min((self.width()-24)/crop.width(),(self.height()-34)/crop.height())
        ox=(self.width()-crop.width()*scale)/2;oy=(self.height()-crop.height()*scale)/2
        p.drawPixmap(QRectF(ox,oy,crop.width()*scale,crop.height()*scale),self.photo,crop)
        def point(x,y):return QPointF(ox+(x-crop.x())*scale,oy+(y-crop.y())*scale)
        self.points={};self.hit_rects={}
        p.setFont(QFont('Segoe UI',8))
        coords=FRONT_POINTS if self.view_index==0 else {key:xy for key,(_,xy) in REGIONS.items() if key!='trigger' and not key.startswith(('front_','slider_end_'))}
        coords=dict(coords)
        # Compact dots follow each lever's track in the selected illustration.
        # Numbered identities remain editable without changing game bindings.
        for lever,numbers in [('lever_left',(9,10)),('lever_right',(11,12))]:
            x,y=coords[lever]
            coords[f'slider_end_{numbers[0]}']=(x,y-65)
            coords[f'slider_end_{numbers[1]}']=(x,y+115)
        # A learned symbol and its numbered legacy alias represent one button.
        front_positions={slot:coords.pop(slot) for slot in ('system_xbox','system_view','system_menu','system_capture')}
        if self.view_index==0:
            # The face-on illustration foreshortens this cluster. Spread the four
            # targets slightly, keeping short leaders to their actual buttons.
            cx,cy=front_positions['system_xbox']
            offsets={'system_xbox':(0,9),'system_view':(-23,27),'system_menu':(23,27),'system_capture':(0,45)}
            for slot,(dx,dy) in offsets.items():
                anchor=point(*front_positions[slot]);xy=(cx+dx/scale,cy+dy/scale)
                p.setPen(QPen(QColor('#02070c'),3));p.drawLine(anchor,point(*xy))
                p.setPen(QPen(QColor('#00e5ff'),1));p.drawLine(anchor,point(*xy))
                front_positions[slot]=xy
        for slot,key in front_marker_slots((self.profile or {}).get('physical',{})).items():
            coords[key]=front_positions[slot]
        anchor=(1220,635) if self.view_index else (1200,420)
        coords['trigger']=(1405,635) if self.view_index else (1390,420)
        p.setPen(QPen(QColor('#050a10'),4));p.drawLine(point(*coords['trigger']),point(*anchor))
        p.setPen(QPen(QColor('#00e5ff'),1.5));p.drawLine(point(*coords['trigger']),point(*anchor))
        if self.profile and self.state:
            physical=self.profile.get('physical',{})
            h2=point(*coords['H2'])
            h2x=source_value(physical.get('H2_x'),self.state)
            h2y=source_value(physical.get('H2_y'),self.state)
            p.setPen(QPen(QColor('#bd93fa'),3));p.drawLine(h2,QPointF(h2.x()+h2x*16,h2.y()-h2y*16))
            if self.state.get('hats'):
                hx,hy=self.state['hats'][0];hat=point(*coords['H1'])
                p.setPen(QPen(QColor('#007f70'),3));p.drawLine(hat,QPointF(hat.x()+hx*14,hat.y()-hy*14))
            # Motion vectors stay anchored on the real V1; no falsely animated photograph.
            roll=source_value(physical.get('roll'),self.state);pitch=source_value(physical.get('pitch'),self.state)
            if self.profile.get('calibration_version')==1:pitch=-pitch
            center=point(*coords['roll']);end=QPointF(center.x()+roll*65,center.y()+pitch*65)
            p.setPen(QPen(QColor('#64a8ff'),3));p.drawLine(center,end);p.setBrush(QColor('#64a8ff'));p.drawEllipse(end,5,5)
            for key in ('lever_left','lever_right'):
                x,y=coords[key]
                value=source_value(physical.get(key),self.state)
                a=point(x,y-35);b=point(x,y+85)
                p.setPen(QPen(QColor('#344052'),6));p.drawLine(a,b)
                end=QPointF(b.x()+(a.x()-b.x())*value,b.y()+(a.y()-b.y())*value)
                p.setPen(QPen(QColor('#f3b657'),6));p.drawLine(b,end)
            twist=source_value(physical.get('twist'),self.state)
            p.setPen(QPen(QColor('#c57a14'),3));p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawArc(QRectF(center.x()-38,center.y()-18,76,36),90*16,int(-twist*150*16))
        for key,(x,y) in coords.items():
            # Pitch is already shown by the shared roll/pitch vector. It is
            # not a separate physical button, especially not on the OLED.
            if key in ('pitch','twist'):continue
            src=(self.profile or {}).get('physical',{}).get(key)
            if key.startswith('system_') and not src:continue
            pos=point(x,y);self.points[key]=pos
            value=source_value(src,self.state)
            if key=='H2':value=max(abs(value),abs(source_value((self.profile or {}).get('physical',{}).get('H2_x'),self.state)),abs(source_value((self.profile or {}).get('physical',{}).get('H2_y'),self.state)))
            if key=='roll':
                physical=(self.profile or {}).get('physical',{})
                value=max(abs(value),abs(source_value(physical.get('pitch'),self.state)),abs(source_value(physical.get('twist'),self.state)))
            active=abs(value)>.1
            # Opaque dark backing and a bright ring remain readable against
            # both dark plastic and the photograph's silver highlights.
            compact=key.startswith(('slider_end_','front_')) or key=='trigger'
            radius=7 if compact else 8
            hovered=key==self.hover_key
            color=QColor('#ffffff' if hovered else '#a5ff60' if active else '#00e5ff')
            if active or hovered:
                halo=QColor('#a5ff60' if active else '#00e5ff');halo.setAlpha(100)
                p.setPen(QPen(halo,5));p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(pos,radius+3,radius+3)
            p.setPen(QPen(QColor('#02070c'),6));p.setBrush(QColor(4,17,25,235))
            p.drawEllipse(pos,radius,radius)
            p.setPen(QPen(color,2.5));p.drawEllipse(pos,radius,radius)
            p.setPen(Qt.PenStyle.NoPen);p.setBrush(QColor('#a5ff60') if active else color)
            p.drawEllipse(pos,2.5,2.5)
            self.hit_rects[key]=QRectF(pos.x()-14,pos.y()-14,28,28)
    def control_at(self,pos):
        if not self.points:return None
        key=min(self.points,key=lambda k:(self.points[k].x()-pos.x())**2+(self.points[k].y()-pos.y())**2)
        distance=(self.points[key].x()-pos.x())**2+(self.points[key].y()-pos.y())**2
        return key if distance<=18**2 else None
    def mousePressEvent(self,event):
        key=self.control_at(event.position())
        if key is not None:self.selected.emit(key)
    def mouseMoveEvent(self,event):
        key=self.control_at(event.position())
        if key!=self.hover_key:self.hover_key=key;self.update()
        self.setCursor(Qt.CursorShape.PointingHandCursor if key is not None else Qt.CursorShape.ArrowCursor)
        if key is not None:
            if key=='roll':
                physical=(self.profile or {}).get('physical',{})
                self.setToolTip('Stick movement / twist\n'+'\n'.join(name+': '+source_text(physical.get(name)) for name in ('roll','pitch','twist'))+'\nMove: pitch/roll vector • Twist: rotation arc.')
            else:self.setToolTip(REGIONS[key][0]+' • '+source_text((self.profile or {}).get('physical',{}).get(key))+'\nClick to edit. Cyan: clickable • Green: active • White: hover.')
        else:self.setToolTip('Original VelocityOne V1 • Bright cyan dots are clickable assignments.')
    def leaveEvent(self,event):
        self.hover_key=None;self.setCursor(Qt.CursorShape.ArrowCursor);self.update()
        super().leaveEvent(event)

class AxisMeter(QWidget):
    def __init__(self):super().__init__();self.values=[];self.setMinimumHeight(36)
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);p.setFont(QFont('Segoe UI',8))
        n=max(1,len(self.values));w=self.width()/n
        for i,v in enumerate(self.values):
            x=i*w+6;p.setPen(QColor('#a5b6ca'));p.drawText(QRectF(x,0,w-12,20),Qt.AlignmentFlag.AlignCenter,f'Axis {i+1}  {v:+.2f}')
            r=QRectF(x,26,w-12,8);p.setPen(Qt.PenStyle.NoPen);p.setBrush(QColor('#293848'));p.drawRoundedRect(r,4,4)
            p.setBrush(QColor('#42c9be'));p.drawRoundedRect(QRectF(x,26,max(1,(v+1)/2*(w-12)),8),4,4)


class ButtonMonitor(QWidget):
    """Full-width raw input tiles; disconnected inputs never retain a pressed state."""
    def __init__(self,parent=None):
        super().__init__(parent)
        self.values=[]
        self.setMinimumHeight(34)
        self.setToolTip('Physical button numbers reported by the Flightstick. Green means pressed.')
    def set_values(self,values):
        self.values=list(values) if values is not None else []
        self._fit_height()
        self.update()
    def _fit_height(self):
        count=max(24,len(self.values))
        columns=max(1,min(count,self.width()//42))
        self.setFixedHeight(((count+columns-1)//columns)*34)
    def resizeEvent(self,event):
        super().resizeEvent(event)
        self._fit_height()
    def paintEvent(self,event):
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        count=max(24,len(self.values))
        columns=max(1,min(count,self.width()//42))
        width=self.width()/columns
        painter.setFont(QFont('Segoe UI',10,QFont.Weight.Bold))
        for index in range(count):
            available=index<len(self.values)
            pressed=available and bool(self.values[index])
            rect=QRectF((index%columns)*width+3,(index//columns)*34+3,width-6,28)
            fill='#a5ff60' if pressed else '#172434' if available else '#111820'
            border='#caff9d' if pressed else '#6485a4' if available else '#344250'
            ink='#091306' if pressed else '#e5f2ff' if available else '#718092'
            painter.setBrush(QColor(fill))
            painter.setPen(QPen(QColor(border),2 if pressed else 1.5))
            painter.drawRoundedRect(rect,6,6)
            painter.setPen(QColor(ink))
            painter.drawText(rect,Qt.AlignmentFlag.AlignCenter,f'{index+1:02d}')
