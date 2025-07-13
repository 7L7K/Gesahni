import os
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_session
from ..models import User, VoiceSample, FaceSample
from ..utils.crypto import encrypt_file
from ..utils.whisper_worker import transcribe_voice

import numpy as np
import face_recognition

router = APIRouter()

MEDIA_ROOT = Path('media')
EMBED_ROOT = Path('embeddings')

class Prefs(BaseModel):
    name: str | None = None
    greeting: str | None = None
    reminder_type: str | None = None

@router.post('/voice/{user_id}')
async def enroll_voice(
    user_id: str, file: UploadFile | None = File(None), db: Session = Depends(get_session)
):
    if file is None:
        raise HTTPException(status_code=400, detail='missing file')
    if file.content_type != 'audio/wav':
        raise HTTPException(status_code=400, detail='invalid file')
    if db.query(VoiceSample).filter_by(user_id=user_id).first():
        raise HTTPException(status_code=409, detail='already enrolled')
    user_dir = MEDIA_ROOT / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    raw_path = user_dir / 'voice.wav'
    data = await file.read()
    with open(raw_path, 'wb') as fh:
        fh.write(data)
    enc_path = raw_path.with_suffix('.enc')
    encrypt_file(str(raw_path), str(enc_path))
    voice_sample = VoiceSample(user_id=user_id, file_path=str(enc_path))
    db.add(voice_sample)
    db.commit()
    transcribe_voice.delay(str(enc_path), user_id)
    return {"message": "queued"}

@router.post('/face/{user_id}')
async def enroll_face(
    user_id: str,
    front: UploadFile | None = File(None),
    left: UploadFile | None = File(None),
    right: UploadFile | None = File(None),
    db: Session = Depends(get_session),
):
    if not front or not left or not right:
        raise HTTPException(status_code=400, detail='missing images')
    user_dir = MEDIA_ROOT / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    if db.query(FaceSample).filter_by(user_id=user_id).first():
        raise HTTPException(status_code=409, detail='already enrolled')
    paths = {}
    for name, file in [('front', front), ('left', left), ('right', right)]:
        if file.content_type != 'image/jpeg':
            raise HTTPException(status_code=400, detail='images must be jpeg')
        raw = user_dir / f"{name}.jpg"
        data = await file.read()
        with open(raw, 'wb') as fh:
            fh.write(data)
        enc = raw.with_suffix('.enc')
        encrypt_file(str(raw), str(enc))
        paths[name] = str(enc)

    # embeddings
    img = face_recognition.load_image_file(str(user_dir / 'front.jpg'))
    encodings = face_recognition.face_encodings(img)
    emb = encodings[0] if encodings else np.zeros(128)
    EMBED_ROOT.mkdir(parents=True, exist_ok=True)
    emb_path = EMBED_ROOT / f"{user_id}.npy"
    np.save(emb_path, emb)

    sample = FaceSample(
        user_id=user_id,
        front_path=paths['front'],
        left_path=paths['left'],
        right_path=paths['right'],
        embeddings_path=str(emb_path),
    )
    db.add(sample)
    db.commit()
    return {"message": "faces stored"}

@router.post('/prefs/{user_id}')
async def set_prefs(user_id: str, prefs: Prefs, db: Session = Depends(get_session)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        user = User(id=user_id)
        db.add(user)
    user.name = prefs.name
    user.greeting = prefs.greeting
    user.reminder_type = prefs.reminder_type
    db.commit()
    return {"message": "saved"}

@router.post('/complete/{user_id}')
async def complete_enroll(user_id: str, db: Session = Depends(get_session)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    if user.is_active:
        raise HTTPException(status_code=409, detail='already active')
    user.is_active = True
    db.commit()
    # stub call to external TTS service
    audio_url = f"https://example.com/greet_{user_id}.mp3"
    return {"audio_url": audio_url}
