"""
Authentication service for managing user registration and login verification.
"""

from __future__ import annotations

import bcrypt

from database.user_repository import UserRepository
from utils.helpers import generate_uuid, get_current_timestamp
from utils.logger import logger


class AuthenticationService:
    """
    Handles user authentication, password hashing, and verification.
    """

    def __init__(self, user_repository: UserRepository | None = None) -> None:
        self.user_repository = (
            user_repository if user_repository is not None else UserRepository()
        )

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashes a plain-text password using bcrypt.
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verifies a plain-text password against a stored bcrypt hash.
        """
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    def register_user(self, username: str, password: str) -> dict:
        """
        Registers a new user in the database repository.
        """
        existing_user = self.user_repository.get_user_by_username(username)
        if existing_user:
            raise ValueError(f"Username '{username}' is already taken.")

        user_id = generate_uuid()
        password_hash = self.hash_password(password)
        created_at = get_current_timestamp()

        self.user_repository.create_user(
            user_id=user_id,
            username=username,
            password_hash=password_hash,
            created_at=created_at,
        )

        logger.info("User '%s' registered successfully.", username)
        return {"id": user_id, "username": username, "created_at": created_at}

    
    def authenticate_user(self, username: str, password: str) -> dict | None:
        """
        Authenticates user credentials against the stored user record.
        """
        user = self.user_repository.get_user_by_username(username)
        if not user:
            return None

        # Handles dictionary or tuple database returns
        stored_hash = user["password_hash"] if isinstance(user, dict) else user[2]
        if self.verify_password(password, stored_hash):
            user_id = user["id"] if isinstance(user, dict) else user[0]
            uname = user["username"] if isinstance(user, dict) else user[1]
            return {"id": user_id, "username": uname}

        return None