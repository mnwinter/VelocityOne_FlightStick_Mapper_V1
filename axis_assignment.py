"""Clickable assignment slots with proportional, evaluated output meters."""
import math
from PySide6.QtCore import Qt,QRectF
from PySide6.QtGui import QPainter,QPainterPath,QColor,QPen
from PySide6.QtWidgets import QPushButton

def axis_fill_interval(value,signed):
    value=float(value)
    if not math.isfinite(value):value=0.
    if signed:
        end=(max(-1.,min(1.,value))+1)/2
        return min(.5,end),max(.5,end)
    return 0.,max(0.,min(1.,value))

class AxisAssignmentButton(QPushButton):
    def __init__(self,text='',parent=None):
        super().__init__(text,parent);self.live_value=None;self.signed=True
    def set_live_value(self,value,signed=True):
        if self.live_value==value and self.signed==signed:return
        self.live_value=value;self.signed=signed;self.update()
    def paintEvent(self,event):
        if self.live_value is None:return super().paintEvent(event)
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r=QRectF(self.rect()).adjusted(1,1,-1,-1)
        path=QPainterPath();path.addRoundedRect(r,5,5)
        p.fillPath(path,QColor('#192331'))
        start,end=axis_fill_interval(self.live_value,self.signed)
        p.save();p.setClipPath(path)
        p.fillRect(QRectF(r.left()+r.width()*start,r.top(),r.width()*(end-start),r.height()),QColor('#23754f'))
        p.restore()
        if self.signed:
            p.setPen(QPen(QColor('#74909a'),1));p.drawLine(int(r.center().x()),int(r.top()+2),int(r.center().x()),int(r.bottom()-2))
        active=end-start>.0005
        border='#b1d3ff' if self.underMouse() or self.hasFocus() else '#60cc91' if active else '#354960'
        p.setPen(QPen(QColor(border),1));p.drawPath(path)
        font=self.font();font.setBold(active);p.setFont(font);p.setPen(QColor('#f0f6ff'))
        text=p.fontMetrics().elidedText(self.text(),Qt.TextElideMode.ElideMiddle,int(r.width()-10))
        p.drawText(r.adjusted(5,0,-5,0),Qt.AlignmentFlag.AlignCenter,text)
