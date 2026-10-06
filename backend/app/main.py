"""Main FastAPI application entry point for NEXUS-BTC."""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import logger
from app.core.exceptions import NexusException
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Initializing NEXUS-BTC forensic database and local schemas...")
    init_db()
    logger.info(f"NEXUS-BTC {settings.VERSION} initialized in offline-first mode.")
    yield
    logger.info("NEXUS-BTC shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Network–Entity eXplainable Unified Surveillance for Bitcoin (NTRO SIH Problem Statement 5)",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else "/api/docs",
    redoc_url="/redoc" if settings.DEBUG else "/api/redoc",
)

# Enable CORS for local Vite development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Centralized exception handler for custom domain errors
@app.exception_handler(NexusException)
async def nexus_exception_handler(request: Request, exc: NexusException):
    logger.warning(f"Domain Exception on {request.url.path}: {exc.message} (details: {exc.details})")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "details": exc.details,
            "path": request.url.path,
        },
    )


# Defensive global exception handler preventing raw stack traces
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "An internal forensic processing error occurred. Technical details logged server-side.",
            "path": request.url.path,
        },
    )


# Register all API endpoints
app.include_router(api_router)

# Mount frontend static distribution if built
FRONTEND_DIST = settings.PROJECT_ROOT_PATH / "frontend" / "dist"
if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path == "api":
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": True, "message": f"API endpoint '/{full_path}' not found", "path": f"/{full_path}"},
            )
        try:
            resolved_dist = FRONTEND_DIST.resolve()
            file_path = (FRONTEND_DIST / full_path).resolve()
            file_path.relative_to(resolved_dist)
            if file_path.exists() and file_path.is_file():
                return FileResponse(file_path)
        except (ValueError, Exception):
            pass
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    @app.get("/")
    def index_placeholder():
        return {
            "system": "NEXUS-BTC",
            "status": "ONLINE",
            "mode": "OFFLINE_FIRST",
            "api_documentation": "/api/docs",
            "frontend": "Run frontend development server or build frontend static dist",
        }


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("NEXUS_PORT", "8000"))
    host = os.environ.get("NEXUS_HOST", "127.0.0.1")
    uvicorn.run("app.main:app", host=host, port=port, reload=False)

