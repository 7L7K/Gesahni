from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class EnrollInitResponse(BaseModel):
    user_id: UUID

class VoiceRequest(BaseModel):
    user_id: UUID
    voiceprint: bytes

class FaceRequest(BaseModel):
    user_id: UUID
    faceprint: bytes

class StatusResponse(BaseModel):
    user_id: UUID
    voice_done: bool
    face_done: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
