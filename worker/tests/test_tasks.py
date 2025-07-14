from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import importlib
import pytest

from app import models, database

import types
sys.modules.setdefault("whisper", types.ModuleType("whisper"))
from app.utils import whisper_worker

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

    user_id = uuid.uuid4()
    with database.SessionLocal() as db:
        db.add(models.VoiceSample(user_id=user_id, file_path=str(voice)))
        db.commit()

    whisper_worker.transcribe_voice(str(voice), user_id)

    out = Path(f"transcripts/{user_id}.txt")
    assert out.exists()
    assert out.read_text() == "hi"
    with database.SessionLocal() as db:
        sample = db.query(models.VoiceSample).filter_by(user_id=user_id).first()
        assert sample.transcript_path == str(out)

import sys
import types
import uuid
import numpy as np


@pytest.fixture()
def worker_tasks(tmp_path, monkeypatch):
    # stub crypto module
    crypto = types.ModuleType("crypto")
    def fake_decrypt(src, dest):
        Path(dest).write_bytes(Path(src).read_bytes())
    crypto.decrypt_file = fake_decrypt
    sys.modules["app.utils.crypto"] = crypto

    # stub pv_eagle_python
    pv = types.ModuleType("pv_eagle_python")
    class DummyEagle:
        def enroll(self, path):
            return b"vec"
    pv.Eagle = DummyEagle
    sys.modules["pv_eagle_python"] = pv

    engine = create_engine(f"sqlite:///{tmp_path}/worker.sqlite")
    SessionLocal = sessionmaker(bind=engine)
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", SessionLocal)
    models.Base.metadata.create_all(bind=engine)

    import importlib
    import worker.tasks as tasks
    tasks = importlib.reload(tasks)
    return tasks


def test_speaker_job_creates_voiceprint(worker_tasks, monkeypatch):
    tasks = worker_tasks
    user_id = uuid.uuid4()
    uid = uuid.UUID("11111111-1111-1111-1111-111111111111")
    monkeypatch.setattr(tasks.uuid, "uuid4", lambda: uid)

    class Resp:
        def __init__(self, content=b"data"):
            self.content = content
        def raise_for_status(self):
            pass
    monkeypatch.setattr(tasks.requests, "get", lambda *a, **k: Resp())

    cb = {}
    monkeypatch.setattr(tasks, "_post_callback", lambda path, payload: cb.update({"path": path, "payload": payload}))

    class DummyEagle:
        def enroll(self, path):
            return b"voicevec"
    monkeypatch.setattr(tasks, "Eagle", DummyEagle)

    tasks.speaker_job(user_id, "http://tus")

    enc = Path("/tmp") / f"{uid}.wav.enc"
    dec = Path("/tmp") / f"{uid}.wav"
    assert not enc.exists()
    assert not dec.exists()
    with tasks.SessionLocal() as db:
        vp = db.query(models.VoicePrint).filter_by(user_id=user_id).first()
        assert vp is not None
        assert vp.vector == b"voicevec"
    assert cb == {"path": "/internal/voice_done", "payload": {"user_id": user_id}}


def test_face_job_creates_faceprint(worker_tasks, monkeypatch):
    tasks = worker_tasks
    user_id = uuid.uuid4()
    ids = [
        uuid.UUID("22222222-2222-2222-2222-222222222221"),
        uuid.UUID("22222222-2222-2222-2222-222222222222"),
        uuid.UUID("22222222-2222-2222-2222-222222222223"),
    ]
    gen = (i for i in ids)
    monkeypatch.setattr(tasks.uuid, "uuid4", lambda: next(gen))

    class GetResp:
        def __init__(self):
            self.content = b"img"
        def raise_for_status(self):
            pass
    monkeypatch.setattr(tasks.requests, "get", lambda *a, **k: GetResp())

    class PostResp:
        def __init__(self):
            self._json = {"vector": [1.0, 2.0, 3.0]}
        def raise_for_status(self):
            pass
        def json(self):
            return self._json
    monkeypatch.setattr(tasks.requests, "post", lambda *a, **k: PostResp())

    cb = {}
    monkeypatch.setattr(tasks, "_post_callback", lambda path, payload: cb.update({"path": path, "payload": payload}))

    tasks.face_job(user_id, ["a", "b", "c"])

    for uid in ids:
        assert not (Path("/tmp") / f"{uid}.jpg.enc").exists()
        assert not (Path("/tmp") / f"{uid}.jpg").exists()
    with tasks.SessionLocal() as db:
        fp = db.query(models.FacePrint).filter_by(user_id=user_id).first()
        assert fp is not None
        vec = np.frombuffer(fp.vector, dtype=np.float32)
        assert np.allclose(vec, np.array([1.0, 2.0, 3.0], dtype=np.float32))
    assert cb == {"path": "/internal/face_done", "payload": {"user_id": user_id}}

