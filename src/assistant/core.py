import logging
from src.transcription.base import TranscriptionService
from src.memory.memory import Memory

logger = logging.getLogger(__name__)


class Assistant:
    """Main assistant class coordinating subsystems."""

    def __init__(self, model_name: str = "base"):
        """Initialize the assistant with the given Whisper model."""
        self.transcription = TranscriptionService(model_name)
        self.memory = Memory()

    def process_audio(self, audio_path: str) -> str:
        logger.info("Processing audio file %s", audio_path)
        text = self.transcription.transcribe(audio_path)
        if text is not None:
            self.memory.add(text)
            return text
        logger.warning("Transcription failed for %s", audio_path)
        return ""
