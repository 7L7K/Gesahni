"""Simple GPT worker placeholder.

This module emulates a background process that reads the latest transcript
for a session, generates a trivial "summary" and "next question", writes the
results to ``summary.json`` and updates ``status.json`` via ``SessionManager``.
"""

from __future__ import annotations

import json
from pathlib import Path
import logging

from src.sessions import SessionManager

logger = logging.getLogger(__name__)


def generate_summary(session_dir: str, manager: SessionManager | None = None) -> None:
    """Generate a naive summary for ``session_dir``.

    Parameters
    ----------
    session_dir:
        Path to the session directory.
    manager:
        Optional ``SessionManager`` instance used to update status. If not
        provided a default ``SessionManager`` pointing to the parent directory
        of ``session_dir`` is created.
    """

    session = Path(session_dir)
    if manager is None:
        manager = SessionManager(session.parent.as_posix())

    transcript_path = session / "transcript.txt"
    summary_path = session / "summary.json"

    try:
        text = transcript_path.read_text(encoding="utf-8")
    except Exception as exc:
        logger.exception("Failed to read transcript %s: %s", transcript_path, exc)
        return

    # Very naive summary: first 100 characters
    summary = text.strip().replace("\n", " ")[:100]
    next_question = "What would you like to discuss next?"
    data = {"summary": summary, "next_question": next_question}

    try:
        summary_path.write_text(json.dumps(data), encoding="utf-8")
        logger.info("Wrote summary to %s", summary_path)
    except Exception as exc:
        logger.exception("Failed to write summary file %s: %s", summary_path, exc)
        return

    # Update session status
    try:
        manager.write_status(session.as_posix(), True, True)
    except Exception as exc:
        logger.exception("Failed to update status for %s: %s", session, exc)

