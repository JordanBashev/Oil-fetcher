from fastapi import Request

from app.config import ACCESS_TOKEN_COOKIE_NAME, ACCESS_TOKEN_TYPE
from app.utils.tokens import TokenError, decode_token

FORWARDED_FOR_HEADER = "X-Forwarded-For"
FORWARDED_FOR_SEPARATOR = ","
UNKNOWN_CLIENT_KEY = "unknown"
USER_KEY_PREFIX = "user:"
IP_KEY_PREFIX = "ip:"


def get_client_ip(request: Request) -> str:
    """Return the original client IP, honoring X-Forwarded-For from the reverse proxy.

    Behind nginx, request.client.host is the proxy's IP (127.0.0.1), which
    would make every user share one bucket. The proxy sends the real client
    address in X-Forwarded-For; we take the first entry (the original client).
    """
    forwarded_for = request.headers.get(FORWARDED_FOR_HEADER)
    if forwarded_for:
        original_client = forwarded_for.split(FORWARDED_FOR_SEPARATOR)[0].strip()
        if original_client:
            return original_client
    if request.client is not None:
        return request.client.host
    return UNKNOWN_CLIENT_KEY


def per_ip_key(request: Request) -> str:
    return f"{IP_KEY_PREFIX}{get_client_ip(request)}"


def per_user_key(request: Request) -> str:
    """Per-user rate-limit bucket when authenticated; falls back to per-IP otherwise.

    Decodes the access-token cookie inline (no DB hit) to identify the user.
    If the cookie is missing or invalid, the caller is treated as an anonymous
    IP — they still get a limit, just shared with anyone on the same address.
    """
    access_token = request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    if access_token is not None:
        try:
            user_id = decode_token(access_token, ACCESS_TOKEN_TYPE)
            return f"{USER_KEY_PREFIX}{user_id}"
        except TokenError:
            pass
    return per_ip_key(request)
