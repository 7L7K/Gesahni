from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import importlib
import pytest
import uuid

from app import models, database
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

    uid = uuid.UUID("11111111-1111-1111-1111-111111111111")
    with database.SessionLocal() as db:
        db.add(
            models.VoiceSample(user_id=uid, file_path=str(voice))
        )
        db.commit()

    whisper_worker.transcribe_voice(str(voice), str(uid))

    out = Path(f"transcripts/{uid}.txt")
    assert out.exists()
    assert out.read_text() == "hi"
    with database.SessionLocal() as db:
        sample = db.query(models.VoiceSample).filter_by(user_id=uid).first()
        assert sample.transcript_path == str(out)

