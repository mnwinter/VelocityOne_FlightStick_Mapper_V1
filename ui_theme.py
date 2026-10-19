"""Shared visual language. Color reinforces the written section labels."""

STYLE = '''
QMainWindow,QDialog{background:#edf1f6;color:#203047;font-family:"Segoe UI";font-size:13px}
QWidget{font-family:"Segoe UI";font-size:13px;color:#203047}
QLabel#muted{color:#596b80;font-size:12px}
QLabel#title{font-size:27px;font-weight:700;color:#172a40}
QLabel#eyebrow{font-size:11px;font-weight:700;color:#247f80;letter-spacing:1px}
QLabel#sectionTitle{font-size:15px;font-weight:700;color:#203047}
QLabel#axisHeading{color:#225fba;font-size:12px;font-weight:700}
QLabel#triggerHeading{color:#946006;font-size:12px;font-weight:700}
QLabel#buttonHeading{color:#7545b5;font-size:12px;font-weight:700}
QFrame#physicalCard,QFrame#mappingCard,QFrame#rawCard{background:white;border:1px solid #d8e0eb;border-radius:12px}
QFrame#physicalCard{border-top:3px solid #159c95}
QFrame#mappingCard{border-top:3px solid #8459c9}
QFrame#rawCard{border-top:3px solid #159c95}
QFrame#axisGroup{background:#f0f6ff;border:1px solid #cdddf6;border-radius:9px}
QFrame#triggerGroup{background:#fff8ea;border:1px solid #eddbb2;border-radius:9px}
QFrame#buttonGroup{background:#f6f1ff;border:1px solid #ded0f3;border-radius:9px}
QFrame#previewGroup{background:#eef8f2;border:1px solid #cae3d2;border-radius:9px}
QFrame#sidebar{background:#172a40;border:1px solid #172a40;border-radius:14px}
QFrame#navGroup{background:#22384f;border:1px solid #354b63;border-radius:9px}
QFrame#sidebar QLabel{color:#f1f5fb}
QFrame#sidebar QLabel#muted{color:#bac9da;font-size:12px}
QFrame#sidebar QLabel#eyebrow{color:#9cb5cf;font-size:11px;letter-spacing:1px}
QFrame#sidebar QLabel#brand{color:white;font-size:23px;font-weight:700}
QFrame#sidebar QPushButton{background:#304960;color:#f7faff;border:1px solid #48617a}
QFrame#sidebar QPushButton:hover{background:#3c5874;border-color:#7f9fbe}
QFrame#sidebar QLineEdit,QFrame#sidebar QComboBox{background:#122337;color:white;border:1px solid #4e6680}
QFrame#sidebar QComboBox QAbstractItemView{background:white;color:#203047;selection-background-color:#dceaf9}
QPushButton{background:white;border:1px solid #cbd6e3;border-radius:6px;padding:8px 10px;font-weight:550}
QPushButton:hover{background:#eaf1fa;border-color:#7e9fcb}
QPushButton:disabled{background:#e7edf2;color:#8a9bae;border-color:#d7e0e9}
QPushButton#primary,QFrame#sidebar QPushButton#primary{background:#16825f;color:white;border:1px solid #249776;padding:10px 12px}
QPushButton#stop,QFrame#sidebar QPushButton#stop{background:#943d4d;color:white;border:1px solid #b65c6d;padding:10px 12px}
QPushButton#clear{background:transparent;color:#75879d;border:0;padding:4px;font-size:17px}
QPushButton#clear:hover{background:#fbe9ec;color:#963e52}
QComboBox,QLineEdit,QSpinBox,QDoubleSpinBox{background:white;border:1px solid #c6d3e2;border-radius:5px;padding:7px;selection-background-color:#d2e4fa}
QTabWidget::pane{border:0;background:white}
QTabBar::tab{padding:10px 12px;background:#edf0f6;color:#5b6b81;border-bottom:3px solid transparent}
QTabBar::tab:selected{background:#f4effc;color:#7144ab;border-bottom:3px solid #8459c9;font-weight:650}
QScrollArea{border:0;background:transparent}
QScrollArea>QWidget>QWidget{background:white}
QScrollBar:vertical{background:#eff2f6;width:9px;border-radius:4px}
QScrollBar::handle:vertical{background:#bfcbda;border-radius:4px;min-height:28px}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0}
QToolTip{background:#172a40;color:white;border:0;padding:7px}
QLabel#badge{background:#e0f2ec;color:#116b55;border:1px solid #b8dfd0;border-radius:6px;padding:8px 12px;font-weight:650}
QLabel#notice{background:#fff8e8;color:#815b16;border:1px solid #eedcae;border-radius:7px;padding:9px 12px;font-size:12px}
QLabel#status{background:#e5ebf2;color:#435c78;border:1px solid #cdd8e5;border-radius:6px;padding:9px;font-size:12px}
'''

