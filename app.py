from config.constants import SUPPORTED_DOCUMENT_TYPES
from utils.validators import (
    is_valid_password,
    is_valid_username,
    is_supported_file,
)

print(is_valid_username("subham"))
print(is_valid_password("password123"))
print(is_supported_file("resume.pdf", SUPPORTED_DOCUMENT_TYPES))
print(is_supported_file("image.png", SUPPORTED_DOCUMENT_TYPES))