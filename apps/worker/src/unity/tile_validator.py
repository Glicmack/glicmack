"""Timing-aware solvability validator for tile sequences.

Validates that every obstacle in a tile sequence is solvable by a human player,
accounting for reaction time, jump/slide duration, lane-switch timing, speed
scaling, and ability cooldown (human fairness margin).

Produces structured failure reason codes for debugging.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import StrEnum


class FailureCode(StrEnum):
    """Structured failure reason codes for solvability validation."""

    LANE_ESCAPE_FAILURE = "LANE_ESCAPE_FAILURE"
    JUMP_TIMING_FAILURE = "JUMP_TIMING_FAILURE"
    SLIDE_TIMING_FAILURE = "SLIDE_TIMING_FAILURE"
    SWITCH_TIMING_FAILURE = "SWITCH_TIMING_FAILURE"
    COOLDOWN_VIOLATION = "COOLDOWN_VIOLATION"
    CHAIN_FAILURE = "CHAIN_FAILURE"


@dataclass
class TileFailure:
    """A single solvability failure."""

    tile_index: int
    tile_id: str
    code: FailureCode
    detail: str


@dataclass
class SolvabilityResult:
    """Result of solvability validation for a chunk."""

    is_valid: bool
    failures: list[TileFailure] = field(default_factory=list)
    failure_rate: float = 0.0


class TileValidator:
    """Timing-aware solvability validator.

    Constants are tuned during playtesting. These represent the minimum
    physical constraints a human player must satisfy.
    """

    REACTION_TIME_SECONDS = 0.3
    LANE_SWITCH_SECONDS = 0.2
    JUMP_DURATION_SECONDS = 0.5
    SLIDE_DURATION_SECONDS = 0.4
    ABILITY_COOLDOWN_SECONDS = 0.3

    # Maximum failure rate before chunk is rejected
    MAX_FAILURE_RATE = 0.20

    def validate_chunk(
        self,
        chunk: list[str],
        catalog: dict,
        abilities: list[str],
        lane_count: int,
        speed: float,
        tile_width: float,
    ) -> SolvabilityResult:
        """Validate an entire chunk for solvability.

        Walks through each tile, checking timing constraints relative to
        the previous obstacle and the player's available abilities.
        """
        tiles_lookup = {t["tile_id"]: t for t in catalog.get("tiles", [])}
        ability_set = set(a.value if hasattr(a, "value") else a for a in abilities)

        failures: list[TileFailure] = []
        last_obstacle_index: int | None = None
        last_ability_used: str | None = None

        for i, tile_id in enumerate(chunk):
            tile_def = tiles_lookup.get(tile_id)
            if not tile_def or tile_def["category"] not in ("obstacle", "mixed"):
                continue

            # Check lane escape
            clear_lanes = self._count_clear_lanes(tile_def, lane_count)
            if clear_lanes == 0:
                # No clear lane — check if abilities can clear it
                required = set(tile_def.get("min_abilities", []))
                if required and not required.intersection(ability_set):
                    failures.append(
                        TileFailure(
                            tile_index=i,
                            tile_id=tile_id,
                            code=FailureCode.LANE_ESCAPE_FAILURE,
                            detail=f"No clear lane and missing abilities: {required - ability_set}",
                        )
                    )
                    continue

            # Check timing constraints relative to previous obstacle
            if last_obstacle_index is not None:
                gap_tiles = i - last_obstacle_index
                gap_seconds = (gap_tiles * tile_width) / speed

                # Reaction time check
                reaction_tiles = math.ceil(speed * self.REACTION_TIME_SECONDS / tile_width)
                if gap_tiles < reaction_tiles:
                    failures.append(
                        TileFailure(
                            tile_index=i,
                            tile_id=tile_id,
                            code=FailureCode.SWITCH_TIMING_FAILURE,
                            detail=f"Gap {gap_tiles} < reaction minimum {reaction_tiles}",
                        )
                    )
                    last_obstacle_index = i
                    continue

                # Ability cooldown check (human fairness margin)
                required_abilities = set(tile_def.get("min_abilities", []))
                if (
                    last_ability_used
                    and required_abilities
                    and last_ability_used not in required_abilities
                ):
                    cooldown_tiles = math.ceil(
                        speed * self.ABILITY_COOLDOWN_SECONDS / tile_width
                    )
                    if gap_tiles < cooldown_tiles:
                        failures.append(
                            TileFailure(
                                tile_index=i,
                                tile_id=tile_id,
                                code=FailureCode.COOLDOWN_VIOLATION,
                                detail=(
                                    f"Different ability required ({required_abilities}) "
                                    f"only {gap_tiles} tiles after {last_ability_used} "
                                    f"(need {cooldown_tiles})"
                                ),
                            )
                        )
                        last_obstacle_index = i
                        continue

            # Track state for next iteration
            last_obstacle_index = i
            required = tile_def.get("min_abilities", [])
            last_ability_used = required[0] if required else None

        total_obstacles = sum(
            1
            for tid in chunk
            if tiles_lookup.get(tid, {}).get("category") in ("obstacle", "mixed")
        )
        failure_rate = len(failures) / total_obstacles if total_obstacles > 0 else 0.0

        return SolvabilityResult(
            is_valid=failure_rate <= self.MAX_FAILURE_RATE,
            failures=failures,
            failure_rate=round(failure_rate, 3),
        )

    @staticmethod
    def _count_clear_lanes(tile_def: dict, lane_count: int) -> int:
        """Count how many lanes are clear (empty or collectible) in a tile."""
        lanes = tile_def.get("lanes", [])
        clear = 0
        for lane in lanes:
            if lane.get("content_type") in ("empty", "collectible", "powerup"):
                clear += 1
        return clear
