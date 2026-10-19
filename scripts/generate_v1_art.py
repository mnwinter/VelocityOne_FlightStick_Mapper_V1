"""Generate original, independently drawn V1 control-layout illustrations.
No manufacturer photographs, tracings, logos or textures are used.
Canvas locations match the app's editable physical-control coordinates.
"""
from pathlib import Path
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'

def illustration(front=False):
    pieces=['''<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="1350" viewBox="0 0 2400 1350">
<defs>
 <linearGradient id="body" x2="0.8" y2="1"><stop stop-color="#38444e"/><stop offset=".45" stop-color="#1f2931"/><stop offset="1" stop-color="#111920"/></linearGradient>
 <linearGradient id="grip" x2="1" y2=".2"><stop stop-color="#0d151c"/><stop offset=".55" stop-color="#33434f"/><stop offset="1" stop-color="#18232b"/></linearGradient>
</defs>
<rect width="2400" height="1350" fill="#0d1118"/>
''']
    def path(d,fill='#1b252e',stroke='#687c8b',width=5):pieces.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round"/>')
    def rect(x,y,w,h,r=9,fill='#141e27',stroke='#526674',sw=3):pieces.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    def ellipse(x,y,rx,ry,fill='#17232b',stroke='#7c8f9a',sw=5):pieces.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    def text(x,y,s,size=15,color='#a8bdcb'):pieces.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="Segoe UI" font-size="{size}" text-anchor="middle">{s}</text>')
    if front:
        path('M718 822 L815 757 L1515 757 L1620 830 L1595 1015 Q1585 1090 1500 1100 L825 1100 Q740 1090 730 1020 Z','url(#body)')
        ellipse(1167,924,220,130,'#0c151d','#8295a0',13)
        ellipse(1167,924,175,102,'#17222a','#e2b657',8)
        path('M1118 929 L1113 328 Q1080 275 1089 219 L1099 158 Q1102 142 1124 142 L1214 142 Q1240 143 1245 164 L1253 228 Q1254 288 1212 332 L1210 931 Q1167 957 1118 929 Z','url(#grip)')
        rect(1106,155,123,188,25,'#263842','#91a5b2',5)
        rect(1120,169,96,30,5,'#0a171b','#48626b',2);text(1168,190,'V1',17,'#6ad8cc')
        for x,y in [(1120,210),(1210,205)]:ellipse(x,y,20,20,'#111a20','#6a8192',4)
        for x,y in [(1117,285),(1213,285)]:ellipse(x,y,16,16,'#0f1b22','#718596',3)
        rect(1154,304,28,37,7,'#131c24','#d4ac58',4)
        path('M1214 585 Q1270 580 1320 623 L1280 672 L1205 659 Z','#1a2831','#607787',4)
        path('M1114 459 L1207 466 L1205 502 L1116 496 Z','#a9bbc4','#314855',3)
        levers=[(810,845),(1512,845)]
        system=[(1168,983),(1123,998),(1213,998),(1168,1010)]
    else:
        path('M739 591 L935 470 L1365 475 L1596 626 L1588 969 Q1582 1032 1515 1068 L1320 1100 L875 1091 Q744 1070 707 970 L698 715 Z','url(#body)')
        ellipse(1160,805,230,206,'#0c151c','#91a2ad',15)
        ellipse(1160,805,192,170,'#20313a','#e0b75a',7)
        ellipse(1160,805,155,139,'#0b151d','#526d7a',3)
        path('M1114 807 L1110 640 Q1065 602 1068 543 L1071 462 Q1073 420 1111 416 L1214 422 Q1257 425 1257 466 L1253 552 Q1252 608 1211 642 L1205 811 Q1160 838 1114 807 Z','url(#grip)')
        rect(1074,436,175,211,26,'#283941','#96aab5',5)
        rect(1098,453,125,49,7,'#08161b','#496572',2);text(1160,485,'V1',24,'#6ad8cc')
        for x,y in [(1108,530),(1208,530)]:ellipse(x,y,24,24,'#0d1921','#8095a5',4)
        for x,y in [(1108,585),(1210,585)]:ellipse(x,y,17,17,'#0d1921','#6e8595',3)
        rect(1145,588,30,42,7,'#101a20','#dab359',4)
        path('M1213 669 Q1300 625 1371 697 L1341 766 L1209 760 Z','#263943','#687e8d',5)
        path('M1110 690 L1210 695 L1208 728 L1112 724 Z','#9caeb7','#3b5664',3)
        levers=[(795,551),(1506,551)]
        for x,numbers in [(814,range(1,5)),(1503,range(5,9))]:
            for y,n in zip((716,783,850,918),numbers):
                rect(x-38,y-25,76,50,9,'#16242d','#7c9bab',3);text(x,y+7,f'B{n}',16,'#d4e4ec')
        system=[(1160,996),(1110,1031),(1209,1031),(1160,1052)]
    for x,y in levers:
        rect(x-31,y-84,62,223,20,'#0d1820','#5c7482',4)
        rect(x-8,y-64,16,180,5,'#e3b35b','#735e39',1)
        path(f'M{x-48} {y-17} L{x+40} {y-24} L{x+49} {y+25} L{x-43} {y+31} Z','#334651','#9babb3',4)
        ellipse(x,y,17,17,'#243741','#e3b45e',4)
    for i,(x,y) in enumerate(system):
        ellipse(x,y,15 if i else 19,13 if i else 17,'#111d25','#a2bbc8',3)
    text(1160,1140,'ORIGINAL V1  /  CONTROL LAYOUT',18,'#688491')
    pieces.append('</svg>');return ''.join(pieces)

if __name__=='__main__':
    from PySide6.QtWidgets import QApplication
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtGui import QImage,QPainter,QFontDatabase
    app=QApplication([])
    if os.name=='nt':
        for font in ('segoeui.ttf','segoeuib.ttf'):QFontDatabase.addApplicationFont(str(Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'/font))
    ASSETS.mkdir(parents=True,exist_ok=True)
    for name,front in [('v1-front',True),('v1-top',False)]:
        svg=ASSETS/(name+'.svg');svg.write_text(illustration(front),encoding='utf-8')
        renderer=QSvgRenderer(str(svg));assert renderer.isValid()
        im=QImage(2400,1350,QImage.Format.Format_ARGB32);im.fill(0)
        painter=QPainter(im);renderer.render(painter);painter.end();assert im.save(str(ASSETS/(name+'.png')))
    print('Original V1 schematic SVG/PNG assets generated')
