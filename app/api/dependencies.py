from fastapi import Request, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings

settings = get_settings()

limiter = Limiter(key_func=get_remote_address, default_limits=[])

def _check_api_key(request: Request) -> None:
    """Raise 401 if API_KEY is configured and the header is wrong/missing."""
    expected = settings.api_key
    if not expected:
        return  # Auth disabled
    provided = request.headers.get("X-API-Key", "")
    if provided != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header.",
        )
