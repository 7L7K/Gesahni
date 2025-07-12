"""Assistant package exposing core classes and utilities."""

from .core import Assistant
from .gpt_worker import generate_summary

__all__ = ["Assistant", "generate_summary"]