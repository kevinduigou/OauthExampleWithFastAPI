from typing import Any, final

from pymongo import MongoClient
from pymongo.collection import Collection
from result import Err, Ok, Result

from backend.domain.user import EmailAddress, User, ValidationToken


@final
class MongoUserRepository:
    __slots__ = ("_client", "_collection")

    def __init__(self, uri: str, db_name: str) -> None:
        self._client = MongoClient(uri)
        database = self._client[db_name]
        self._collection: Collection[Any] = database["users"]

    def create_user(self, user: User) -> Result[str, str]:
        try:
            document: dict[str, object] = {
                "hashed_password": user.hashed_password,
                "is_validated": user.is_validated,
                "validation_token": (
                    user.validation_token.value if user.validation_token else None
                ),
                "provider": user.provider,
                "provider_user_id": user.provider_user_id,
                "access_token": user.access_token,
                "refresh_token": user.refresh_token,
                "token_expires_at": user.token_expires_at,
            }
            if user.email is not None:
                document["email"] = user.email.value
            result = self._collection.insert_one(document)
            return Ok(str(result.inserted_id))
        except Exception as exc:  # noqa: BLE001
            return Err(str(exc))

    def _build_user(self, document: dict[str, object]) -> User:
        email_value = document.get("email")
        validation_token = document.get("validation_token")
        email = EmailAddress(email_value) if isinstance(email_value, str) else None
        token = (
            ValidationToken(str(validation_token))
            if isinstance(validation_token, str) and validation_token
            else None
        )

        return User(
            email=email,
            hashed_password=document.get("hashed_password"),
            is_validated=bool(document.get("is_validated", False)),
            validation_token=token,
            provider=str(document.get("provider", "")),
            provider_user_id=document.get("provider_user_id")
            if isinstance(document.get("provider_user_id"), str)
            else None,
            access_token=document.get("access_token")
            if isinstance(document.get("access_token"), str)
            else None,
            refresh_token=document.get("refresh_token")
            if isinstance(document.get("refresh_token"), str)
            else None,
            token_expires_at=document.get("token_expires_at"),
            identifier=str(document.get("_id", "")),
        )

    def find_by_email(self, email: EmailAddress) -> Result[User, str]:
        try:
            document = self._collection.find_one({"email": email.value})
            if document is None:
                return Err("User not found")

            user = self._build_user(document)
            return Ok(user)
        except Exception as exc:  # noqa: BLE001
            return Err(str(exc))

    def find_by_provider(
        self, provider: str, provider_user_id: str
    ) -> Result[User, str]:
        try:
            document = self._collection.find_one(
                {"provider": provider, "provider_user_id": provider_user_id}
            )
            if document is None:
                return Err("User not found")

            return Ok(self._build_user(document))
        except Exception as exc:  # noqa: BLE001
            return Err(str(exc))

    def validate_by_token(self, token: ValidationToken) -> Result[None, str]:
        try:
            result = self._collection.update_one(
                {"validation_token": token.value},
                {"$set": {"is_validated": True}},
            )
            if result.modified_count == 0:
                return Err("Invalid or expired token")
            return Ok(None)
        except Exception as exc:  # noqa: BLE001
            return Err(str(exc))

    def update_password_hash(
        self, email: EmailAddress, new_hash: str
    ) -> Result[None, str]:
        try:
            result = self._collection.update_one(
                {"email": email.value},
                {"$set": {"hashed_password": new_hash}},
            )
            if result.matched_count == 0:
                return Err("User not found")
            return Ok(None)
        except Exception as exc:  # noqa: BLE001
            return Err(str(exc))

    def update_oauth_user(
        self,
        provider: str,
        provider_user_id: str,
        email: EmailAddress | None,
        access_token: str | None,
        refresh_token: str | None,
        token_expires_at: object,
    ) -> Result[str, str]:
        try:
            updates: dict[str, object] = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_expires_at": token_expires_at,
                "is_validated": True,
            }
            if email is not None:
                updates["email"] = email.value
            result = self._collection.update_one(
                {"provider": provider, "provider_user_id": provider_user_id},
                {"$set": updates},
            )
            if result.matched_count == 0:
                return Err("User not found")

            lookup = self._collection.find_one(
                {"provider": provider, "provider_user_id": provider_user_id}
            )
            if lookup is None:
                return Err("User not found")

            return Ok(str(lookup.get("_id", "")))
        except Exception as exc:  # noqa: BLE001
            return Err(str(exc))
