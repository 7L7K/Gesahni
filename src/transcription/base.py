import os
import tempfile
from pathlib import Path
from typing import Optional

try:
    import whisper  # type: ignore
except ImportError:
    whisper = None


class TranscriptionService:
    """Transcribe audio files using OpenAI Whisper if available."""

    def __init__(self, model_name: str = "base") -> None:
        self.model_name = model_name
        self.model: Optional[object] = None

    def _load_model(self):
        if self.model is None and whisper is not None:
            try:
                self.model = whisper.load_model(self.model_name)
            except Exception:
                self.model = None

    def transcribe(self, audio_path: str, output_path: Optional[str] = None) -> str:
        self._load_model()
        if self.model is None:
            return "(transcription unavailable)"
        result = self.model.transcribe(audio_path)
        text = result.get("text", "").strip()
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
        return text

    def transcribe_bytes(self, audio_bytes: bytes) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            path = tmp.name
        try:
            return self.transcribe(path)
        finally:
            Path(path).unlink(missing_ok=True)
