import os
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

import sys
import types
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
fer = types.ModuleType("fernet")
class DummyFernet:
    def __init__(self, *a, **k):
        pass
    @staticmethod
    def generate_key():
        return b"0" * 16
    def encrypt(self, b):
        return b
    def decrypt(self, b):
        return b
fer.Fernet = DummyFernet
sys.modules["cryptography.fernet"] = fer
fake_fr = types.ModuleType("face_recognition")
fake_fr.load_image_file = lambda p: None
fake_fr.face_encodings = lambda img: []
sys.modules["face_recognition"] = fake_fr
cel = types.ModuleType("celery")
class DummyCelery:
    def __init__(self, *a, **k):
        pass
    def task(self, fn):
        return fn
cel.Celery = DummyCelery
sys.modules["celery"] = cel
sys.modules["whisper"] = types.ModuleType("whisper")
crypto_mod = types.ModuleType("crypto")
crypto_mod.encrypt_file = lambda src, dest: Path(dest).write_bytes(Path(src).read_bytes())
sys.modules["app.utils.crypto"] = crypto_mod
from app import models, database
from app.main import app

@pytest.fixture()
def client(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path}/test.db")
    SessionLocal = sessionmaker(bind=engine)
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", SessionLocal)
    models.Base.metadata.create_all(bind=engine)

    return TestClient(app)

def test_missing_voice_file_returns_400(client):
    resp = client.post("/enroll/voice/00000000-0000-0000-0000-000000000001")
    assert resp.status_code == 400


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_reenroll_same_user(client, tmp_path, monkeypatch):
    voice = tmp_path / "v.wav"
    voice.write_bytes(b"data")

    def fake_encrypt(src, dest):
        Path(dest).write_bytes(Path(src).read_bytes())

    class DummyTask:
        def delay(self, *args, **kwargs):
            pass

    import app.routes.enroll as enroll
    monkeypatch.setattr(enroll, "encrypt_file", fake_encrypt)
    monkeypatch.setattr(enroll, "transcribe_voice", DummyTask())

    user = "123e4567-e89b-12d3-a456-426655440000"
    with voice.open("rb") as fh:
        resp = client.post(
            f"/enroll/voice/{user}",
            files={"file": ("v.wav", fh, "audio/wav")},
        )
    assert resp.status_code == 200

    with voice.open("rb") as fh:
        resp = client.post(
            f"/enroll/voice/{user}",
            files={"file": ("v.wav", fh, "audio/wav")},
        )
    assert resp.status_code == 409



