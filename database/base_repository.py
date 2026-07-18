"""
Base repository for all database repositories.
"""

from __future__ import annotations

from database.sqlite_manager import SQLiteManager


class BaseRepository:
    """
    Base class for repositories.

    Provides access to the shared SQLite manager.
    """

    def __init__(self) -> None:
        self.db = SQLiteManager()