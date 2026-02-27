"""Catalog endpoints — serve tile and style pack definitions loaded from repo JSON."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/tiles")
async def get_tile_catalog():
    """Return available tile definitions (loaded from packages/tile-catalog/catalog.json)."""
    # TODO: Load from catalog JSON file (cached at startup)
    return {"message": "Not implemented yet"}


@router.get("/styles")
async def get_style_packs():
    """Return available style pack definitions (loaded from packages/style-catalog/packs.json)."""
    # TODO: Load from catalog JSON file (cached at startup)
    return {"message": "Not implemented yet"}
