import logging
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

from .base import TranscriptionService

logger = logging.getLogger(__name__)

try:
    from pyannote.audio import Pipeline  # type: ignore
except Exception:  # pragma: no cover - pyannote.audio optional
    Pipeline = None


class DiarizationService:
    """Perform speaker diarization and return speaker-labelled text."""

    def __init__(self, transcriber: TranscriptionService, model_name: str = "pyannote/speaker-diarization") -> None:
        self.transcriber = transcriber
        if Pipeline is not None:
            try:
                self.pipeline = Pipeline.from_pretrained(model_name)
                logger.info("Loaded diarization model '%s'", model_name)
            except Exception as exc:  # pragma: no cover - external models
                logger.exception("Failed to load diarization model: %s", exc)
                self.pipeline = None
        else:  # pragma: no cover - pyannote not installed
            self.pipeline = None

    def diarize(self, audio_path: str) -> Optional[str]:
        """Return speaker-labelled transcription for ``audio_path``."""
        if self.pipeline is None:
            logger.warning("Diarization requested but model is unavailable")
            return None
        try:
            diarization = self.pipeline(audio_path)
        except Exception as exc:
            logger.exception("Diarization failed: %s", exc)
            return None

        segments: List[str] = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            text = self._transcribe_segment(audio_path, turn.start, turn.end)
            if text:
                segments.append(f"{speaker}: {text.strip()}")
        return "\n".join(segments)

    def _transcribe_segment(self, audio_path: str, start: float, end: float) -> Optional[str]:
        """Helper to transcribe a slice of audio using the parent transcriber."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp_name = tmp.name
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    audio_path,
                    "-ss",
                    str(start),
                    "-to",
                    str(end),
                    tmp_name,
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            text = self.transcriber._transcribe_no_diarization(tmp_name)
        except Exception as exc:  # pragma: no cover - ffmpeg or transcription errors
            logger.exception("Failed to transcribe segment: %s", exc)
            text = None
        finally:
            Path(tmp_name).unlink(missing_ok=True)
        return text
