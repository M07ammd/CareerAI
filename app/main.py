"""
CareerPilot AI - FastAPI Application Entry Point
"""

from __future__ import annotations

import logging
import sys
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import get_settings

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rate limiter (slowapi)
# ---------------------------------------------------------------------------

limiter = Limiter(key_func=get_remote_address, default_limits=[])


# ---------------------------------------------------------------------------
# Application lifecycle
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup / shutdown hooks."""
    logger.info("=" * 60)
    logger.info("  CareerPilot AI  |  v%s", settings.version)
    logger.info("  LLM: %s/%s", settings.llm_provider, settings.llm_model)
    logger.info("  Web Search: %s", "enabled" if settings.web_search_enabled else "disabled")
    logger.info("  API Key Auth: %s", "enabled" if settings.api_key else "disabled")
    logger.info("  Rate limit: %d req/min/IP on /analyze", settings.rate_limit_per_minute)
    logger.info("  Save Reports: %s", settings.save_reports)
    logger.info("=" * 60)

    try:
        from app.graph.graph import get_graph
        get_graph()
        logger.info("LangGraph workflow compiled and ready.")
    except Exception as exc:
        logger.warning("Could not pre-compile graph: %s", exc)

    yield

    logger.info("CareerPilot AI shutting down.")


# ---------------------------------------------------------------------------
# Optional API-key dependency
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Request-ID middleware (for error correlation)
# ---------------------------------------------------------------------------


class RequestIdMiddleware:
    """Attach a UUID request ID to every request and response."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            req_id = str(uuid.uuid4())
            scope["state"] = getattr(scope.get("state"), "__dict__", {})
            # Store in scope extensions so it is accessible in routes
            scope.setdefault("extensions", {})["request_id"] = req_id

            async def send_with_header(message):
                if message["type"] == "http.response.start":
                    headers = dict(message.get("headers", []))
                    headers[b"x-request-id"] = req_id.encode()
                    message = {**message, "headers": list(headers.items())}
                await send(message)

            await self.app(scope, receive, send_with_header)
        else:
            await self.app(scope, receive, send)


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    # Hide docs in production
    docs_url = "/docs" if settings.debug else None
    redoc_url = "/redoc" if settings.debug else None

    app = FastAPI(
        title="CareerPilot AI",
        description=(
            "Agentic AI Career Assistant — Analyses resumes and job descriptions "
            "to produce skill matching, gap analysis, interview prep, and career roadmaps."
        ),
        version=settings.version,
        lifespan=lifespan,
        docs_url=docs_url,
        redoc_url=redoc_url,
    )

    # Attach the rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Request-ID middleware
    app.add_middleware(RequestIdMiddleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    from app.api.routes import router as api_router
    app.include_router(api_router, prefix="/api")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