# The same components retain their semantic accents in the black theme.
STYLE += '''
QMainWindow,QDialog{background:#080b10;color:#dce5f2}
QWidget{color:#dce5f2}
QLabel#muted{color:#9daec4}
QLabel#title{color:#f0f5fc}
QLabel#eyebrow{color:#51cfc4}
QLabel#sectionTitle{color:#eef3fb}
QLabel#axisHeading{color:#79b4ff}
QLabel#triggerHeading{color:#f3bf6b}
QLabel#buttonHeading{color:#c2a0ff}
QFrame#physicalCard,QFrame#mappingCard,QFrame#rawCard{background:#11161e;border-color:#2b3543}
QFrame#physicalCard,QFrame#rawCard{border-top:3px solid #36bfb5}
QFrame#mappingCard{border-top:3px solid #a07ae6}
QFrame#axisGroup{background:#111f32;border-color:#2e4c73}
QFrame#triggerGroup{background:#292116;border-color:#66502b}
QFrame#buttonGroup{background:#221b32;border-color:#503b70}
QFrame#previewGroup{background:#14251e;border-color:#2a5040}
QFrame#sidebar{background:#0e131b;border-color:#293341}
QFrame#navGroup{background:#171f2b;border-color:#303e50}
QFrame#sidebar QLabel#muted{color:#a5b6cc}
QFrame#sidebar QLabel#eyebrow{color:#91a7c3}
QFrame#sidebar QPushButton{background:#232e3d;color:#e6edf8;border-color:#3a4b62}
QFrame#sidebar QPushButton:hover{background:#30415a;border-color:#6885aa}
QFrame#sidebar QLineEdit,QFrame#sidebar QComboBox{background:#0c1119;color:#e3ecfa;border-color:#3b4c64}
QPushButton{background:#192331;color:#dce8f9;border-color:#354960}
QPushButton:hover{background:#273c57;border-color:#6794ce}
QPushButton:disabled{background:#171d26;color:#6d7c90;border-color:#2b3542}
QPushButton#clear{background:transparent;color:#a3b0c4;border:0}
QPushButton#clear:hover{background:#452632;color:#ff9bb1}
QPushButton#primary,QFrame#sidebar QPushButton#primary{background:#146c50;color:#dcfff1;border-color:#2b9977}
QPushButton#stop,QFrame#sidebar QPushButton#stop{background:#793244;color:#ffe8ed;border-color:#aa5168}
QComboBox,QLineEdit,QSpinBox,QDoubleSpinBox{background:#101721;color:#e5edf9;border-color:#3c4b61;selection-background-color:#315c92}
QComboBox QAbstractItemView,QFrame#sidebar QComboBox QAbstractItemView{background:#192332;color:#edf4ff;selection-background-color:#34537b}
QTabWidget::pane{background:#11161e}
QTabBar::tab{background:#1a2331;color:#a4b4ca;border-bottom:3px solid transparent}
QTabBar::tab:selected{background:#2b2140;color:#d4baff;border-bottom:3px solid #a17be7}
QScrollArea>QWidget>QWidget{background:#11161e}
QScrollBar:vertical{background:#151d28}
QScrollBar::handle:vertical{background:#43546c}
QToolTip{background:#25354c;color:#f3f7ff;border:1px solid #5c7595}
QLabel#badge{background:#102e28;color:#73ded1;border-color:#286154}
QLabel#notice{background:#292314;color:#e1c17e;border-color:#5b4b27}
QLabel#status{background:#171e28;color:#a5b6ca;border-color:#303c4d}
QCheckBox{color:#dce5f2;spacing:8px}
QCheckBox::indicator{width:16px;height:16px;border:1px solid #647c9c;background:#101721;border-radius:3px}
QCheckBox::indicator:checked{background:#49b9ac;border-color:#7bdfd3}
'''

