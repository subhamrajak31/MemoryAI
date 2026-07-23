"""
Business logic for user authentication.
"""
from __future__ import annotations
from utils.helpers import (
    generate_uuid,
    get_current_timestamp,
)
from database.user_repository import UserRepository
from services.auth_service import AuthenticationService
from utils.validators import (
    is_valid_username,
    is_valid_password,
)
from services.session_manager import SessionManager

class UserAuthenticationService:
    """
    Handles user registration and login.
    """

    def __init__(self) -> None:
        self.user_repository = UserRepository()

    def register_user(
        self,
        username: str,
        password: str,
    ) -> str:
        """
        Register a new user.

        Returns:
            User ID
        """

        if not is_valid_username(username):
            raise ValueError("Invalid username.")

        if not is_valid_password(password):
            raise ValueError("Invalid password.")

        if self.user_repository.user_exists(username):
            raise ValueError("Username already exists.")

        user_id = generate_uuid()
        created_at = get_current_timestamp()

        password_hash = AuthenticationService.hash_password(password)

        self.user_repository.create_user(
            user_id=user_id,
            username=username,
            password_hash=password_hash,
            created_at=created_at,
        )

        return user_id

    def login_user(
        self,
        username: str,
        password: str,
    ) -> str:
        """
        Authenticate a user.

        Returns:
            User ID
        """

        user = self.user_repository.get_user_by_username(username)

        if user is None:
            raise ValueError("Invalid username or password.")

        if not AuthenticationService.verify_password(
            password,
            user["password_hash"],
        ):
            raise ValueError("Invalid username or password.")

        SessionManager.login(
        user_id=user["id"],
        username=user["username"],
        )

        return user["id"]