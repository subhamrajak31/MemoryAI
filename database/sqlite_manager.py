"""
SQLite database connection manager for MemoryAI.
"""

from __future__ import annotations

import sqlite3

from config.settings import DATABASE_DIR
from utils.logger import logger


DATABASE_PATH = DATABASE_DIR / "memoryai.db"

class SQLiteManager:
    """
    Manages SQLite database connections and schema initialization.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    """
    Manages SQLite database connections and schema initialization.
    """

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
    
        self.database_path = DATABASE_PATH
    
        self.initialize_database()
    
        self._initialized = True

    def get_connection(self) -> sqlite3.Connection:
        """
        Create and return a SQLite database connection.
        """
        try:
            connection = sqlite3.connect(self.database_path)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON;")

            logger.info(
                "Connected to SQLite database: %s",
                self.database_path,
            )

            return connection

        except sqlite3.Error as error:
            logger.exception(
                "Failed to connect to SQLite database: %s",
                error,
            )
            raise

    def initialize_database(self) -> None:
        """
        Create database tables if they do not already exist.
        """
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()

                cursor.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id TEXT PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS chat_sessions (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    );

                    CREATE TABLE IF NOT EXISTS messages (
                        id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        FOREIGN KEY (session_id)
                            REFERENCES chat_sessions(id)
                    );

                    CREATE TABLE IF NOT EXISTS memory (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        memory TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    );

                    CREATE TABLE IF NOT EXISTS documents (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        filename TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        uploaded_at TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    );
                    """
                )

                connection.commit()

                logger.info("Database schema initialized successfully.")

        except sqlite3.Error as error:
            logger.exception(
                "Failed to initialize database schema: %s",
                error,
            )
            raise