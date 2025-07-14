from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import User, VoiceSample, FaceSample

router = APIRouter()

@router.get('/{user_id}/enrollment-status')
def enrollment_status(user_id: str, db: Session = Depends(get_session)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='user not found')

    # Check if user has provided voice and face samples
    voice = db.query(VoiceSample).filter_by(user_id=user_id).first()
    face = db.query(FaceSample).filter_by(user_id=user_id).first()

    percent = 0
    if voice:
        percent += 50
    if face:
        percent += 50

    # Default status
    status = 'pending'
    if percent > 0 and percent < 100:
        status = 'processing'
    if user.is_active:
        status = 'complete'
        percent = 100

    return {"status": status, "percent": percent}
