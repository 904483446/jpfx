import pytest
from app.core.config import settings
from app.core.errors import AppError
from app.services.key_cipher import KeyCipher


def test_encrypt_decrypt_round_trip(monkeypatch):
    monkeypatch.setattr(
        settings,
        "api_key_encryption_secret",
        "high-entropy application encryption secret for local testing",
    )

    cipher = KeyCipher.from_settings()

    assert cipher.decrypt(cipher.encrypt("sk-example")) == "sk-example"


def test_missing_encryption_secret_raises_chinese_configuration_error(monkeypatch):
    monkeypatch.setattr(settings, "api_key_encryption_secret", None)

    with pytest.raises(AppError) as captured:
        KeyCipher.from_settings()

    assert captured.value.code == "MODEL_CONFIG_ENCRYPTION_NOT_CONFIGURED"
    assert captured.value.status_code == 500
    assert captured.value.message == "模型配置密钥加密未配置"


def test_decrypt_rejects_tampered_token_without_exposing_ciphertext(monkeypatch):
    monkeypatch.setattr(settings, "api_key_encryption_secret", "high-entropy-secret")
    cipher = KeyCipher.from_settings()
    encrypted_value = cipher.encrypt("sk-example")

    with pytest.raises(AppError) as captured:
        cipher.decrypt(f"A{encrypted_value[1:]}")

    assert captured.value.code == "MODEL_CONFIG_DECRYPTION_FAILED"
    assert captured.value.message == "模型配置密钥解密失败"


def test_decrypt_rejects_non_utf8_plaintext_without_exposing_ciphertext(monkeypatch):
    monkeypatch.setattr(settings, "api_key_encryption_secret", "high-entropy-secret")
    cipher = KeyCipher.from_settings()
    encrypted_value = cipher._cipher.encrypt(b"\xff").decode("ascii")

    with pytest.raises(AppError) as captured:
        cipher.decrypt(encrypted_value)

    assert captured.value.code == "MODEL_CONFIG_DECRYPTION_FAILED"
    assert captured.value.message == "模型配置密钥解密失败"
