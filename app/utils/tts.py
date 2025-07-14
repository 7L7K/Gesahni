import logging
from pathlib import Path
try:  # pragma: no cover - gtts may be missing in tests
    from gtts import gTTS
except Exception:
    gTTS = None

logger = logging.getLogger(__name__)


def generate(text: str, dest: str) -> None:
    """Generate an MP3 file with ``text`` saved to ``dest``."""
    path = Path(dest)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if gTTS is None:
            raise RuntimeError("gTTS not available")
        tts = gTTS(text=text, lang="en")
        tts.save(str(path))
        logger.info("Saved TTS output to %s", path)
    except Exception as exc:
        logger.exception("TTS generation failed: %s", exc)
        raise
