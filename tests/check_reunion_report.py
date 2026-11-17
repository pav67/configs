#!/usr/bin/env python3
"""Validate report requests and ensure failed generations preserve existing notes."""
import io
import json
from pathlib import Path
import runpy
import tempfile
import urllib.error
from unittest.mock import patch

module = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'desktop/lib/reunion_audio.py'))
report = module['report']
g = report.__globals__
with tempfile.TemporaryDirectory() as tmp:
    home = Path(tmp)
    state = home / 'state'; state.mkdir()
    config = home / '.config/reunion-audio'; config.mkdir(parents=True)
    (config/'ai.json').write_text(json.dumps({'base_url':'http://localhost:1234/v1','model':'test','timeout':10}))
    meeting = home/'meeting'; meeting.mkdir()
    (meeting/'transcription.txt').write_text('Alice propose une migration, sans décision.')
    g.update(HOME=home,STATE=state,notify=lambda *_:None)
    requests=[]
    def success(request,timeout):
        requests.append(json.loads(request.data))
        assert request.full_url=='http://localhost:1234/v1/chat/completions'
        assert timeout==10
        return io.BytesIO(json.dumps({'choices':[{'finish_reason':'stop','message':{'content':'# Compte rendu\nMigration proposée.'}}]}).encode())
    with patch('urllib.request.urlopen',success): report(str(meeting))
    assert (meeting/'CR.md').read_text().startswith('# Compte rendu')
    assert requests[0]['messages'][1]['content'].endswith('Alice propose une migration, sans décision.')
    with patch('urllib.request.urlopen',success): report(str(meeting))
    assert list(meeting.glob('CR.*.bak.md'))
    original=(meeting/'CR.md').read_text()
    def truncated(*args,**kwargs):
        return io.BytesIO(b'{"choices":[{"finish_reason":"length","message":{"content":"incomplete"}}]}')
    for response in (truncated, urllib.error.URLError('offline')):
        kwargs={'side_effect': response} if isinstance(response,Exception) else {'new':response}
        with patch('urllib.request.urlopen',**kwargs):
            try: report(str(meeting))
            except RuntimeError: pass
            else: raise AssertionError('Expected error')
        assert (meeting/'CR.md').read_text()==original
        assert not (state/'report.json').exists()
print('Report request, atomic output, backup, truncated response and offline recovery: OK')
