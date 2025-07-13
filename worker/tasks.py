import os
import uuid
from pathlib import Path
from typing import List

import requests
import numpy as np
from celery import Celery

from app.utils.crypto import decrypt_file
from app.database import SessionLocal
from app.models import VoicePrint, FacePrint

try:
    from pv_eagle_python import Eagle
except Exception:  # pragma: no cover - library may be missing in tests
    Eagle = None

API_BASE = os.getenv("API_BASE", "http://api:8000")
celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_BACKEND", "redis://redis:6379/0"),
)


def _post_callback(path: str, payload: dict) -> None:
    """Send a POST request to ``API_BASE``/``path`` ignoring failures."""
    url = f"{API_BASE}{path}"
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass


@celery_app.task
def speaker_job(user_id: str, tus_url: str) -> None:
    """Enroll a speaker from a remote encrypted WAV file."""
    tmp_enc = Path("/tmp") / f"{uuid.uuid4()}.wav.enc"
    tmp_wav = tmp_enc.with_suffix(".wav")
    try:
        resp = requests.get(tus_url, timeout=30)
        resp.raise_for_status()
        tmp_enc.write_bytes(resp.content)
        decrypt_file(str(tmp_enc), str(tmp_wav))
        if Eagle is None:
            raise RuntimeError("pv_eagle_python not available")
        eagle = Eagle()
        vector: bytes = eagle.enroll(str(tmp_wav))
        with SessionLocal() as db:
            vp = VoicePrint(user_id=user_id, vector=vector)
            db.add(vp)
            db.commit()
    finally:
        tmp_enc.unlink(missing_ok=True)
        tmp_wav.unlink(missing_ok=True)
    _post_callback("/internal/voice_done", {"user_id": user_id})


@celery_app.task
def face_job(user_id: str, tus_urls: List[str]) -> None:
    """Enroll a face from multiple encrypted images."""
    vectors = []
    for url in tus_urls:
        tmp_enc = Path("/tmp") / f"{uuid.uuid4()}.jpg.enc"
        tmp_img = tmp_enc.with_suffix(".jpg")
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            tmp_enc.write_bytes(resp.content)
            decrypt_file(str(tmp_enc), str(tmp_img))
            with open(tmp_img, "rb") as fh:
                r = requests.post(f"{API_BASE}/embed", files={"file": fh}, timeout=30)
            r.raise_for_status()
            data = r.json()
            embedding = np.array(data.get("vector") or data.get("embedding"), dtype=np.float32)
            vectors.append(embedding)
        finally:
            tmp_enc.unlink(missing_ok=True)
            tmp_img.unlink(missing_ok=True)
    if vectors:
        avg = np.mean(vectors, axis=0)
        with SessionLocal() as db:
            fp = FacePrint(user_id=user_id, vector=avg.tobytes())
            db.add(fp)
            db.commit()
    _post_callback("/internal/face_done", {"user_id": user_id})
