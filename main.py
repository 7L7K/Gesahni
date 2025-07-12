"""Entry point for running the assistant."""
import argparse
import logging
import yaml
from src.assistant.core import Assistant
from src.sessions import SessionManager

logger = logging.getLogger(__name__)

def load_config(path: str) -> dict:
    """Load YAML configuration from ``path``.
    Returns an empty dictionary if loading fails.
    """
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return yaml.safe_load(fh) or {}
    except Exception as exc:
        logger.exception("Failed to load configuration: %s", exc)
        return {}

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the assistant")
    parser.add_argument(
        "audio",
        nargs="?",
        default="sample.wav",
        help="Path to the audio file to process",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s:%(name)s: %(message)s'
    )

    config = load_config('config.yaml')

    model_name = config.get('whisper_model', 'base')
    session_root = config.get('session_root', 'sessions')
    audio_cfg = config.get('audio', {})

    assistant = Assistant(model_name=model_name)
    session_manager = SessionManager(root=session_root)

    try:
        session_dir = session_manager.create_today_session()
        logger.info("Session directory prepared at %s", session_dir)
    except Exception as exc:
        logger.exception("Unable to create session directory: %s", exc)
        return

    logger.info("Loaded config for '%s'", config.get('name'))
    logger.info(
        "Audio settings: bitrate=%s, format=%s",
        audio_cfg.get('bitrate'), audio_cfg.get('format')
    )
    logger.info("Using Whisper model: %s", model_name)

    try:
        result = assistant.process_audio(args.audio)
        logger.info("Processed audio: %s", result)
    except Exception as exc:
        logger.exception("Audio processing failed: %s", exc)

if __name__ == '__main__':
    main()
