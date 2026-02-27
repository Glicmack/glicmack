"""Game logic validation for DesignSpec.

Catches semantic issues that Pydantic's structural validation can't:
- Player must have at least one avoidance ability
- Obstacle density + collectible rate can't overflow
- Difficulty parameters must be consistent
- Gap tiles must scale with speed for playability
"""

from __future__ import annotations

import math

from design_spec.enums import Ability
from design_spec.models import DesignSpec


class ValidationResult:
    """Result of game-logic validation."""

    def __init__(self) -> None:
        self.warnings: list[str] = []
        self.corrections: list[str] = []

    @property
    def had_corrections(self) -> bool:
        return len(self.corrections) > 0


class DesignSpecValidator:
    """Post-parse validation for game-logic consistency.

    Mutates the spec in-place to fix issues, and returns a log of what changed.
    """

    # Minimum reaction distance in tiles at base speed
    MIN_REACTION_TILES_PER_SPEED_UNIT = 0.25

    @classmethod
    def validate(cls, spec: DesignSpec) -> ValidationResult:
        result = ValidationResult()

        cls._ensure_avoidance_ability(spec, result)
        cls._clamp_density_overflow(spec, result)
        cls._ensure_difficulty_consistency(spec, result)
        cls._scale_gap_to_speed(spec, result)
        cls._validate_obstacle_types_for_abilities(spec, result)

        return result

    @staticmethod
    def _ensure_avoidance_ability(spec: DesignSpec, result: ValidationResult) -> None:
        """Player must have at least one of: jump, slide, dash."""
        avoidance = {Ability.JUMP, Ability.SLIDE, Ability.DASH}
        if not avoidance.intersection(spec.player.abilities):
            spec.player.abilities.append(Ability.JUMP)
            result.corrections.append(
                "Added 'jump' ability — player needs at least one avoidance ability"
            )

    @staticmethod
    def _clamp_density_overflow(spec: DesignSpec, result: ValidationResult) -> None:
        """Obstacle density + collectible spawn_rate must not exceed 0.95."""
        total = spec.obstacles.density + spec.collectibles.spawn_rate
        if total > 0.95:
            scale = 0.95 / total
            spec.obstacles.density = round(spec.obstacles.density * scale, 3)
            spec.collectibles.spawn_rate = round(spec.collectibles.spawn_rate * scale, 3)
            result.corrections.append(
                f"Scaled density ({spec.obstacles.density}) + spawn_rate "
                f"({spec.collectibles.spawn_rate}) to stay under 0.95"
            )

    @staticmethod
    def _ensure_difficulty_consistency(spec: DesignSpec, result: ValidationResult) -> None:
        """starting_difficulty must be less than max_difficulty."""
        if spec.difficulty.starting_difficulty >= spec.difficulty.max_difficulty:
            spec.difficulty.starting_difficulty = round(
                spec.difficulty.max_difficulty * 0.3, 3
            )
            result.corrections.append(
                f"Adjusted starting_difficulty to {spec.difficulty.starting_difficulty} "
                f"(must be below max_difficulty {spec.difficulty.max_difficulty})"
            )

    @classmethod
    def _scale_gap_to_speed(cls, spec: DesignSpec, result: ValidationResult) -> None:
        """min_gap_tiles must allow reaction time at the given base speed."""
        min_required = max(
            1,
            math.ceil(spec.player.speed_base * cls.MIN_REACTION_TILES_PER_SPEED_UNIT),
        )
        if spec.obstacles.min_gap_tiles < min_required:
            spec.obstacles.min_gap_tiles = min_required
            result.corrections.append(
                f"Increased min_gap_tiles to {min_required} for playability at speed "
                f"{spec.player.speed_base}"
            )

    @staticmethod
    def _validate_obstacle_types_for_abilities(
        spec: DesignSpec, result: ValidationResult
    ) -> None:
        """Warn if obstacle types require abilities the player doesn't have."""
        from design_spec.enums import ObstacleType

        ability_set = set(spec.player.abilities)

        # wall_low requires slide, wall_high requires jump
        if ObstacleType.WALL_LOW in spec.obstacles.types and Ability.SLIDE not in ability_set:
            result.warnings.append(
                "Obstacle type 'wall_low' typically requires slide ability (player doesn't have it)"
            )
        if ObstacleType.WALL_HIGH in spec.obstacles.types and Ability.JUMP not in ability_set:
            result.warnings.append(
                "Obstacle type 'wall_high' typically requires jump ability (player doesn't have it)"
            )
