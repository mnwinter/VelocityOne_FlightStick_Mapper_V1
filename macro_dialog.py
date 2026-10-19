"""Profile-scoped macro editor. Editing never sends game or desktop input."""
import copy
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QFormLayout,QLabel,QPushButton,
 QListWidget,QListWidgetItem,QLineEdit,QComboBox,QSpinBox,QTableWidget,QTableWidgetItem,
 QHeaderView,QDialogButtonBox,QMessageBox,QAbstractItemView,QSplitter,QWidget)
from macros import validate_macros,PAD_OUTPUTS
from widgets import SourceDialog,source_text

class MacroDialog(QDialog):
 def __init__(self,macros,provider,keys,parent=None):
  super().__init__(parent);self.setWindowTitle('Flightstick macros • sequences & simultaneous presses')
  self.resize(1140,800);self.setMinimumSize(960,690)
  self.macros=copy.deepcopy(macros);self.provider=provider;self.keys=keys;self.current=-1
  self.source=None;self.loading=False
  outer=QVBoxLayout(self);outer.setSpacing(12)
  title=QLabel('Macro workshop');title.setObjectName('title');outer.addWidget(title)
  help=QLabel('Build steps in order. Outputs in the same step press together, hold for the duration, then release.\nDelay after = a pause before the next step. An empty output step is a timed pause. Stop output cancels every macro.')
  help.setWordWrap(True);help.setObjectName('muted');outer.addWidget(help)
  split=QSplitter();outer.addWidget(split,1)
  left=QWidget();ll=QVBoxLayout(left);ll.setContentsMargins(0,0,12,0)
  ll.addWidget(QLabel('SAVED MACROS IN THIS PROFILE'))
  self.list=QListWidget();ll.addWidget(self.list)
  row=QHBoxLayout()
  for text,fn in [('New macro',self.add_macro),('Delete',self.remove_macro)]:
   b=QPushButton(text);b.clicked.connect(fn);row.addWidget(b)
  ll.addLayout(row);split.addWidget(left)
  right=QWidget();rl=QVBoxLayout(right);rl.setContentsMargins(12,0,0,0)
  form=QFormLayout();self.name=QLineEdit();form.addRow('Macro name',self.name)
  self.assign=QPushButton('Assign flightstick button…');self.assign.clicked.connect(self.assign_source);form.addRow('Physical trigger',self.assign)
  settings=QHBoxLayout();self.trigger=QComboBox();self.trigger.addItem('On press','press');self.trigger.addItem('On release','release')
  self.repeat=QComboBox()
  for text,value in [('Run once','once'),('Repeat count','count'),('Repeat while held','held'),('Toggle repeating','toggle')]:self.repeat.addItem(text,value)
  settings.addWidget(self.trigger);settings.addWidget(self.repeat);form.addRow('Run behavior',settings)
  timings=QHBoxLayout();self.count=QSpinBox();self.count.setRange(1,999);self.gap=QSpinBox();self.gap.setRange(40,600000);self.gap.setSuffix(' ms');self.gap.setValue(100)
  timings.addWidget(QLabel('Count'));timings.addWidget(self.count);timings.addWidget(QLabel('Pause between repeats'));timings.addWidget(self.gap);form.addRow('',timings)
  rl.addLayout(form)
  self.table=QTableWidget(0,3);self.table.setHorizontalHeaderLabels(['Simultaneous outputs','Hold / pause','Delay after'])
  self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
  self.table.setColumnWidth(1,130);self.table.setColumnWidth(2,130)
  self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
  self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
  self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
  rl.addWidget(self.table,1)
  tools=QHBoxLayout()
  for text,fn in [('Add step',lambda:self.step_editor()),('Edit step',self.edit_step),('Remove',self.remove_step),('↑',lambda:self.move_step(-1)),('↓',lambda:self.move_step(1))]:
   b=QPushButton(text);b.clicked.connect(fn);tools.addWidget(b)
  rl.addLayout(tools)
  note=QLabel('Keyboard and mouse macro outputs work in either output mode. Xbox outputs require Xbox gamepad mode.\nPressing a running macro again restarts it; toggle mode stops it. Ordinary bindings remain active alongside macros.\nTiming follows the output worker; this is not a real-time motion controller.')
  note.setWordWrap(True);note.setObjectName('muted');rl.addWidget(note)
  split.addWidget(right);split.setSizes([260,840])
  buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel)
  buttons.accepted.connect(self.save);buttons.rejected.connect(self.reject);outer.addWidget(buttons)
  self.list.currentRowChanged.connect(self.select_macro)
  self.name.textChanged.connect(self.store);self.trigger.currentIndexChanged.connect(self.behavior_changed);self.repeat.currentIndexChanged.connect(self.behavior_changed)
  self.count.valueChanged.connect(self.store);self.gap.valueChanged.connect(self.store)
  self.refresh_list()
 def refresh_list(self,selected=0):
  self.loading=True;self.list.clear()
  for m in self.macros:self.list.addItem(m['name'])
  self.current=-1;self.loading=False
  if self.macros:self.list.setCurrentRow(min(selected,len(self.macros)-1))
  else:self.select_macro(-1)
 def select_macro(self,index):
  self.current=index;self.loading=True;valid=0<=index<len(self.macros)
  for w in (self.name,self.assign,self.trigger,self.repeat,self.count,self.gap,self.table):w.setEnabled(valid)
  self.table.setRowCount(0)
  if valid:
   m=self.macros[index];self.source=copy.deepcopy(m['source']);self.name.setText(m['name']);self.assign.setText(source_text(self.source)+' • Change / learn…')
   self.trigger.setCurrentIndex(self.trigger.findData(m['trigger']));self.repeat.setCurrentIndex(self.repeat.findData(m['repeat']))
   self.count.setValue(m['count']);self.gap.setValue(m['gap_ms']);self.show_steps()
  else:self.name.clear();self.assign.setText('Add a macro to begin');self.source=None
  self.loading=False;self.update_enabled()
 def update_enabled(self):
  valid=self.current>=0;self.count.setEnabled(valid and self.repeat.currentData()=='count');self.gap.setEnabled(valid and self.repeat.currentData()!='once')
 def behavior_changed(self):
  if self.loading:return
  if self.repeat.currentData()=='held':self.trigger.setCurrentIndex(0)
  self.store();self.update_enabled()
 def store(self,*_):
  if self.loading or self.current<0:return
  m=self.macros[self.current];m.update(name=self.name.text(),source=copy.deepcopy(self.source),trigger=self.trigger.currentData(),repeat=self.repeat.currentData(),count=self.count.value(),gap_ms=self.gap.value())
  self.list.item(self.current).setText(m['name'] or '(unnamed)')
 def add_macro(self):
  if len(self.macros)>=64:return
  d=SourceDialog('Assign new macro to a V1 button',self.provider,None,self,True)
  if not d.exec():return
  self.macros.append(dict(name='Macro '+str(len(self.macros)+1),source=d.source(),trigger='press',repeat='once',count=2,gap_ms=100,steps=[]))
  self.refresh_list(len(self.macros)-1)
 def remove_macro(self):
  if self.current>=0:self.macros.pop(self.current);self.refresh_list()
 def assign_source(self):
  if self.current<0:return
  d=SourceDialog('Assign macro trigger',self.provider,self.source,self,True)
  if d.exec():self.source=d.source();self.assign.setText(source_text(self.source)+' • Change / learn…');self.store()
 def output_label(self,token):
  if token.startswith('key:'):
   vk=int(token[4:]);return 'Key '+next((k for k,v in self.keys.items() if v==vk),str(vk))
  return token.replace('pad:','Xbox ').replace('mouse:','Mouse ')
 def show_steps(self):
  steps=self.macros[self.current]['steps'];self.table.setRowCount(len(steps))
  for i,s in enumerate(steps):
   for j,text in enumerate([' + '.join(self.output_label(t) for t in s['outputs']) or 'Pause (no outputs)',str(s['duration_ms'])+' ms',str(s['delay_ms'])+' ms']):self.table.setItem(i,j,QTableWidgetItem(text))
  self.table.resizeRowsToContents()
 def edit_step(self):
  index=self.table.currentRow()
  if index>=0:self.step_editor(index)
 def step_editor(self,index=None):
  if self.current<0:return
  steps=self.macros[self.current]['steps']
  if index is None and len(steps)>=128:return
  old=steps[index] if index is not None else dict(outputs=[],duration_ms=100,delay_ms=50)
  d=QDialog(self);d.setWindowTitle('Step • simultaneous output group');d.resize(600,650);l=QVBoxLayout(d)
  n=QLabel('Select outputs that should be pressed together.\nLeave all unchecked for a timed pause.');l.addWidget(n)
  search=QLineEdit();search.setPlaceholderText('Filter outputs…');l.addWidget(search)
  choices=QListWidget();l.addWidget(choices,1)
  tokens=[('pad:'+x,'Xbox '+x) for x in sorted(PAD_OUTPUTS)]+[('key:'+str(v),'Key '+k) for k,v in self.keys.items()]+[('mouse:'+x,'Mouse '+x) for x in ('left','right','middle')]
  # Keep imported valid virtual-key values editable even if absent from the usual picker.
  known={t for t,_ in tokens}
  tokens += [(t,self.output_label(t)) for t in old['outputs'] if t not in known]
  for token,title in tokens:
   item=QListWidgetItem(title,choices);item.setData(Qt.ItemDataRole.UserRole,token);item.setFlags(item.flags()|Qt.ItemFlag.ItemIsUserCheckable);item.setCheckState(Qt.CheckState.Checked if token in old['outputs'] else Qt.CheckState.Unchecked)
  def filter_items(text):
   for i in range(choices.count()):choices.item(i).setHidden(text.lower() not in choices.item(i).text().lower())
  search.textChanged.connect(filter_items)
  f=QFormLayout();duration=QSpinBox();duration.setRange(40,600000);duration.setSuffix(' ms');duration.setValue(old['duration_ms']);delay=QSpinBox();delay.setRange(0,600000);delay.setSuffix(' ms');delay.setValue(old['delay_ms']);f.addRow('Hold / pause duration',duration);f.addRow('Delay after release',delay);l.addLayout(f)
  buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(d.accept);buttons.rejected.connect(d.reject);l.addWidget(buttons)
  if d.exec():
   step=dict(outputs=[choices.item(i).data(Qt.ItemDataRole.UserRole) for i in range(choices.count()) if choices.item(i).checkState()==Qt.CheckState.Checked],duration_ms=duration.value(),delay_ms=delay.value())
   if len(step['outputs'])>32:QMessageBox.warning(self,'Too many outputs','Maximum 32 outputs per step.');return
   if index is None:steps.append(step);index=len(steps)-1
   else:steps[index]=step
   self.show_steps();self.table.selectRow(index)
 def remove_step(self):
  index=self.table.currentRow()
  if self.current>=0 and index>=0:self.macros[self.current]['steps'].pop(index);self.show_steps()
 def move_step(self,delta):
  index=self.table.currentRow()
  if self.current<0:return
  steps=self.macros[self.current]['steps'];target=index+delta
  if index>=0 and 0<=target<len(steps):steps[index],steps[target]=steps[target],steps[index];self.show_steps();self.table.selectRow(target)
 def save(self):
  self.store()
  try:validate_macros(self.macros)
  except ValueError as e:QMessageBox.warning(self,'Review macro',str(e));return
  self.accept()
