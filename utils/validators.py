from pathlib import Path


def is_valid_username(username: str) -> bool:
    """Check if username is valid."""
    return len(username.strip()) >= 3


def is_valid_password(password: str) -> bool:
    """Check if password is valid."""
    return len(password) >= 8


def is_supported_file(filename: str, supported_extensions: list[str]) -> bool:
    """Check if uploaded file is supported."""
    return Path(filename).suffix.lower() in supported_extensions