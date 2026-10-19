"""Xbox control glyphs painted as vectors, without font-specific symbol fallbacks."""
from PySide6.QtCore import Qt,QRectF,QPointF
from PySide6.QtGui import QPainter,QColor,QPen,QFont
from PySide6.QtWidgets import QWidget

class XboxSymbol(QWidget):
    def __init__(self,target,parent=None):
        super().__init__(parent);self.target=target;self.setFixedSize(30,20)
        self.setToolTip('Xbox '+target);self.setAccessibleName('Xbox '+target)
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);p.scale(30/36,20/26)
        p.setPen(QPen(QColor('#e3edf9'),1.6));p.setBrush(QColor('#111820'))
        p.setFont(QFont('Segoe UI',9,QFont.Weight.Bold));t=self.target;r=QRectF(2,2,31,22)
        if t in ('A','B','X','Y'):
            p.drawEllipse(QRectF(6,2,22,22))
            p.setPen(QColor(dict(A='#7be344',B='#ff6269',X='#5caeff',Y='#ffd450')[t]))
            p.drawText(r,Qt.AlignmentFlag.AlignCenter,t)
        elif t in ('LT','RT','LB','RB'):
            p.drawRoundedRect(r,5,5);p.drawText(r,Qt.AlignmentFlag.AlignCenter,t)
        elif t in ('Menu','View','Guide'):
            p.drawEllipse(QRectF(6,2,22,22))
            if t=='Menu':
                for y in (9,13,17):p.drawLine(12,y,22,y)
            elif t=='View':
                p.drawRect(11,8,8,7);p.drawRect(15,11,8,7)
            else:
                p.drawLine(11,7,23,19);p.drawLine(23,7,11,19)
        elif t in ('Up','Down','Left','Right'):
            p.drawRoundedRect(QRectF(13,3,8,20),1,1);p.drawRoundedRect(QRectF(7,9,20,8),1,1)
            p.setPen(Qt.PenStyle.NoPen);p.setBrush(QColor('#f2f7ff'))
            x,y={'Up':(17,6),'Down':(17,20),'Left':(10,13),'Right':(24,13)}[t]
            p.drawEllipse(QPointF(x,y),3,3)
        else:
            # L/R stick glyph with an axis arrow, or press indicator for L3/R3.
            p.drawEllipse(QRectF(6,2,22,22));p.drawText(QRectF(6,2,22,22),Qt.AlignmentFlag.AlignCenter,'L' if t.startswith('L') else 'R')
            if t.endswith('X'):
                p.drawLine(1,13,5,13);p.drawLine(29,13,35,13)
            elif t.endswith('Y'):
                p.drawLine(17,0,17,3);p.drawLine(17,23,17,26)
            else:
                p.drawLine(29,3,33,7);p.drawLine(29,7,33,7);p.drawLine(33,3,33,7)
