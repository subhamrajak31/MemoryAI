"""
Application-wide constants.

This file stores values that are fixed across the application.
If a value is expected to change between environments,
it belongs in settings.py instead.
"""

APP_NAME = "MemoryAI"
APP_VERSION = "1.0.0"

SUPPORTED_DOCUMENT_TYPES = [
    ".pdf",
    ".docx",
]

MAX_CHAT_HISTORY = 20

MAX_USERNAME_LENGTH = 30
MIN_PASSWORD_LENGTH = 8

DEFAULT_CHAT_TITLE = "New Chat"