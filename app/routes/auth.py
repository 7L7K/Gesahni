from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import User, EnrollmentStatus
from ..utils.session import create_session

router = APIRouter()

class RegisterPayload(BaseModel):
    name: str
    email: str | None = None

class LoginPayload(BaseModel):
    user_id: str

@router.post('/register')
def register(payload: RegisterPayload, db: Session = Depends(get_session)):
    user = User(id=str(uuid4()), name=payload.name, email=payload.email)
    db.add(user)
    db.add(EnrollmentStatus(user_id=user.id))
    db.commit()
    return {"user_id": user.id}

@router.post('/login')
def login(payload: LoginPayload, db: Session = Depends(get_session)):
    user = db.query(User).filter_by(id=payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    token = create_session(user.id)
    return {"token": token}
