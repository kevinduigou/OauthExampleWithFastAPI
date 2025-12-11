from dataclasses import dataclass
from datetime import datetime
from typing import final

from result import Err, Ok, Result


@final
@dataclass(frozen=True, slots=True)
class EmailAddress:
    value: str

    @staticmethod
    def try_create(raw_value: str) -> Result["EmailAddress", str]:
        normalized_value = raw_value.strip().lower()
        if "@" not in normalized_value:
            return Err("Email must contain '@'")
        local_part, _, domain_part = normalized_value.partition("@")
        if not local_part or not domain_part or "." not in domain_part:
            return Err("Email format is invalid")
        return Ok(EmailAddress(normalized_value))


@final
@dataclass(frozen=True, slots=True)
class ValidationToken:
    value: str

    @staticmethod
    def create(random_source: str) -> "ValidationToken":
        return ValidationToken(random_source)


@final
@dataclass(slots=True)
class User:
    email: EmailAddress | None
    hashed_password: str | None
    is_validated: bool
    validation_token: ValidationToken | None
    provider: str
    provider_user_id: str | None
    access_token: str | None = None
    refresh_token: str | None = None
    token_expires_at: datetime | None = None
    identifier: str | None = None

    def validate(self) -> None:
        self.is_validated = True
