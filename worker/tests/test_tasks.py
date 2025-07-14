from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import importlib
import os
import types
import sys
import pytest
import uuid
import numpy as np

os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
sys.modules.setdefault("whisper", types.ModuleType("whisper"))

# Provide a minimal Celery replacement before importing tasks
cel = types.ModuleType("celery")
class DummyCelery:
    def __init__(self, *a, **k): pass
    def task(self, *a, **k):
        bind = k.get("bind", False)
        def deco(fn):
            if bind:
                def wrapper(*args, **kw): return fn(None, *args, **kw)
                return wrapper
            return fn
        return deco
cel.Celery = DummyCelery
sys.modules.setdefault("celery", cel)

from app import models, database
from app.utils import whisper_worker
from worker import tasks

@pytest.fixture()
def setup_db(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path}/db.sqlite")
    SessionLocal = sessionmaker(bind=engine)
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", SessionLocal)
    models.Base.metadata.create_all(bind=engine)
    importlib.reload(whisper_worker)
    return engine

def test_transcribe_voice_updates_sample(setup_db, tmp_path, monkeypatch):
    engine = setup_db
    voice = tmp_path / "sample.enc"
    voice.write_bytes(b"data")

    def fake_decrypt(src, dest):
        Path(dest).write_bytes(Path(src).read_bytes())

    class DummyModel:
        def transcribe(self, path):
            return {"text": "hi"}

    monkeypatch.setattr(whisper_worker, "decrypt_file", fake_decrypt)
    monkeypatch.setattr(whisper_worker, "get_model", lambda: DummyModel())
    monkeypatch.chdir(tmp_path)

    uid = str(uuid.uuid4())
    with database.SessionLocal() as db:
        db.add(models.VoiceSample(user_id=uid, file_path=str(voice)))
        db.commit()

    whisper_worker.transcribe_voice(str(voice), uid)

    out = Path(f"transcripts/{uid}.txt")
    assert out.exists()
    assert out.read_text() == "hi"
    with database.SessionLocal() as db:
        sample = db.query(models.VoiceSample).filter_by(user_id=uid).first()
        assert sample.transcript_path == str(out)

def _setup_worker_db(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path}/db.sqlite")
    SessionLocal = sessionmaker(bind=engine)
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", SessionLocal)
    monkeypatch.setattr(tasks, "SessionLocal", SessionLocal)
    models.Base.metadata.create_all(bind=engine)
    return SessionLocal

def test_speaker_job_vectorization(tmp_path, monkeypatch):
    SessionLocal = _setup_worker_db(tmp_path, monkeypatch)

    def fake_get(url, timeout=30):
        class Resp:
            content = b"enc"
            def raise_for_status(self): pass
        return Resp()

    def fake_post(url, json=None, files=None, timeout=10):
        class Resp:
            def raise_for_status(self): pass
        return Resp()

    def fake_decrypt(src, dest):
        Path(dest).write_bytes(b"wav")

    class DummyEagle:
        def enroll(self, path):
            return b"vec"

    monkeypatch.setattr(tasks.requests, "get", fake_get)
    monkeypatch.setattr(tasks.requests, "post", fake_post)
    monkeypatch.setattr(tasks, "decrypt_file", fake_decrypt)
    monkeypatch.setattr(tasks, "Eagle", DummyEagle)
    monkeypatch.setattr(tasks, "_post_callback", lambda *a, **k: None)

    uid = str(uuid.uuid4())
    tasks.speaker_job(uid, "http://fake")

    with SessionLocal() as db:
        vp = db.query(models.VoicePrint).filter_by(user_id=uid).first()
        assert vp.vector == b"vec"

def test_face_job_vectorization(tmp_path, monkeypatch):
    SessionLocal = _setup_worker_db(tmp_path, monkeypatch)

    vectors = [np.array([1.0, 2.0], dtype=np.float32), np.array([3.0, 4.0], dtype=np.float32)]
    get_calls = []

    def fake_get(url, timeout=30):
        class Resp:
            content = b"enc"
            def raise_for_status(self): pass
        get_calls.append(url)
        return Resp()

    def fake_post(url, files=None, timeout=30):
        class Resp:
            def raise_for_status(self): pass
            def json(self): return {"vector": vectors[len(get_calls)-1].tolist()}
        return Resp()

    def fake_decrypt(src, dest):
        Path(dest).write_bytes(b"img")

    monkeypatch.setattr(tasks.requests, "get", fake_get)
    monkeypatch.setattr(tasks.requests, "post", fake_post)
    monkeypatch.setattr(tasks, "decrypt_file", fake_decrypt)
    monkeypatch.setattr(tasks, "_post_callback", lambda *a, **k: None)
    monkeypatch.setattr(tasks, "Eagle", None)

    uid = str(uuid.uuid4())
    tasks.face_job(uid, ["url1", "url2"])

    avg = np.mean(vectors, axis=0)
    with SessionLocal() as db:
        fp = db.query(models.FacePrint).filter_by(user_id=uid).first()
        assert np.allclose(np.frombuffer(fp.vector, dtype=np.float32), avg)
