"""
CareerPilot AI - FastAPI Application Entry Point
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings

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
# Application lifecycle
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup / shutdown hooks."""
    logger.info("=" * 60)
    logger.info("  CareerPilot AI  |  v%s", settings.version)
    logger.info("  LLM Provider: %s | Model: %s", settings.llm_provider, settings.llm_model)
    logger.info("  Web Search: %s", "enabled" if settings.web_search_enabled else "disabled")
    logger.info("=" * 60)

    # Pre-warm the graph compilation
    try:
        from graph.graph import get_graph
        get_graph()
        logger.info("LangGraph workflow compiled and ready.")
    except Exception as exc:
        logger.warning("Could not pre-compile graph: %s", exc)

    yield

    logger.info("CareerPilot AI shutting down.")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    app = FastAPI(
        title="CareerPilot AI",
        description=(
            "Agentic AI Career Assistant — Analyzes resumes and job descriptions "
            "to produce skill matching, gap analysis, interview prep, and career roadmaps."
        ),
        version=settings.version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    from api.routes import router as api_router
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
