"""
Authentication service for user registration and login.
"""

from __future__ import annotations

import bcrypt


class AuthenticationService:
    """
    Handles password hashing and verification.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain-text password.
        """
        password_bytes = password.encode("utf-8")

        salt = bcrypt.gensalt()

        password_hash = bcrypt.hashpw(password_bytes, salt)

        return password_hash.decode("utf-8")

    @staticmethod
    def verify_password(
        password: str,
        password_hash: str,
    ) -> bool:
        """
        Verify a password against its stored hash.
        """
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )