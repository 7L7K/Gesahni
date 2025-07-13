import os
from pathlib import Path

from celery import Celery
import whisper
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import VoiceSample
from .encryption import decrypt_file

celery_app = Celery(
    'whisper_worker',
    broker=os.getenv('CELERY_BROKER', 'redis://redis:6379/0'),
    backend=os.getenv('CELERY_BACKEND', 'redis://redis:6379/0'),
)

model = None

def get_model():
    global model
    if model is None:
        model = whisper.load_model('tiny')
    return model

@celery_app.task
def transcribe_voice(file_path: str, user_id: str) -> None:
    temp_path = Path(file_path).with_suffix('.decrypted.wav')
    decrypt_file(file_path, str(temp_path))
    transcript = get_model().transcribe(str(temp_path))['text']
    out_dir = Path('transcripts')
    out_dir.mkdir(parents=True, exist_ok=True)
    txt_path = out_dir / f"{user_id}.txt"
    txt_path.write_text(transcript, encoding='utf-8')

    with SessionLocal() as db:
        sample = db.query(VoiceSample).filter_by(user_id=user_id).first()
        if sample:
            sample.transcript_path = str(txt_path)
            db.commit()
    try:
        os.remove(temp_path)
    except FileNotFoundError:
        pass

@celery_app.task
def speaker_job(file_path: str, user_id: str) -> None:
    """Placeholder task for speaker enrollment."""
    # Actual speaker model training would happen here
    return None

@celery_app.task
def face_job(file_paths: list[str], user_id: str) -> None:
    """Placeholder task for face enrollment."""
    # Face embedding and storage would happen here
    return None
