"""Assistant package exposing core classes and utilities."""

from .core import Assistant
from .gpt_worker import generate_summary
from .chat import ChatAssistant

__all__ = ["Assistant", "generate_summary", "ChatAssistant"]

