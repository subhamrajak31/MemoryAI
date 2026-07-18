"""
User repository for database operations related to users.
"""

from __future__ import annotations

import sqlite3

from database.base_repository import BaseRepository
from utils.logger import logger


class UserRepository(BaseRepository):

    def create_user(
        self,
        user_id: str,
        username: str,
        password_hash: str,
        created_at: str,
    ) -> None:
        """
        Insert a new user into the database.
        """
        query = """
        INSERT INTO users (
            id,
            username,
            password_hash,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """

        try:
            with self.db.get_connection() as connection:
                connection.execute(
                    query,
                    (
                        user_id,
                        username,
                        password_hash,
                        created_at,
                    ),
                )

                connection.commit()

                logger.info(
                    "User '%s' created successfully.",
                    username,
                )

        except sqlite3.IntegrityError:
            logger.exception(
                "Username '%s' already exists.",
                username,
            )
            raise

        except sqlite3.Error:
            logger.exception(
                "Failed to create user '%s'.",
                username,
            )
            raise
    def get_user_by_username(self, username: str) -> sqlite3.Row | None:
        """
        Retrieve a user by username.
        """
        query = """
        SELECT *
        FROM users
        WHERE username = ?
        """

        try:
            with self.db.get_connection() as connection:
                cursor = connection.execute(query, (username,))
                return cursor.fetchone()

        except sqlite3.Error:
            logger.exception(
                "Failed to retrieve user '%s'.",
                username,
            )
            raise

    def get_user_by_id(self, user_id: str) -> sqlite3.Row | None:
        """
        Retrieve a user by ID.
        """
        query = """
        SELECT *
        FROM users
        WHERE id = ?
        """

        try:
            with self.db.get_connection() as connection:
                cursor = connection.execute(query, (user_id,))
                return cursor.fetchone()

        except sqlite3.Error:
            logger.exception(
                "Failed to retrieve user with ID '%s'.",
                user_id,
            )
            raise

    def user_exists(self, username: str) -> bool:
        """
        Check whether a username already exists.
        """
        return self.get_user_by_username(username) is not None
        def update_password(
        self,
        user_id: str,
        password_hash: str,
    ) -> None:
            """
            Update a user's password hash.
            """
            query = """
            UPDATE users
            SET password_hash = ?
            WHERE id = ?
            """

            try:
                with self.db.get_connection() as connection:
                    connection.execute(
                        query,
                        (
                            password_hash,
                            user_id,
                        ),
                    )

                    connection.commit()

                    logger.info(
                        "Password updated for user ID '%s'.",
                        user_id,
                    )

            except sqlite3.Error:
                logger.exception(
                    "Failed to update password for user ID '%s'.",
                    user_id,
                )
                raise

    def delete_user(self, user_id: str) -> None:
        """
        Delete a user by ID.
        """
        query = """
        DELETE FROM users
        WHERE id = ?
        """

        try:
            with self.db.get_connection() as connection:
                connection.execute(query, (user_id,))
                connection.commit()

                logger.info(
                    "User '%s' deleted successfully.",
                    user_id,
                )

        except sqlite3.Error:
            logger.exception(
                "Failed to delete user '%s'.",
                user_id,
            )
            raise

    def get_all_users(self) -> list[sqlite3.Row]:
        """
        Retrieve all users.
        """
        query = """
        SELECT *
        FROM users
        ORDER BY created_at ASC
        """

        try:
            with self.db.get_connection() as connection:
                cursor = connection.execute(query)
                return cursor.fetchall()

        except sqlite3.Error:
            logger.exception(
                "Failed to retrieve users."
            )
            raise