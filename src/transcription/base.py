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

    def __init__(self, model_name: str = "base", enable_diarization: bool = False) -> None:
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

        self.enable_diarization = enable_diarization
        self.diarization = None
        if enable_diarization:
            try:
                from .diarization import DiarizationService
                self.diarization = DiarizationService(self)
            except Exception as exc:
                logger.exception("Failed to initialize diarization: %s", exc)

    def _transcribe_no_diarization(self, audio_path: str) -> Optional[str]:
        """Transcribe ``audio_path`` without applying diarization."""
        if self.model is None:
            logger.warning("Transcription requested but model is unavailable")
            return None
        try:
            result = self.model.transcribe(audio_path)
        except Exception as exc:
            logger.exception("Transcription failed: %s", exc)
            return None
        return result.get("text", "")

    def transcribe(self, audio_path: str) -> Optional[str]:
        """Transcribe audio file at ``audio_path``.

        Returns ``None`` if transcription cannot be performed or fails.
        """
        if self.enable_diarization and self.diarization is not None:
            return self.diarization.diarize(audio_path)
        return self._transcribe_no_diarization(audio_path)

    def transcribe_bytes(self, audio_bytes: bytes) -> Optional[str]:
        """Transcribe raw audio bytes.

        Returns ``None`` if the bytes cannot be written or transcription fails.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            try:
                tmp.write(audio_bytes)
                tmp.flush()
                path = tmp.name
            except Exception as exc:
                logger.exception(
                    "Failed to write temporary audio file: %s", exc
                )
                return None
        text = self.transcribe(path)
        Path(path).unlink(missing_ok=True)
        return text
