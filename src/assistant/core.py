from src.transcription.base import TranscriptionService
from src.memory.memory import Memory

class Assistant:
    """Main assistant class coordinating subsystems."""
    def __init__(self):
        self.transcription = TranscriptionService()
        self.memory = Memory()

    def process_audio(self, audio_path: str) -> str:
        text = self.transcription.transcribe(audio_path)
        self.memory.add(text)
        return text
