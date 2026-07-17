from datetime import datetime
from uuid import uuid4


def generate_uuid() -> str:
    """Generate a unique ID."""
    return str(uuid4())


def get_current_timestamp() -> str:
    """Return current timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def sanitize_filename(filename: str) -> str:
    """Remove spaces from filename."""
    return filename.replace(" ", "_")