import os


class TranscriptionService:
    """Transcription service using OpenAI Whisper."""

    def __init__(self, model: str = "base") -> None:
        """Initialize the service with a Whisper model name."""
        self.model_name = model
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                import whisper
            except ImportError as exc:
                raise RuntimeError(
                    "Whisper is not installed. Install the 'openai-whisper' package"
                ) from exc

            self._model = whisper.load_model(self.model_name)

    def transcribe(self, audio_path: str, output_path: str) -> str:
        """Transcribe ``audio_path`` and write result to ``output_path``."""
        self._load_model()
        result = self._model.transcribe(audio_path)
        text = result.get("text", "").strip()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(text)
        return text
