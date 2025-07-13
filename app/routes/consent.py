from datetime import datetime
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import ConsentLog

router = APIRouter()

@router.post('/')
async def log_consent(request: Request, db: Session = Depends(get_session)):
    ua = request.headers.get('User-Agent', 'unknown')
    entry = ConsentLog(user_agent=ua, timestamp=datetime.utcnow())
    db.add(entry)
    db.commit()
    return {'message': 'recorded'}
