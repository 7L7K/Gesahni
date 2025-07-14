from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .routes import enroll, consent

app = FastAPI()

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

# Ensure session directory exists
Path("sessions").mkdir(parents=True, exist_ok=True)
app.mount("/sessions", StaticFiles(directory="sessions"), name="sessions")

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

app.include_router(enroll.router, prefix="/enroll")
app.include_router(consent.router, prefix="/consent")
