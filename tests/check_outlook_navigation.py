#!/usr/bin/env python3
"""Validate parent selection and ensure the old message closes only after success."""
from pathlib import Path
import runpy
import sys
from unittest.mock import patch
import json

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'desktop/lib'))
m=runpy.run_path(str(Path(sys.path[0])/'outlook_navigation.py'))
g=m['navigate'].__globals__
parent={'address':'0x1','class':'google-chrome','title':'Courrier - Outlook - Google Chrome',
        'initialTitle':'Boîte de réception – Test – Outlook - Google Chrome','monitor':1}
old={'address':'0x2','class':'google-chrome','initialClass':'google-chrome',
     'title':'Message – Test – Outlook - Google Chrome','initialTitle':'about:blank - Google Chrome',
     'monitor':1,'floating':True,'size':[1100,900],'at':[100,200]}
new=dict(old,address='0x3',title='Suivant – Test – Outlook - Google Chrome')
assert m['parent_window'](old,[old,parent])==parent
try:m['parent_window'](old,[old])
except RuntimeError:pass
else:raise AssertionError('Missing parent accepted')
commands=[];g['dispatch']=lambda action,args:commands.append((action,args))
sequence=iter([[old,parent],[old,parent,new],[old,parent,new]])
g['clients']=lambda:next(sequence)
with patch('subprocess.check_output',return_value=json.dumps(old)),patch('time.sleep'):
 m['navigate']('next')
assert commands[0]==('sendshortcut',',Down,address:0x1')
assert commands[1]==('sendshortcut','SHIFT,Return,address:0x1')
assert commands[-1]==('closewindow','address:0x2')
assert ('focuswindow','address:0x3') in commands
commands.clear();g['clients']=lambda:[old,parent]
with patch('subprocess.check_output',return_value=json.dumps(old)),patch('time.sleep'),patch('time.monotonic',side_effect=[0,13]):
 try:m['navigate']('previous')
 except RuntimeError:pass
 else:raise AssertionError('Missing new window accepted')
assert commands[0]==('sendshortcut',',Up,address:0x1')
assert not any(action=='closewindow' for action,_ in commands)
commands.clear()
with patch('subprocess.check_output',return_value=json.dumps({'address':'0x9','class':'kitty'})):
 m['navigate']('next')
assert commands==[('sendshortcut','CTRL,code:194,address:0x9')]
print('Outlook parent selection, forward/backward input, preserve-on-failure and shortcut forwarding: OK')
