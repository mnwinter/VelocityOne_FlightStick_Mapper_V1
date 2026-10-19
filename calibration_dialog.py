"""Guided physical identification. Changes commit only when Apply is pressed."""
import time
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QDialog,QVBoxLayout,QLabel,QPushButton,QCheckBox,QDialogButtonBox
from calibration import CalibrationSession
from widgets import source_text

STEPS=[
 ('Main stick — roll','Center the main stick.','Move the main stick directly RIGHT.'),
 ('Main stick — pitch','Center the main stick.','Push the main stick directly FORWARD.'),
 ('Main stick — twist','Center the twist axis.','Twist the grip CLOCKWISE.'),
 ('Left base lever — throttle','Move the LEFT lever fully BACK before clicking Capture.','Move only the LEFT lever fully FORWARD.'),
 ('Right base lever — brake','Move the RIGHT lever fully BACK before clicking Capture.','Move only the RIGHT lever fully FORWARD.'),
 ('Right hat H2 — horizontal','Release H2 to its center.','Move the RIGHT hat directly RIGHT.'),
 ('Right hat H2 — vertical','Release H2 to its center.','Move the RIGHT hat directly UP.')]

class CalibrationDialog(QDialog):
    def __init__(self,provider,parent=None):
        super().__init__(parent);self.setWindowTitle('Identify original V1 controls');self.setMinimumSize(560,610)
        self.provider=provider;self.session=CalibrationSession();self.index=0;self.listening=False;self.deadline=0
        box=QVBoxLayout(self);box.setSpacing(14)
        title=QLabel('Identify your physical V1 controls');title.setObjectName('title');box.addWidget(title)
        intro=QLabel('Seven short captures measure the actual input order and direction.\nKeep every other control still. Nothing is applied until you finish.');intro.setWordWrap(True);box.addWidget(intro)
        self.step_label=QLabel();self.step_label.setObjectName('axisHeading');box.addWidget(self.step_label)
        self.start_label=QLabel();self.start_label.setWordWrap(True);box.addWidget(self.start_label)
        self.move_label=QLabel();self.move_label.setObjectName('notice');self.move_label.setWordWrap(True);box.addWidget(self.move_label)
        self.status=QLabel();self.status.setWordWrap(True);box.addWidget(self.status)
        self.capture=QPushButton('Capture movement');self.capture.clicked.connect(self.begin);box.addWidget(self.capture)
        self.next=QPushButton('Next control');self.next.setEnabled(False);self.next.clicked.connect(self.advance);box.addWidget(self.next)
        self.summary=QLabel();self.summary.setWordWrap(True);self.summary.setObjectName('muted');box.addWidget(self.summary,1)
        self.standard=QCheckBox('Set standard gamepad axes and triggers (replaces six assignments)');self.standard.setChecked(True);box.addWidget(self.standard)
        note=QLabel('Standard: main stick → LX/LY, left lever → RT, right lever → LT, H2 → RX/RY.\nButton bindings and the LT + RT combo are preserved.');note.setWordWrap(True);note.setObjectName('muted');box.addWidget(note)
        self.buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Apply|QDialogButtonBox.StandardButton.Cancel)
        self.apply_button=self.buttons.button(QDialogButtonBox.StandardButton.Apply);self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.accept);self.buttons.rejected.connect(self.reject);box.addWidget(self.buttons)
        self.timer=QTimer(self);self.timer.timeout.connect(self.tick);self.timer.start(20);self.show_step()
        self.finished.connect(self.timer.stop)
    def exec(self):
        try:return super().exec()
        finally:
            self.timer.stop()
            self.deleteLater()
    def show_step(self):
        name,start,move=STEPS[self.index];self.step_label.setText(f'STEP {self.index+1} / 7  •  {name}')
        self.start_label.setText(start);self.move_label.setText(move);self.status.setText('Place the control at its start position, then click Capture.')
        self.next.setEnabled(False);self.capture.setEnabled(True);self.capture.setText('Capture movement')
    def begin(self):
        try:self.session.begin(self.index,self.provider())
        except ValueError as e:self.status.setText(str(e));return
        self.listening=True;self.deadline=time.monotonic()+15;self.next.setEnabled(False)
        self.apply_button.setEnabled(False)
        self.status.setText('Listening… '+STEPS[self.index][2]);self.capture.setText('Restart capture')
    def tick(self):
        if not self.listening:return
        s=self.provider()
        if s is None or time.monotonic()>self.deadline:
            self.listening=False;self.status.setText('No capture. Reconnect if needed, reset the control and Capture again.');return
        if self.session.observe(s):
            self.listening=False;self.status.setText(self.session.message);self.next.setEnabled(True)
            self.summary.setText('\n'.join(STEPS[CalibrationSession.keys.index(k)][0]+': '+source_text(v) for k,v in self.session.sources.items()))
            if self.index==6:
                self.next.setEnabled(False);self.capture.setText('Recapture vertical H2');self.apply_button.setEnabled(True)
                self.status.setText(self.session.message+'\nAll controls identified. Review the results, then Apply.')
        elif self.session.message!='Listening for one axis…':self.status.setText(self.session.message)
    def advance(self):
        self.index+=1;self.show_step()
