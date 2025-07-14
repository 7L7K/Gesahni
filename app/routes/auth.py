from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import User

router = APIRouter()

class RegisterPayload(BaseModel):
    name: str
    email: str | None = None

@router.post('/register')
def register(payload: RegisterPayload, db: Session = Depends(get_session)):
    user = User(name=payload.name)
    db.add(user)
    db.commit()
    return {"user_id": user.id}

class LoginPayload(BaseModel):
    user_id: str

@router.post('/login')
def login(payload: LoginPayload, db: Session = Depends(get_session)):
    user = db.query(User).filter_by(id=payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    return {"message": "ok"}
