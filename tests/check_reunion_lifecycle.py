#!/usr/bin/env python3
"""Test project export, cleanup, cancellation, collision and busy-file protections."""
from pathlib import Path
import json
import runpy
import tempfile
import wave
from unittest.mock import patch

module = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'desktop/lib/reunion_audio.py'))
g = module['archive_report'].__globals__
with tempfile.TemporaryDirectory() as tmp:
    home = Path(tmp); root=home/'recordings'; state=home/'state'; vault=home/'vault'
    for p in (root,state,vault/'Projet A'): p.mkdir(parents=True)
    config=home/'.config/reunion-audio';config.mkdir(parents=True)
    (config/'obsidian.json').write_text(json.dumps({'vault':str(vault),'projects':{'Projet A':'Projet A'}}))
    g.update(HOME=home,ROOT=root,STATE=state,notify=lambda *_:None,active=lambda *_:False)
    def meeting(name='2026-11-18_10-50-28'):
        d=root/name;d.mkdir()
        (d/'CR.md').write_text('# Compte rendu\nTexte validé.\n')
        with wave.open(str(d/'reunion.wav'),'wb') as w:
            w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(b'\0\0'*16000*65)
        return d
    d=meeting()
    assert g['meeting_label'](d)=='[Audio] Réunion du 18/11/2026 à 10:50 (1 min 05 s)'
    (d/'transcription.txt').write_text('Texte')
    assert g['meeting_label'](d).startswith('[Transcript]')
    g['choose']=lambda *_:'Plus tard'
    g['propose_archive'](d)
    assert d.exists() and not list((vault/'Projet A').iterdir())
    # Existing CR is never overwritten.
    old=vault/'Projet A/CR - 2026-11-18 à 10h50m28s.md';old.write_text('Ancien')
    expected=(d/'CR.md').read_bytes()
    g['save']('last.json',{'directory':str(d)})
    target=g['archive_report'](d,'Projet A')
    assert target.read_bytes()==expected and old.read_text()=='Ancien'
    assert not d.exists() and not (state/'last.json').exists()
    assert g['read']('last-export.json')['destination']==str(target)
    # Failed transfer retains all meeting files.
    d=meeting()
    with patch('os.fsync',side_effect=OSError('disk failure')):
        try:g['archive_report'](d,'Projet A')
        except OSError:pass
        else:raise AssertionError('Expected disk error')
    assert (d/'CR.md').read_bytes()==expected and (d/'reunion.wav').exists()
    # Cancelled deletion is harmless; confirmed deletion removes only this meeting.
    g['choose']=lambda *_:'Annuler'
    g['delete_meeting'](d);assert d.exists()
    g['choose']=lambda *_:'Supprimer définitivement'
    g['delete_meeting'](d);assert not d.exists() and target.exists()
    outside=home/'outside';outside.mkdir();(outside/'keep').write_text('safe')
    for invalid in [outside,root]:
        try:g['delete_meeting'](invalid)
        except RuntimeError:pass
        else:raise AssertionError('Unsafe deletion')
    link=root/'link';link.symlink_to(outside,target_is_directory=True)
    try:g['delete_meeting'](link)
    except RuntimeError:pass
    else:raise AssertionError('Symlink deletion')
    assert (outside/'keep').exists()
    # A recording in progress is protected.
    d=meeting();g['save']('recording.json',{'directory':str(d)});g['active']=lambda *_:True
    try:g['delete_meeting'](d)
    except RuntimeError:pass
    else:raise AssertionError('Active recording deleted')
    assert d.exists()
    # Descendants are selectable with their full relative path; hidden folders
    # and symlinks are excluded, in both explicit and automatic configurations.
    nested=vault/'Projet A'/'Client'/'Comptes rendus';nested.mkdir(parents=True)
    (vault/'Projet A'/'.private'/'Hidden').mkdir(parents=True)
    (vault/'Projet A'/'Linked').symlink_to(outside,target_is_directory=True)
    projects=g['obsidian_projects']()
    assert projects['Projet A/Client/Comptes rendus']==nested
    assert not any('private' in label or 'Linked' in label for label in projects)
    auto=home/'.config/obsidian';auto.mkdir()
    (auto/'obsidian.json').write_text(json.dumps({'vaults':{'test':{'path':str(vault),'open':True}}}))
    custom=(config/'obsidian.json').read_text();(config/'obsidian.json').unlink()
    assert g['obsidian_projects']()==projects
    (config/'obsidian.json').write_text(custom)
    g['active']=lambda *_:False
    result=g['archive_report'](d,'Projet A/Client/Comptes rendus')
    assert result.parent==nested and result.exists() and not d.exists()
    # Configured project must stay within the vault.
    (config/'obsidian.json').write_text(json.dumps({'vault':str(vault),'projects':{'Bad':'../outside'}}))
    try:g['obsidian_projects']()
    except RuntimeError:pass
    else:raise AssertionError('Project escaped vault')
print('Meeting labels, project export, verified cleanup, collisions, cancellation and deletion safety: OK')
