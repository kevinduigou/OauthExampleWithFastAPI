from datetime import datetime
from secrets import token_urlsafe
from typing import final

from result import Err, Ok, Result

from backend.domain.user import EmailAddress, User, ValidationToken
from backend.infrastructure.email_sender import BrevoEmailSender
from backend.infrastructure.user_repository import MongoUserRepository
from backend.security import hash_password, needs_rehash, verify_password


@final
class AuthService:
    __slots__ = ("_repository", "_email_sender")

    def __init__(
        self, repository: MongoUserRepository, email_sender: BrevoEmailSender
    ) -> None:
        self._repository = repository
        self._email_sender = email_sender

    def register_user(self, email_text: str, password: str) -> Result[str, str]:
        email_result = EmailAddress.try_create(email_text)
        match email_result:
            case Err(error):
                return Err(error)
            case Ok(email):
                existing_user = self._repository.find_by_email(email)
                match existing_user:
                    case Ok(_):
                        return Err("User already exists")
                    case Err(error):
                        if error != "User not found":
                            return Err(error)

                hashed = hash_password(password)
                token = ValidationToken.create(token_urlsafe(32))
                user = User(
                    email=email,
                    hashed_password=hashed,
                    is_validated=False,
                    validation_token=token,
                    provider="local",
                    provider_user_id=email.value,
                    access_token=None,
                    refresh_token=None,
                    token_expires_at=None,
                )

                creation_result = self._repository.create_user(user)
                match creation_result:
                    case Err(error):
                        return Err(error)
                    case Ok(identifier):
                        user.identifier = identifier
                        email_result = self._email_sender.send_validation_email(
                            email, token
                        )
                        match email_result:
                            case Err(email_error):
                                return Err(email_error)
                            case Ok(_):
                                return Ok(identifier)

    def validate_account(self, token_value: str) -> Result[None, str]:
        validation_token = ValidationToken(token_value)
        return self._repository.validate_by_token(validation_token)

    def authenticate(self, email_text: str, password: str) -> Result[User, str]:
        email_result = EmailAddress.try_create(email_text)
        match email_result:
            case Err(error):
                return Err(error)
            case Ok(email):
                user_result = self._repository.find_by_email(email)
                match user_result:
                    case Err(error):
                        return Err(error)
                    case Ok(user):
                        if user.provider != "local":
                            return Err("Password login not available for this account")
                        if user.hashed_password is None:
                            return Err("Password login not available for this account")
                        if not verify_password(password, user.hashed_password):
                            return Err("Invalid credentials")
                        if needs_rehash(user.hashed_password):
                            new_hash = hash_password(password)
                            update_result = self._repository.update_password_hash(
                                user.email, new_hash
                            )
                            match update_result:
                                case Err(error):
                                    return Err(error)
                        if not user.is_validated:
                            return Err("Account not validated")
                        return Ok(user)

    def register_oauth_user(
        self,
        provider: str,
        provider_user_id: str,
        email_text: str | None,
        access_token: str | None,
        refresh_token: str | None,
        token_expires_at: datetime | None,
    ) -> Result[str, str]:
        if provider.strip() == "" or provider_user_id.strip() == "":
            return Err("Missing provider identity")

        email: EmailAddress | None = None
        if email_text:
            email_result = EmailAddress.try_create(email_text)
            match email_result:
                case Err(error):
                    return Err(error)
                case Ok(valid_email):
                    email = valid_email

        existing_user = self._repository.find_by_provider(provider, provider_user_id)
        match existing_user:
            case Ok(user):
                update_result = self._repository.update_oauth_user(
                    provider,
                    provider_user_id,
                    email,
                    access_token,
                    refresh_token,
                    token_expires_at,
                )
                match update_result:
                    case Err(error):
                        return Err(error)
                    case Ok(identifier):
                        user.identifier = identifier
                        return Ok(identifier)
            case Err(error):
                if error != "User not found":
                    return Err(error)

        user = User(
            email=email,
            hashed_password=None,
            is_validated=True,
            validation_token=None,
            provider=provider,
            provider_user_id=provider_user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=token_expires_at,
        )
        creation_result = self._repository.create_user(user)
        match creation_result:
            case Err(error):
                return Err(error)
            case Ok(identifier):
                user.identifier = identifier
                return Ok(identifier)
