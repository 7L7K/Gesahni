from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import RegisterRequest, LoginRequest

from ..database import get_session
from ..models import User, EnrollmentStatus
from ..utils.session import create_session

router = APIRouter()

@router.post('/register')
def register(payload: RegisterRequest, db: Session = Depends(get_session)):
    user = User(id=str(uuid4()), name=payload.name, email=payload.email)
    db.add(user)
    db.add(EnrollmentStatus(user_id=user.id))
    db.commit()
    return {"user_id": user.id}

@router.post('/login')
def login(payload: LoginRequest, db: Session = Depends(get_session)):
    user = db.query(User).filter_by(id=payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    token = create_session(user.id)
    return {"token": token}
