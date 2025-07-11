import tempfile
from pathlib import Path
from typing import Optional

try:
    import whisper  # type: ignore
except Exception:  # pragma: no cover - whisper is optional
    whisper = None


class TranscriptionService:
    """Transcribe audio files using Whisper if available."""

    def __init__(self, model_name: str = "base") -> None:
        self.model: Optional[object]
        if whisper is not None:
            try:
                self.model = whisper.load_model(model_name)
            except Exception:
                self.model = None
        else:
            self.model = None

    def transcribe(self, audio_path: str) -> str:
        if self.model is None:
            return "(transcription unavailable)"
        result = self.model.transcribe(audio_path)
        return result.get("text", "")

    def transcribe_bytes(self, audio_bytes: bytes) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            path = tmp.name
        text = self.transcribe(path)
        Path(path).unlink(missing_ok=True)
        return text
