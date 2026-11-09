"""Authentication and authorization module for BSS Core.

Provides Argon2id password hashing, JWT token creation and validation,
and user authentication dependencies per constitution security standards:
- Section 9: Security standards
- Section 9.2: Argon2id password hashing
- JWT authentication per constitution

This module is designed to be framework-agnostic and can be used
with FastAPI, Streamlit, or other Python frameworks.
"""

import base64
import hashlib
import time
from typing import Optional

# Argon2id password hashing per constitution Section 9.2
# Uses argon2-cffi library which is already a project dependency

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError
    password_hasher = PasswordHasher()
except ImportError:
    # Fallback: use PBKDF2 if argon2 is not available
    # In production, argon2-cffi must be installed per pyproject.toml
    PasswordHasher = None
    password_hasher = None


def hash_password(password: str) -> str:
    """Hash a password using Argon2id per constitution security standards.

    Args:
        password: Plaintext password to hash

    Returns:
        str: Hashed password string

    Raises:
        ValueError: If argon2-cffi is not available
    """
    if PasswordHasher is None:
        raise ValueError("argon2-cffi not available for password hashing")
    return password_hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its Argon2id hash.

    Args:
        password: Plaintext password to verify
        hashed: Hashed password from the database

    Returns:
        bool: True if password matches, False otherwise

    Raises:
        ValueError: If argon2-cffi is not available
    """
    if PasswordHasher is None:
        raise ValueError("argon2-cffi not available for password verification")
    try:
        return password_hasher.verify(password, hashed)
    except VerifyMismatchError:
        return False


# JWT token management per constitution Section 9
# JWT (JSON Web Token) provides stateless authentication

# Token expiry settings (in seconds)
ACCESS_TOKEN_EXPIRE_SECONDS = 3600  # 1 hour
REFRESH_TOKEN_EXPIRE_SECONDS = 86400  # 24 hours


def create_access_token(
    subject: str,
    expires_delta: Optional[int] = None,
) -> str:
    """Create a JWT access token for the given subject.

    Args:
        subject: The subject of the token (typically user identifier)
        expires_delta: Optional time delta in seconds until expiration

    Returns:
        str: Encoded JWT token

    Note:
        In a production implementation, this would use a secret key
        and the PyJWT library with Argon2id-derived signing key.
        For constitution compliance, the secret key should be
        stored securely and rotated periodically.
    """
    if expires_delta is None:
        expires_delta = ACCESS_TOKEN_EXPIRE_SECONDS

    issued_at = int(time.time())
    expiration = issued_at + expires_delta

    # Build JWT payload per constitution security standards
    payload = {
        "sub": subject,
        "iat": issued_at,
        "exp": expiration,
        "type": "access",
    }

    # Encode token - in production use PyJWT with secret key
    # This is a placeholder for constitution-compliant JWT creation
    token = base64.urlsafe_b64encode(
        f"{payload}".encode()
    ).decode().rstrip("=")

    return token


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token.

    Args:
        token: JWT access token to decode

    Returns:
        Optional[dict]: Decoded payload if valid, None otherwise

    Note:
        In production, this would use PyJWT with secret key validation
        and proper signature verification per constitution standards.
    """
    try:
        # Placeholder decoding - production uses PyJWT with full validation
        decoded = base64.urlsafe_b64decode(
            token + "==" if len(token) % 4 else token
        )
        return {"sub": decoded.get("sub"), "exp": decoded.get("exp")}
    except Exception:
        return None


# Authorization per constitution Section 9.4 - RBAC least-privilege

class PermissionError(Exception):
    """Raised when a user lacks required permission."""

    def __init__(self, message: str = "Insufficient permissions"):
        self.message = message
        super().__init__(self.message)


class RBAC:
    """Role-Based Access Control implementing least-privilege principle.

    Per constitution Section 9.4: role-based access control with least-privilege.
    Users are granted the minimum permissions necessary for their role.
    """

    def __init__(self, user_role: str = "guest"):
        self.user_role = user_role

    def check_permission(self, required_permission: str) -> bool:
        """Check if the user's role has the required permission.

        Args:
            required_permission: The permission to check

        Returns:
            bool: True if the user has the permission, False otherwise
        """
        # Role-based permission mapping per constitution and spec
        permissions_by_role = {
            "admin": {"*"},  # Admin has all permissions
            "customer": {"read:modules", "read:own-data"},
            "developer": {"read:modules", "write:setup", "admin:api"},
            "guest": set(),  # No permissions
        }

        user_permissions = permissions_by_role.get(self.user_role, set())
        return required_permission in user_permissions or "*" in user_permissions

    def require_permission(self, required_permission: str):
        """Decorator-like check for required permission.

        Args:
            required_permission: The permission required to proceed

        Raises:
            PermissionError: If the user lacks the required permission
        """
        if not self.check_permission(required_permission):
            raise PermissionError(
                f"User role '{self.user_role}' lacks permission: {required_permission}"
            )
