"""Glicmack API — FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.routes import catalog, generate


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    # TODO: Initialize DB connection pool
    # TODO: Load catalogs from repo JSON
    yield
    # TODO: Close DB connections


app = FastAPI(
    title="Glicmack API",
    description="Text-to-Game AI — generate playable endless runners from prompts",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router, prefix="/api/v1", tags=["generation"])
app.include_router(catalog.router, prefix="/api/v1/catalog", tags=["catalog"])


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
