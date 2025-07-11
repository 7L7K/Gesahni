import logging
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

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
                logger.info("Loaded whisper model '%s'", model_name)
            except Exception as exc:
                logger.exception("Failed to load whisper model: %s", exc)
                self.model = None
        else:
            self.model = None

    def transcribe(self, audio_path: str) -> str:
        """Transcribe audio file at ``audio_path``."""
        if self.model is None:
            logger.warning("Transcription requested but model is unavailable")
            return "(transcription unavailable)"
        try:
            result = self.model.transcribe(audio_path)
        except Exception as exc:
            logger.exception("Transcription failed: %s", exc)
            return ""
        return result.get("text", "")

    def transcribe_bytes(self, audio_bytes: bytes) -> str:
        """Transcribe raw audio bytes."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            try:
                tmp.write(audio_bytes)
                tmp.flush()
                path = tmp.name
            except Exception as exc:
                logger.exception("Failed to write temporary audio file: %s", exc)
                return ""
        text = self.transcribe(path)
        Path(path).unlink(missing_ok=True)
        return text
