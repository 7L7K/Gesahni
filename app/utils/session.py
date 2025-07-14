from __future__ import annotations
import uuid
from typing import Optional, Dict

_session_store: Dict[str, str] = {}


def create_session(user_id: str) -> str:
    token = str(uuid.uuid4())
    _session_store[token] = user_id
    return token


def get_user(token: str) -> Optional[str]:
    return _session_store.get(token)