STYLE += """
QWidget{font-size:14px}
QLabel#muted{font-size:12px}
QLabel#eyebrow,QLabel#axisHeading,QLabel#triggerHeading,QLabel#buttonHeading{font-size:12px;letter-spacing:0.5px}
QLabel#sectionTitle{font-size:17px}
QPushButton{padding:8px 9px}
QFrame#axisGroup{border-top:3px solid #79b4ff}
QFrame#triggerGroup{border-top:3px solid #e3ad54}
QFrame#buttonGroup{border-top:3px solid #a785e2}
QScrollArea>QWidget>QWidget{background:#080b10}
QSplitter::handle{background:#080b10}
"""

STYLE += "QPushButton{padding:6px 9px}"

STYLE += """
QListWidget,QTableWidget{background:#101720;color:#e3ecfa;border:1px solid #34465e;border-radius:6px;selection-background-color:#274e73;selection-color:#f1f8ff;outline:0}
QListWidget::item{padding:6px;border-bottom:1px solid #1c2a3b}
QListWidget::item:selected{background:#254660;color:#ecfaff}
QTableWidget::item{padding:7px;border:0}
QTableWidget{gridline-color:#2c3b50}
QHeaderView::section{background:#1b293c;color:#a9c5e8;border:0;border-right:1px solid #34465e;border-bottom:1px solid #34465e;padding:8px;font-weight:600}
QTableCornerButton::section{background:#1b293c;border:0}
QListView::indicator{width:16px;height:16px;border:1px solid #6782a4;border-radius:3px;background:#101720}
QListView::indicator:checked{background:#38aa9e;border-color:#89e7db}
"""


# Live assignment feedback overrides hover so a held input remains unmistakable.
STYLE += """
QPushButton[liveActive="true"],QPushButton[liveActive="true"]:hover{
    background:#a5ff60;color:#091306;border:1px solid #caff9d;font-weight:700;
}
"""


STYLE += """
QWidget{font-size:12px}
QLabel#title{font-size:23px}
QLabel#sectionTitle{font-size:15px}
QLabel#eyebrow,QLabel#axisHeading,QLabel#triggerHeading,QLabel#buttonHeading{font-size:11px}
QPushButton{padding:4px 6px}
QComboBox,QLineEdit,QSpinBox,QDoubleSpinBox{padding:4px}
QLineEdit#actionName{background:transparent;border:1px solid transparent;border-radius:3px;padding:1px 3px;color:#dce8f9;font-weight:600}
QLineEdit#actionName:hover{border-color:#4a627d;background:#101721}
QLineEdit#actionName:focus{border-color:#51cfc4;background:#101721}
QLabel#notice{padding:4px 8px;font-size:11px}
QLabel#badge{padding:5px 8px}
QMenuBar{background:#111820;color:#dae6f7;border-bottom:1px solid #304154;spacing:8px}
QMenuBar::item{padding:5px 12px;background:transparent}
QMenuBar::item:selected{background:#29425e}
QMenu{background:#162130;color:#e5eefb;border:1px solid #3c536d;padding:5px}
QMenu::item{padding:6px 28px 6px 12px}
QMenu::item:selected{background:#2d4f70}
QMenu::separator{height:1px;background:#35485e;margin:4px}
"""

STYLE += """
QPushButton#primary,QPushButton#stop{padding:5px 8px}
QLineEdit#actionName{font-size:11px;padding:0px 2px}
"""
