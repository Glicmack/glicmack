"""Tile sequence generation — converts a DesignSpec into tile_sequence.json.

This is the core gameplay generation logic. It produces a sequence of tile IDs
from the catalog, respecting difficulty curves, fairness constraints, and
timing-aware solvability requirements.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass

from design_spec.models import DesignSpec

from .tile_validator import SolvabilityResult, TileValidator


@dataclass
class GenerationResult:
    """Result of tile sequence generation."""

    chunks: list[list[str]]
    total_tiles: int
    safe_mode_activated: bool
    solvability_failures: list[dict]


class TileGenerator:
    """Generates tile sequences from a DesignSpec."""

    MAX_REGEN_ATTEMPTS = 3
    SAFE_MODE_DENSITY_REDUCTION = 0.2
    SAFE_MODE_SPEED_REDUCTION = 0.2

    def __init__(self, catalog: dict):
        """Initialize with tile catalog loaded from packages/tile-catalog/catalog.json."""
        self.catalog = catalog
        self.tiles_by_category = self._index_catalog(catalog)
        self.validator = TileValidator()

    def generate(self, spec: DesignSpec, num_chunks: int = 10) -> GenerationResult:
        """Generate tile sequences for the given number of chunks.

        Each chunk is independently seeded for reproducibility:
        chunk_seed = spec.seed + chunk_index
        """
        all_chunks: list[list[str]] = []
        all_failures: list[dict] = []
        safe_mode = False

        working_density = spec.obstacles.density
        working_speed = spec.player.speed_base

        for chunk_idx in range(num_chunks):
            chunk, failures, activated_safe = self._generate_chunk(
                spec=spec,
                chunk_index=chunk_idx,
                density_override=working_density if safe_mode else None,
                speed_override=working_speed if safe_mode else None,
            )
            all_chunks.append(chunk)
            all_failures.extend(failures)

            if activated_safe:
                safe_mode = True
                working_density *= (1 - self.SAFE_MODE_DENSITY_REDUCTION)
                working_speed *= (1 - self.SAFE_MODE_SPEED_REDUCTION)

        total = sum(len(c) for c in all_chunks)
        return GenerationResult(
            chunks=all_chunks,
            total_tiles=total,
            safe_mode_activated=safe_mode,
            solvability_failures=all_failures,
        )

    def _generate_chunk(
        self,
        spec: DesignSpec,
        chunk_index: int,
        density_override: float | None = None,
        speed_override: float | None = None,
    ) -> tuple[list[str], list[dict], bool]:
        """Generate a single chunk with retry and safe-mode fallback."""
        density = density_override or spec.obstacles.density
        speed = speed_override or spec.player.speed_base

        for attempt in range(self.MAX_REGEN_ATTEMPTS):
            rng = random.Random(spec.seed + chunk_index + attempt * 1000)
            chunk = self._build_chunk(spec, chunk_index, rng, density)

            result = self.validator.validate_chunk(
                chunk=chunk,
                catalog=self.catalog,
                abilities=spec.player.abilities,
                lane_count=spec.player.lane_count,
                speed=speed,
                tile_width=spec.world.tile_width,
            )

            if result.is_valid:
                return chunk, [], False

        # Safe-mode fallback: reduce density and speed
        reduced_density = density * (1 - self.SAFE_MODE_DENSITY_REDUCTION)
        rng = random.Random(spec.seed + chunk_index + 9999)
        chunk = self._build_chunk(spec, chunk_index, rng, reduced_density)
        return chunk, [{"chunk": chunk_index, "reason": "safe_mode_activated"}], True

    def _build_chunk(
        self,
        spec: DesignSpec,
        chunk_index: int,
        rng: random.Random,
        density: float,
    ) -> list[str]:
        """Build a raw tile sequence for one chunk."""
        difficulty = min(
            spec.difficulty.max_difficulty,
            spec.difficulty.starting_difficulty + (spec.difficulty.ramp_rate * chunk_index),
        )

        sequence: list[str] = []
        tiles_since_obstacle = spec.obstacles.min_gap_tiles  # Start with breathing room

        for i in range(spec.world.chunk_length):
            # Warm-up zone: first 10 tiles of chunk 0 are always safe
            if chunk_index == 0 and i < 10:
                tile = self._pick_safe_tile(rng, spec)
                tiles_since_obstacle += 1
            elif tiles_since_obstacle < spec.obstacles.min_gap_tiles:
                # Must place safe tile (fairness constraint)
                tile = self._pick_safe_tile(rng, spec)
                tiles_since_obstacle += 1
            elif rng.random() < density * difficulty:
                # Place obstacle tile
                tile = self._pick_obstacle_tile(rng, spec, difficulty)
                tiles_since_obstacle = 0
            elif rng.random() < spec.collectibles.spawn_rate:
                # Place collectible tile
                tile = self._pick_collectible_tile(rng)
                tiles_since_obstacle += 1
            else:
                tile = "empty_01"
                tiles_since_obstacle += 1

            sequence.append(tile)

        return sequence

    def _pick_safe_tile(self, rng: random.Random, spec: DesignSpec) -> str:
        """Pick a safe (empty or collectible) tile."""
        safe_tiles = self.tiles_by_category.get("empty", []) + self.tiles_by_category.get(
            "collectible", []
        )
        return rng.choice(safe_tiles) if safe_tiles else "empty_01"

    def _pick_obstacle_tile(
        self, rng: random.Random, spec: DesignSpec, difficulty: float
    ) -> str:
        """Pick an obstacle tile appropriate for current difficulty."""
        obstacles = self.tiles_by_category.get("obstacle", [])
        if not obstacles:
            return "empty_01"

        # Filter by difficulty rating
        suitable = [
            t
            for t in obstacles
            if self._get_tile_difficulty(t) <= difficulty + 0.2
        ]
        return rng.choice(suitable) if suitable else rng.choice(obstacles)

    def _pick_collectible_tile(self, rng: random.Random) -> str:
        """Pick a collectible tile."""
        collectibles = self.tiles_by_category.get("collectible", [])
        return rng.choice(collectibles) if collectibles else "collectible_center"

    def _get_tile_difficulty(self, tile_id: str) -> float:
        """Get difficulty rating for a tile from the catalog."""
        for tile in self.catalog.get("tiles", []):
            if tile["tile_id"] == tile_id:
                return tile.get("difficulty_rating", 0.5)
        return 0.5

    @staticmethod
    def _index_catalog(catalog: dict) -> dict[str, list[str]]:
        """Index tile IDs by category for fast lookup."""
        index: dict[str, list[str]] = {}
        for tile in catalog.get("tiles", []):
            cat = tile["category"]
            if cat not in index:
                index[cat] = []
            index[cat].append(tile["tile_id"])
        return index

    def to_json(self, result: GenerationResult) -> str:
        """Serialize tile sequence to JSON for StreamingAssets/tile_sequence.json."""
        return json.dumps(
            {
                "chunks": result.chunks,
                "total_tiles": result.total_tiles,
                "safe_mode_activated": result.safe_mode_activated,
            },
            indent=2,
        )
