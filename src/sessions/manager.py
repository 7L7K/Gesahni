import os
from datetime import date


class SessionManager:
    """Manage session directories and files."""

    def __init__(self, root: str = "sessions"):
        self.root = root

    def create_today_session(self) -> str:
        """Create today's session folder with placeholder files."""
        today = date.today().isoformat()
        session_dir = os.path.join(self.root, today)
        os.makedirs(session_dir, exist_ok=True)

        # Create placeholder files if they don't exist
        for name in ["video.mp4", "audio.wav", "transcript.txt", "tags.json"]:
            path = os.path.join(session_dir, name)
            if not os.path.exists(path):
                open(path, "a").close()

        return session_dir

