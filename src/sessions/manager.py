import os
import logging
import json
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
        for name in [
            "video.webm",
            "audio.wav",
            "transcript.txt",
            "tags.json",
            "status.json",
            "summary.json",
        ]:
            path = os.path.join(session_dir, name)
            if not os.path.exists(path):
                try:
                    open(path, "a").close()
                except OSError as exc:
                    logger.exception("Failed to create file %s: %s", path, exc)
                    raise

        return session_dir

    def get_latest_session(self):
        """Return the most recent session directory or ``None`` if none exist."""
        try:
            dirs = [
                d
                for d in os.listdir(self.root)
                if os.path.isdir(os.path.join(self.root, d))
            ]
        except OSError as exc:
            logger.exception("Failed to list sessions in %s: %s", self.root, exc)
            return None

        if not dirs:
            return None

        latest = sorted(dirs)[-1]
        return os.path.join(self.root, latest)

    def write_status(self, session_dir: str, whisper_done: bool, gpt_done: bool) -> None:
        """Write status information to ``session_dir/status.json``."""
        path = os.path.join(session_dir, "status.json")
        data = {"whisper_done": whisper_done, "gpt_done": gpt_done}
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh)
        except Exception as exc:
            logger.exception("Failed to write status file %s: %s", path, exc)
            raise

        return None

