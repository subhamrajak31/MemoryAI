"""
Base repository providing common database helper methods.
"""

from __future__ import annotations

import sqlite3

from database.sqlite_manager import SQLiteManager


class BaseRepository:
    """
    Base class for all repositories.

    Provides reusable database helper methods.
    """

    def __init__(self) -> None:
        self.db = SQLiteManager()

    def execute(
        self,
        query: str,
        parameters: tuple = (),
    ) -> None:
        """
        Execute INSERT, UPDATE or DELETE queries.
        """
        connection = self.db.get_connection()

        try:
            connection.execute(query, parameters)
            connection.commit()
        finally:
            connection.close()

    def fetch_one(
        self,
        query: str,
        parameters: tuple = (),
    ) -> sqlite3.Row | None:
        """
        Execute a query and return a single row.
        """
        connection = self.db.get_connection()

        try:
            cursor = connection.execute(query, parameters)
            return cursor.fetchone()
        finally:
            connection.close()

    def fetch_all(
        self,
        query: str,
        parameters: tuple = (),
    ) -> list[sqlite3.Row]:
        """
        Execute a query and return all rows.
        """
        connection = self.db.get_connection()

        try:
            cursor = connection.execute(query, parameters)
            return cursor.fetchall()
        finally:
            connection.close()