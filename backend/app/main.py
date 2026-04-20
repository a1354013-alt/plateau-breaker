from __future__ import annotations

import os
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.api import analytics_router, health_records_router, profile_router, report_router
from app.database import create_db_and_tables
from app.version import get_version_info


def _parse_cors_origins(value: str | None) -> list[str]:
    """Comma-separated origins via env (e.g. "https://app.example.com,https://admin.example.com")."""

    if not value or not value.strip():
        # Default dev (Vite) + preview (vite preview) ports.
        return [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4173",
            "http://127.0.0.1:4173",
        ]

    origins = [o.strip() for o in value.split(",") if o.strip()]
    return origins or ["http://localhost:5173", "http://127.0.0.1:5173"]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    yield


_version = get_version_info()
_api_name = f"{_version.name} API"


class _SpaFallbackMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, *, index_html: Path, api_prefix: str = "/api"):
        super().__init__(app)
        self._index_html = index_html
        self._api_prefix = api_prefix

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)

        if request.method != "GET":
            return response

        path = request.url.path
        if path.startswith(self._api_prefix):
            return response

        if response.status_code != 404:
            return response

        accept = request.headers.get("accept", "")
        if "text/html" not in accept and "*/*" not in accept:
            return response

        if not self._index_html.exists():
            return response

        return FileResponse(self._index_html)


def create_app() -> FastAPI:
    api = FastAPI(
        title=_api_name,
        description="Rule-based health analytics backend for weight plateau analysis",
        version=_version.version,
        lifespan=lifespan,
    )

    cors_origins = _parse_cors_origins(os.getenv("CORS_ORIGINS"))
    allow_credentials = True
    if "*" in cors_origins:
        cors_origins = ["*"]
        # CORS forbids allow_credentials with wildcard origins.
        allow_credentials = False

    api.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    api.include_router(health_records_router)
    api.include_router(analytics_router)
    api.include_router(profile_router)
    api.include_router(report_router)

    @api.get("/api/meta")
    def api_meta() -> dict[str, str]:
        return {
            "name": _api_name,
            "version": _version.version,
            "docs": "/docs",
        }

    @api.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    dist_dir = Path(
        os.getenv("PLATEAUBREAKER_FRONTEND_DIST_DIR")
        or (Path(__file__).resolve().parent / "static" / "dist")
    ).resolve()
    index_html = dist_dir / "index.html"

    if dist_dir.exists() and index_html.exists():
        # Serve the built SPA when available (e.g. in Docker/prod builds).
        # This must be registered AFTER API routes like /health to avoid shadowing them.
        api.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend")
        api.add_middleware(_SpaFallbackMiddleware, index_html=index_html)

    return api


app = create_app()
