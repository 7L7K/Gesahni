"""Entry point for running the assistant."""
import os
import yaml
from src.assistant.core import Assistant
from src.sessions import SessionManager


def load_config(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as fh:
        return yaml.safe_load(fh)


def main() -> None:
    config = load_config('config.yaml')
    assistant = Assistant()
    session_manager = SessionManager()
    session_dir = session_manager.create_today_session()
    # Normally we would pass config to components.
    print(f"Loaded config for {config.get('name')}")
    print(f"Session directory prepared at {session_dir}")

    audio_path = os.path.join(session_dir, "audio.wav")
    transcript_path = os.path.join(session_dir, "transcript.txt")
    result = assistant.process_audio(audio_path, transcript_path)
    print(f"Transcription saved to {transcript_path}")
    print(result)


if __name__ == '__main__':
    main()

