from passlib.context import CryptContext

# We support both Argon2 and bcrypt.
# New hashes will use the FIRST scheme (argon2).
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
)


def hash_password(plain_password: str) -> str:
    """Hash a plain password using Argon2 (preferred) or bcrypt."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a stored hash (argon2 or bcrypt)."""
    return pwd_context.verify(plain_password, hashed_password)


def needs_rehash(hashed_password: str) -> bool:
    """Check if a stored hash should be upgraded (e.g. bcrypt → argon2)."""
    return pwd_context.needs_update(hashed_password)
