from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Boolean, LargeBinary
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=True)
    greeting = Column(String, nullable=True)
    reminder_type = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    voice_samples      = relationship("VoiceSample", back_populates="user")
    face_samples       = relationship("FaceSample", back_populates="user")
    enrollment_status  = relationship("EnrollmentStatus", back_populates="user", uselist=False)
    voiceprints        = relationship("VoicePrint", back_populates="user")
    faceprints         = relationship("FacePrint", back_populates="user")

class VoiceSample(Base):
    __tablename__ = "voice_samples"
    id              = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id         = Column(String, ForeignKey("users.id"))
    file_path       = Column(String)
    transcript_path = Column(String, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="voice_samples")

class FaceSample(Base):
    __tablename__ = "face_samples"
    id               = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id          = Column(String, ForeignKey("users.id"))
    left_path        = Column(String)
    right_path       = Column(String)
    front_path       = Column(String)
    embeddings_path  = Column(String)
    created_at       = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="face_samples")

class ConsentLog(Base):
    __tablename__ = "consent_log"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_agent = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class EnrollmentStatus(Base):
    __tablename__ = "enrollment_statuses"
    user_id    = Column(String, ForeignKey("users.id"), primary_key=True)
    voice_done = Column(Boolean, default=False)
    face_done  = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="enrollment_status")

class VoicePrint(Base):
    __tablename__ = "voiceprints"
    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id    = Column(String, ForeignKey("users.id"))
    vector     = Column(LargeBinary)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="voiceprints")

class FacePrint(Base):
    __tablename__ = "faceprints"
    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id    = Column(String, ForeignKey("users.id"))
    vector     = Column(LargeBinary)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="faceprints")
