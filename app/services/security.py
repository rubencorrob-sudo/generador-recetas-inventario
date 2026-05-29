import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from app.config import settings


class TokenError(ValueError):
    pass


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    iterations = 260_000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return (
        f"pbkdf2_sha256${iterations}$"
        f"{base64.b64encode(salt).decode()}$"
        f"{base64.b64encode(digest).decode()}"
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt, digest = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        computed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            base64.b64decode(salt),
            int(iterations),
        )
        return hmac.compare_digest(computed, base64.b64decode(digest))
    except (ValueError, TypeError):
        return False


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(
            (now + timedelta(minutes=settings.access_token_expire_minutes)).timestamp()
        ),
    }
    if extra:
        payload.update(extra)

    header = {"alg": "HS256", "typ": "JWT"}
    header_part = _b64url_encode(
        json.dumps(header, separators=(",", ":")).encode("utf-8")
    )
    payload_part = _b64url_encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    signing_input = f"{header_part}.{payload_part}".encode("utf-8")
    signature = hmac.new(
        settings.secret_key.encode("utf-8"), signing_input, hashlib.sha256
    ).digest()
    return f"{header_part}.{payload_part}.{_b64url_encode(signature)}"


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        header_part, payload_part, signature_part = token.split(".")
    except ValueError as exc:
        raise TokenError("Token JWT mal formado") from exc

    signing_input = f"{header_part}.{payload_part}".encode("utf-8")
    expected_signature = hmac.new(
        settings.secret_key.encode("utf-8"), signing_input, hashlib.sha256
    ).digest()
    try:
        signature = _b64url_decode(signature_part)
    except ValueError as exc:
        raise TokenError("Firma JWT invalida") from exc
    if not hmac.compare_digest(signature, expected_signature):
        raise TokenError("Firma JWT invalida")

    try:
        header = json.loads(_b64url_decode(header_part))
        payload = json.loads(_b64url_decode(payload_part))
    except (ValueError, json.JSONDecodeError) as exc:
        raise TokenError("Token JWT invalido") from exc

    if header.get("alg") != "HS256":
        raise TokenError("Algoritmo JWT no soportado")
    if int(payload.get("exp", 0)) < int(datetime.now(UTC).timestamp()):
        raise TokenError("Token JWT expirado")
    return payload

