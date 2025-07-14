"""Simple GPT worker placeholder.

This module emulates a background process that reads the latest transcript
for a session, generates a trivial "summary" and "next question", writes the
results to ``summary.json`` and updates ``status.json`` via ``SessionManager``.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

try:  # Optional dependency
    import openai
    from openai.error import OpenAIError, RateLimitError
except Exception:  # pragma: no cover - library may be missing in tests
    openai = None
    OpenAIError = Exception
    RateLimitError = Exception

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

    summary = None
    next_question = "What would you like to discuss next?"

    if openai is not None:
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Summarize the following transcript in a single sentence.",
                    },
                    {"role": "user", "content": text},
                ],
                max_tokens=60,
            )
            summary = resp["choices"][0]["message"]["content"].strip()
        except RateLimitError as exc:  # pragma: no cover - depends on API
            logger.warning("OpenAI rate limited: %s", exc)
        except OpenAIError as exc:  # pragma: no cover - depends on API
            logger.exception("OpenAI error: %s", exc)
        except Exception as exc:  # pragma: no cover - unexpected
            logger.exception("Unexpected OpenAI failure: %s", exc)

    if not summary:
        # Very naive summary: first 100 characters
        summary = text.strip().replace("\n", " ")[:100]

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

