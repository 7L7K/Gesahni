import uuid
from pathlib import Path
from datetime import date

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import requests
import numpy as np
import face_recognition

from ..database import get_session
from ..models import User, VoiceSample, FaceSample
from ..utils.encryption import encrypt_file, encrypt_bytes, decrypt_bytes
from ..utils.whisper_worker import transcribe_voice, speaker_job, face_job
from ..utils import tts

router = APIRouter()

MEDIA_ROOT = Path('media')
EMBED_ROOT = Path('embeddings')
UPLOAD_ROOT = Path('uploads')
VOICE_ROOT = UPLOAD_ROOT / 'voice'
FACE_ROOT = UPLOAD_ROOT / 'face'

class Prefs(BaseModel):
    name: str | None = None
    greeting: str | None = None
    reminder_type: str | None = None

class VoiceRequest(BaseModel):
    user_id: str
    tus_url: str

class FaceRequest(BaseModel):
    user_id: str
    urls: list[str]

@router.post('/voice/{user_id}')
async def enroll_voice(
    user_id: str, file: UploadFile | None = File(None), db: Session = Depends(get_session),
):
    # Validate that the ID is a valid UUID, but keep it as a string
    try:
        uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail='invalid user id')

    if file is None:
        raise HTTPException(status_code=400, detail='missing file')
    if file.content_type != 'audio/wav':
        raise HTTPException(status_code=400, detail='invalid file')

    # Always use string user_id in the DB to match your model definition
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
    try:
        uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail='invalid user id')
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
    # Embeddings
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
    today = date.today().isoformat()
    session_dir = Path('sessions') / f"{today}-{user_id}"
    session_dir.mkdir(parents=True, exist_ok=True)
    out_path = session_dir / 'welcome.mp3'
    greeting = user.name or 'there'
    try:
        tts.generate(f"Welcome {greeting}!", out_path.as_posix())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    audio_url = f"/sessions/{today}-{user_id}/welcome.mp3"
    return {"audio_url": audio_url}

@router.post('/init')
async def enroll_init(db: Session = Depends(get_session)):
    """Create a new user and prepare upload folders."""
    user_id = str(uuid.uuid4())
    (VOICE_ROOT / user_id).mkdir(parents=True, exist_ok=True)
    (FACE_ROOT / user_id).mkdir(parents=True, exist_ok=True)
    user = User(id=user_id)
    db.add(user)
    db.commit()
    return {"user_id": user_id}

@router.post('/voice')
async def upload_voice(payload: VoiceRequest, db: Session = Depends(get_session)):
    """Fetch encrypted audio from TUS URL, decrypt, store and enqueue job."""
    user = db.query(User).filter_by(id=payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    voice_dir = VOICE_ROOT / payload.user_id
    voice_dir.mkdir(parents=True, exist_ok=True)
    try:
        resp = requests.get(payload.tus_url, timeout=10)
        resp.raise_for_status()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f'failed to fetch audio: {exc}')
    enc_path = voice_dir / 'voice.enc'
    enc_path.write_bytes(resp.content)
    dec_data = decrypt_bytes(resp.content)
    wav_path = voice_dir / 'voice.wav'
    wav_path.write_bytes(dec_data)
    sample = VoiceSample(user_id=payload.user_id, file_path=str(enc_path))
    db.add(sample)
    db.commit()
    speaker_job.delay(str(wav_path), payload.user_id)
    return {"message": "queued"}

@router.post('/face')
async def upload_face(payload: FaceRequest, db: Session = Depends(get_session)):
    """Fetch face images, encrypt them and enqueue processing job."""
    if len(payload.urls) != 3:
        raise HTTPException(status_code=400, detail='expected three urls')
    user = db.query(User).filter_by(id=payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    face_dir = FACE_ROOT / payload.user_id
    face_dir.mkdir(parents=True, exist_ok=True)
    names = ['front', 'left', 'right']
    enc_paths = []
    for name, url in zip(names, payload.urls):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f'failed to fetch {name}: {exc}')
        enc_data = encrypt_bytes(resp.content)
        path = face_dir / f'{name}.enc'
        path.write_bytes(enc_data)
        enc_paths.append(str(path))
    sample = FaceSample(user_id=payload.user_id,
                        front_path=enc_paths[0],
                        left_path=enc_paths[1],
                        right_path=enc_paths[2],
                        embeddings_path='')
    db.add(sample)
    db.commit()
    face_job.delay(enc_paths, payload.user_id)
    return {"message": "queued"}

@router.get('/status/{user_id}')
async def enroll_status(user_id: str, db: Session = Depends(get_session)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    voice = db.query(VoiceSample).filter_by(user_id=user_id).first()
    face = db.query(FaceSample).filter_by(user_id=user_id).first()
    percent = 0
    if voice:
        percent += 50
    if face:
        percent += 50
    status = 'pending'
    if percent > 0:
        status = 'processing'
    if user.is_active:
        status = 'complete'
        percent = 100
    return {"status": status, "percent": percent}
