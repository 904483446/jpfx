from base64 import urlsafe_b64encode
from hashlib import sha256

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import Settings, settings
from app.core.errors import (
    model_config_decryption_failed,
    model_config_encryption_not_configured,
)


class KeyCipher:
    def __init__(self, cipher: Fernet) -> None:
        self._cipher = cipher

    @classmethod
    def from_settings(cls, configuration: Settings = settings) -> "KeyCipher":
        secret = configuration.api_key_encryption_secret
        if not secret:
            raise model_config_encryption_not_configured()

        derived_key = urlsafe_b64encode(sha256(secret.encode("utf-8")).digest())
        return cls(Fernet(derived_key))

    def encrypt(self, value: str) -> str:
        return self._cipher.encrypt(value.encode("utf-8")).decode("ascii")

    def decrypt(self, encrypted_value: str) -> str:
        try:
            return self._cipher.decrypt(encrypted_value.encode("ascii")).decode("utf-8")
        except (InvalidToken, UnicodeDecodeError, UnicodeEncodeError) as error:
            raise model_config_decryption_failed() from error
