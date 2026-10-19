"""Nonblocking macro scheduler: each tick returns desired simultaneous holds."""
import copy
from core import source_value,BUTTONS
PAD_OUTPUTS=set(BUTTONS)|{'LT','RT'}
def validate_macros(items):
 if not isinstance(items,list) or len(items)>64:raise ValueError('Maximum 64 macros per profile')
 for m in items:
  if not isinstance(m,dict) or not isinstance(m.get('name'),str) or not 1<=len(m['name'])<=80:raise ValueError('Macro name must be 1–80 characters')
  src=m.get('source',{})
  if not isinstance(src,dict) or src.get('kind')!='button' or type(src.get('index')) is not int or not 0<=src['index']<128:raise ValueError('Assign a flightstick button')
  if m.get('trigger') not in ('press','release') or m.get('repeat') not in ('once','count','held','toggle'):raise ValueError('Invalid trigger or repeat mode')
  if m['repeat']=='held' and m['trigger']!='press':raise ValueError('While-held repeat requires a press trigger')
  for k,lo,hi in [('count',1,999),('gap_ms',40,600000)]:
   if type(m.get(k)) is not int or not lo<=m[k]<=hi:raise ValueError('Invalid macro '+k)
  steps=m.get('steps')
  if not isinstance(steps,list) or not 1<=len(steps)<=128:raise ValueError('A macro requires 1–128 steps')
  for step in steps:
   if not isinstance(step,dict):raise ValueError('Invalid macro step')
   for k,lo,hi in [('duration_ms',40,600000),('delay_ms',0,600000)]:
    if type(step.get(k)) is not int or not lo<=step[k]<=hi:raise ValueError('Invalid step '+k)
   tokens=step.get('outputs')
   if not isinstance(tokens,list) or len(tokens)>32 or any(not isinstance(t,str) for t in tokens) or len(set(tokens))!=len(tokens):raise ValueError('Invalid simultaneous outputs')
   for t in tokens:
    if t.startswith('pad:') and t[4:] in PAD_OUTPUTS:continue
    if t in ('mouse:left','mouse:right','mouse:middle'):continue
    if t.startswith('key:') and t[4:].isdigit() and 1<=int(t[4:])<=254:continue
    raise ValueError('Unknown macro output: '+t)
 return items
class MacroRunner:
 def __init__(self):self.reset()
 def reset(self):self.configuration=None;self.previous=[];self.running={}
 def update(self,macros,state,now):
  if state is None:self.reset();return set()
  down=[source_value(m['source'],state)>.5 for m in macros]
  if macros!=self.configuration:
   self.configuration=copy.deepcopy(macros);self.previous=down;self.running={};return set()
  outputs=set()
  for i,m in enumerate(macros):
   edge=(down[i] and not self.previous[i]) if m['trigger']=='press' else (not down[i] and self.previous[i])
   if edge:
    if m['repeat']=='toggle' and i in self.running:self.running.pop(i)
    else:self.running[i]=dict(step=0,phase='hold',deadline=now+m['steps'][0]['duration_ms']/1000,cycles=0)
   if m['repeat']=='held' and not down[i]:self.running.pop(i,None)
   run=self.running.get(i)
   if not run:continue
   # At most one output boundary per tick: stalled frames never skip a press.
   ended=False
   if now>=run['deadline']:
    if run['phase']=='hold':
     ended=True
     step=m['steps'][run['step']];run.update(phase='delay',deadline=now+step['delay_ms']/1000)
     if step['delay_ms']==0 and run['step']==len(m['steps'])-1:self.advance(i,m,run,now)
    else:self.advance(i,m,run,now)
   run=self.running.get(i)
   if run and run['phase']=='hold' and not ended:outputs.update(m['steps'][run['step']]['outputs'])
  self.previous=down
  return outputs
 def advance(self,i,m,run,now):
  if run['phase']=='gap':run.update(step=0,phase='hold',deadline=now+m['steps'][0]['duration_ms']/1000);return
  run['step']+=1
  if run['step']<len(m['steps']):run.update(phase='hold',deadline=now+m['steps'][run['step']]['duration_ms']/1000);return
  run['cycles']+=1
  if m['repeat']=='once' or (m['repeat']=='count' and run['cycles']>=m['count']):self.running.pop(i);return
  run.update(phase='gap',deadline=now+m['gap_ms']/1000)
def merge_gamepad(out,tokens):
 for t in tokens:
  if not t.startswith('pad:'):continue
  target=t[4:]
  if target in ('LT','RT'):out[target]=1.
  else:out['buttons']|=BUTTONS[target]
 return out
