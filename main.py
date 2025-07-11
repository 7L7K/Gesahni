"""Entry point for running the assistant."""
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
    except Exception as exc:  # pragma: no cover - simple script
        logger.exception("Failed to load configuration: %s", exc)
        return {}


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    config = load_config('config.yaml')
    assistant = Assistant()
    session_manager = SessionManager()

    try:
        session_dir = session_manager.create_today_session()
    except Exception:
        logger.error("Unable to create session directory")
        return

    logger.info("Loaded config for %s", config.get('name'))
    logger.info("Session directory prepared at %s", session_dir)

    try:
        result = assistant.process_audio('sample.wav')
        logger.info("Processed audio: %s", result)
    except Exception as exc:
        logger.exception("Audio processing failed: %s", exc)


if __name__ == '__main__':
    main()

