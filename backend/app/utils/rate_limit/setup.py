from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.utils.rate_limit.keys import per_ip_key

limiter = Limiter(key_func=per_ip_key)


def install_rate_limit(app: FastAPI) -> None:
    """Register the limiter on the app and wire up the 429 handler.

    The limiter is exposed as a module-level singleton so route files can
    decorate their handlers with @limiter.limit(...). The middleware enforces
    the limits per request; the exception handler converts a RateLimitExceeded
    raise into a clean 429 response with a Retry-After header.
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
