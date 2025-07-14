from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import User

router = APIRouter()

@router.get('/{user_id}/enrollment-status')
def enrollment_status(user_id: str, db: Session = Depends(get_session)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    enrolled = bool(user.is_active)
    return {"enrolled": enrolled}
