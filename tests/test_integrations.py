import json, os
from pathlib import Path
from types import SimpleNamespace
import pytest
from engine import integrations


def test_buffer_dry_run(monkeypatch):
    monkeypatch.setenv('PUBLISH_ENABLED','false')
    monkeypatch.setenv('PUBLISH_DRY_RUN','true')
    result=integrations.buffer_queue('https://example.invalid/video','caption',['channel'],enabled=True)
    assert result['dry_run'] is True
    assert 'tidak ada post' in result['message'].lower()


def test_buffer_disabled_even_when_requested(monkeypatch):
    monkeypatch.setenv('PUBLISH_ENABLED','true')
    monkeypatch.setenv('PUBLISH_DRY_RUN','true')
    result=integrations.buffer_queue('https://example.invalid/video','caption',['id'],enabled=False)
    assert result['dry_run'] is True


def test_buffer_requires_both_flags(monkeypatch):
    monkeypatch.setenv('PUBLISH_ENABLED','true')
    monkeypatch.setenv('PUBLISH_DRY_RUN','true')
    result=integrations.buffer_queue('https://example.invalid/video','caption',['id'],enabled=True)
    assert result['dry_run'] is True


def test_pixabay_fallback_and_download(tmp_path, monkeypatch):
    search=SimpleNamespace(json=lambda:{'hits':[{'id':12,'videos':{'small':{'url':'https://video.invalid/12'}}}]},raise_for_status=lambda:None)
    chunks=[b'x'*120000]
    class Download:
        def __enter__(self): return self
        def __exit__(self,*a): return None
        def raise_for_status(self): pass
        def iter_content(self,chunk_size): yield from chunks
    monkeypatch.setattr(integrations.requests,'get',lambda *a,**k: search if not k.get('stream') else Download())
    files,ids=integrations.pixabay_download('query','key',tmp_path,count=1,cache_path=tmp_path/'cache.json')
    assert ids==['12'] and Path(files[0]).stat().st_size>100000


def test_pixabay_no_results(tmp_path, monkeypatch):
    class Resp:
        def raise_for_status(self): pass
        def json(self): return {'hits':[]}
    monkeypatch.setattr(integrations.requests,'get',lambda *a,**k: Resp())
    with pytest.raises(RuntimeError): integrations.pixabay_download('q','key',tmp_path,cache_path=tmp_path/'cache.json')


def test_cloudinary_signature_and_result(tmp_path, monkeypatch):
    p=tmp_path/'video.mp4';p.write_bytes(b'x'*120000)
    monkeypatch.setenv('CLOUDINARY_CLOUD_NAME','cloud')
    monkeypatch.setenv('CLOUDINARY_API_KEY','key')
    monkeypatch.setenv('CLOUDINARY_API_SECRET','secret')
    class Resp:
        def raise_for_status(self): pass
        def json(self): return {'secure_url':'https://res.invalid/video','public_id':'test','bytes':120000}
    calls=[]
    monkeypatch.setattr(integrations.requests,'post',lambda *a,**k: (calls.append(k) or Resp()))
    result=integrations.cloudinary_upload(p,public_id='test')
    assert result['secure_url']=='https://res.invalid/video'
    assert calls[0]['data']['public_id']=='test' and calls[0]['data']['signature' ] and calls[0]['data']['overwrite']=='true'


def test_buffer_queue_success_and_dedupe(tmp_path, monkeypatch):
    monkeypatch.setenv('PUBLISH_ENABLED','true')
    monkeypatch.setenv('PUBLISH_DRY_RUN','false')
    monkeypatch.setenv('BUFFER_ACCESS_TOKEN','token')
    calls=[]
    def fake_post(url,**kwargs):
        payload=kwargs['json']; q=payload['query']
        calls.append(payload)
        if 'GetChannel' in q:
            return SimpleNamespace(raise_for_status=lambda:None,json=lambda:{'data':{'channel':{'id':'c1','name':'Test','service':'instagram','type':'business','isDisconnected':False,'isQueuePaused':False}}})
        return SimpleNamespace(raise_for_status=lambda:None,json=lambda:{'data':{'createPost':{'post':{'id':'post-1','dueAt':'2026-01-01'}}}})
    monkeypatch.setattr(integrations.requests,'post',fake_post)
    manifest=tmp_path/'manifest.json'
    result=integrations.buffer_queue('https://cloud.invalid/video','caption',['c1'],enabled=True,manifest_path=manifest,content_key='key1')
    assert result['results'][0]['status']=='success'
    saved=json.loads(manifest.read_text())
    assert saved['key1']['c1']['status']=='success'
    calls_before=len(calls)
    result2=integrations.buffer_queue('https://cloud.invalid/video','caption',['c1'],enabled=True,manifest_path=manifest,content_key='key1')
    assert result2['results'][0]['status']=='skipped_reconcile'
    assert len(calls)==calls_before


def test_buffer_channel_uses_notification_for_fb_group():
    assert integrations._scheduling_type({'service':'facebook','type':'group'})=='notification'
    assert integrations._scheduling_type({'service':'instagram','type':'profile'})=='notification'
    assert integrations._scheduling_type({'service':'instagram','type':'business'})=='automatic'
    assert integrations._post_metadata({'service':'instagram','type':'business'},'Title\nCaption')['instagram']['type']=='reel'
    assert integrations._post_metadata({'service':'facebook','type':'page'},'Title')['facebook']['type']=='reel'
    assert integrations._post_metadata({'service':'youtube','type':'channel'},'Title')['youtube']['categoryId']=='27'
    with pytest.raises(RuntimeError): integrations._post_metadata({'service':'pinterest','type':'account'},'Title')


def test_buffer_manifest_unknown_prevents_retry(tmp_path, monkeypatch):
    manifest=tmp_path/'manifest.json'; manifest.write_text(json.dumps({'key':{'c1':{'status':'unknown'}}}))
    monkeypatch.setenv('PUBLISH_ENABLED','true');monkeypatch.setenv('PUBLISH_DRY_RUN','false');monkeypatch.setenv('BUFFER_ACCESS_TOKEN','token')
    result=integrations.buffer_queue('https://cloud.invalid/video','caption',['c1'],enabled=True,manifest_path=manifest,content_key='key')
    assert result['results'][0]['status']=='skipped_reconcile'


def test_tts_uses_python_module(tmp_path, monkeypatch):
    import sys, types, asyncio
    fake=types.ModuleType('edge_tts')
    class Communicate:
        def __init__(self,text,voice): self.text=text; self.voice=voice
        async def save(self,path): Path(path).write_bytes(b'x'*20000)
    fake.Communicate=Communicate
    monkeypatch.setitem(sys.modules,'edge_tts',fake)
    target=tmp_path/'audio.mp3'
    assert integrations.create_tts('hello',target)==str(target)
    assert target.stat().st_size==20000


def test_publish_pipeline_guard_rejects_without_explicit_flags(monkeypatch):
    from engine.production_pipeline import run_pipeline
    monkeypatch.setenv('PUBLISH_ENABLED','false')
    monkeypatch.setenv('PUBLISH_DRY_RUN','true')
    with pytest.raises(RuntimeError,match='Publish Guard'):
        run_pipeline(outdir='never_created',publish=True,channel_ids=['c1'])
