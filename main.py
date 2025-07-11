"""Entry point for running the assistant."""
import yaml
from src.assistant.core import Assistant
from src.sessions import SessionManager


def load_config(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as fh:
        return yaml.safe_load(fh)


def main() -> None:
    config = load_config('config.yaml')

    assistant = Assistant(model_name=config.get('whisper_model', 'base'))

    session_manager = SessionManager(
        root=config.get('session_root', 'sessions')
    )
    session_dir = session_manager.create_today_session()

    print(f"Loaded config for {config.get('name')}")
    audio_cfg = config.get('audio', {})
    print(
        f"Audio settings: bitrate={audio_cfg.get('bitrate')} "
        f"format={audio_cfg.get('format')}"
    )
    print(f"Using Whisper model: {config.get('whisper_model')}")
    print(f"Session directory prepared at {session_dir}")
    # Placeholder for processing
    result = assistant.process_audio('sample.wav')
    print(f"Processed audio: {result}")


if __name__ == '__main__':
    main()

