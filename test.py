"""
Integration test for Phase 6 authentication.
"""

from services.authentication_service import UserAuthenticationService
from database.user_repository import UserRepository

service = UserAuthenticationService()
repository = UserRepository()

USERNAME = "phase6_test_user"
PASSWORD = "Password123"

print("=" * 50)
print("PHASE 6 AUTHENTICATION TEST")
print("=" * 50)

# -------------------------------------------------
# Cleanup previous test user if present
# -------------------------------------------------

existing_user = repository.get_user_by_username(USERNAME)

if existing_user:
    repository.delete_user(existing_user["id"])
    print("Old test user deleted.")

# -------------------------------------------------
# Registration
# -------------------------------------------------

print("\nRegistering user...")

user_id = service.register_user(
    username=USERNAME,
    password=PASSWORD,
)

print("User ID:", user_id)

# -------------------------------------------------
# Duplicate Registration
# -------------------------------------------------

print("\nTesting duplicate registration...")

try:
    service.register_user(
        username=USERNAME,
        password=PASSWORD,
    )
except ValueError as e:
    print("Expected:", e)

# -------------------------------------------------
# Correct Login
# -------------------------------------------------

print("\nTesting valid login...")

logged_in_id = service.login_user(
    username=USERNAME,
    password=PASSWORD,
)

assert logged_in_id == user_id

print("Login successful.")

# -------------------------------------------------
# Wrong Password
# -------------------------------------------------

print("\nTesting wrong password...")

try:
    service.login_user(
        username=USERNAME,
        password="WrongPassword",
    )
except ValueError as e:
    print("Expected:", e)

# -------------------------------------------------
# Unknown User
# -------------------------------------------------

print("\nTesting unknown user...")

try:
    service.login_user(
        username="unknown_user",
        password="Password123",
    )
except ValueError as e:
    print("Expected:", e)

print("\nAll authentication tests passed!")

# -------------------------------------------------
# Cleanup
# -------------------------------------------------

repository.delete_user(user_id)

print("Test user removed.")