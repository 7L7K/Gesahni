from src.transcription.base import TranscriptionService
from src.memory.memory import Memory

class Assistant:
    """Main assistant class coordinating subsystems."""
    def __init__(self):
        self.transcription = TranscriptionService()
        self.memory = Memory()

    def process_audio(self, audio_path: str, transcript_path: str) -> str:
        """Transcribe ``audio_path`` and store the result."""
        text = self.transcription.transcribe(audio_path, transcript_path)
        self.memory.add(text)
        return text
