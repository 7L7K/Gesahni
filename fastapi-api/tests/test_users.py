import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
import types

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

fake_fr = types.ModuleType("face_recognition")
fake_fr.load_image_file = lambda p: None
fake_fr.face_encodings = lambda img: []
sys.modules["face_recognition"] = fake_fr

cel = types.ModuleType("celery")
class DummyCelery:
    def __init__(self, *a, **k):
        pass
    def task(self, *args, **kwargs):
        if args and callable(args[0]):
            return args[0]
        def decorator(fn):
            return fn
        return decorator
cel.Celery = DummyCelery
sys.modules["celery"] = cel

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


def test_enrollment_status(client):
    resp = client.post('/auth/register', json={'name': 'Bob'})
    uid = resp.json()['user_id']
    resp = client.get(f'/users/{uid}/enrollment-status')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'pending'
    assert data['percent'] == 0
