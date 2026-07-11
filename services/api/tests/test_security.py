import importlib


def test_hash_password_uses_argon2_and_verifies_plain_password():
    security = importlib.import_module("app.core.security")

    encoded = security.hash_password("correct-password")

    assert encoded != "correct-password"
    assert encoded.startswith("$argon2")
    assert security.verify_password("correct-password", encoded) is True
    assert security.verify_password("wrong-password", encoded) is False
