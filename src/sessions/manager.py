import os
import logging
from datetime import date

logger = logging.getLogger(__name__)


class SessionManager:
    """Manage session directories and files."""

    def __init__(self, root: str = "sessions"):
        self.root = root

    def create_today_session(self) -> str:
        """Create today's session folder with placeholder files."""
        today = date.today().isoformat()
        session_dir = os.path.join(self.root, today)
        try:
            os.makedirs(session_dir, exist_ok=True)
        except OSError as exc:
            logger.exception("Failed to create session directory %s: %s", session_dir, exc)
            raise

        # Create placeholder files if they don't exist
        for name in ["video.mp4", "audio.wav", "transcript.txt", "tags.json"]:
            path = os.path.join(session_dir, name)
            if not os.path.exists(path):
                try:
                    open(path, "a").close()
                except OSError as exc:
                    logger.exception("Failed to create file %s: %s", path, exc)
                    raise

        return session_dir

