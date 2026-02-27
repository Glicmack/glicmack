"""Central DesignSpec schema — the contract between AI parser, validator, assembler, and API.

Every field has a default value. The AI fills what it can from the prompt; everything else
falls back to safe defaults. This file is the single source of truth for what a
"game configuration" looks like.
"""

from __future__ import annotations

import random
from typing import Optional

from pydantic import BaseModel, Field

from design_spec.enums import (
    Ability,
    CollectibleType,
    FontStyle,
    GroundType,
    HudStyle,
    LightingMood,
    Mood,
    ObstacleType,
    PatternStyle,
    PlayerArchetype,
    PostProcessing,
    PowerupType,
    ScoreDisplay,
    Setting,
    SfxPack,
    StylePack,
)


# ---------------------------------------------------------------------------
# Sub-specs
# ---------------------------------------------------------------------------


class ThemeSpec(BaseModel):
    """High-level theme extracted from the user prompt."""

    name: str = "Neon Cyber Runner"
    setting: Setting = Setting.CYBERPUNK_CITY
    mood: Mood = Mood.INTENSE
    narrative_hook: Optional[str] = None


class PlayerSpec(BaseModel):
    """Player character configuration."""

    archetype: PlayerArchetype = PlayerArchetype.RUNNER
    model_variant: str = "default"
    abilities: list[Ability] = Field(default_factory=lambda: [Ability.JUMP, Ability.SLIDE])
    speed_base: float = Field(default=8.0, ge=4.0, le=20.0)
    lane_count: int = Field(default=3, ge=2, le=5)


class WorldSpec(BaseModel):
    """World / level generation parameters."""

    chunk_length: int = Field(default=50, ge=20, le=200)
    tile_width: float = Field(default=4.0, ge=2.0, le=10.0)
    ground_type: GroundType = GroundType.ROAD
    environment_density: float = Field(default=0.5, ge=0.0, le=1.0)
    has_elevation_changes: bool = False


class ObstacleSpec(BaseModel):
    """Obstacle placement configuration."""

    types: list[ObstacleType] = Field(
        default_factory=lambda: [ObstacleType.BARRIER, ObstacleType.GAP]
    )
    density: float = Field(default=0.3, ge=0.1, le=0.8)
    pattern_style: PatternStyle = PatternStyle.MIXED
    min_gap_tiles: int = Field(default=2, ge=1, le=5)


class CollectibleSpec(BaseModel):
    """Collectible item configuration."""

    primary_type: CollectibleType = CollectibleType.COIN
    has_powerups: bool = True
    powerup_types: list[PowerupType] = Field(
        default_factory=lambda: [PowerupType.MAGNET, PowerupType.MULTIPLIER]
    )
    spawn_rate: float = Field(default=0.4, ge=0.1, le=0.9)


class DifficultySpec(BaseModel):
    """Difficulty ramping configuration."""

    starting_difficulty: float = Field(default=0.2, ge=0.0, le=1.0)
    ramp_rate: float = Field(default=0.05, ge=0.01, le=0.2)
    max_difficulty: float = Field(default=0.9, ge=0.3, le=1.0)
    lives: int = Field(default=1, ge=1, le=5)


class StyleSpec(BaseModel):
    """Visual style configuration."""

    style_pack: StylePack = StylePack.NEON_CYBER
    color_primary: str = "#00FFFF"
    color_secondary: str = "#FF00FF"
    color_accent: str = "#FFFF00"
    lighting_mood: LightingMood = LightingMood.DARK
    post_processing: PostProcessing = PostProcessing.BLOOM_HEAVY


class AudioSpec(BaseModel):
    """Audio configuration."""

    music_track: str = "synthwave_01"
    sfx_pack: SfxPack = SfxPack.DEFAULT
    music_intensity: float = Field(default=0.7, ge=0.0, le=1.0)


class UISpec(BaseModel):
    """UI/HUD configuration."""

    hud_style: HudStyle = HudStyle.MINIMAL
    score_display: ScoreDisplay = ScoreDisplay.DISTANCE
    show_combo: bool = True
    font_style: FontStyle = FontStyle.FUTURISTIC


# ---------------------------------------------------------------------------
# Root DesignSpec
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "1.0.0"


class DesignSpec(BaseModel):
    """The complete design specification for a generated game.

    This is the central contract of the Glicmack pipeline:
    - AI parser produces it from a user prompt
    - Validators verify it's playable and sane
    - Assembler writes it as design_spec.json to StreamingAssets
    - Unity's ConfigLoader.cs reads it at runtime
    - Users can edit it directly to tweak their game
    """

    schema_version: str = SCHEMA_VERSION
    seed: int = Field(default_factory=lambda: random.randint(0, 2**31 - 1))

    theme: ThemeSpec = Field(default_factory=ThemeSpec)
    player: PlayerSpec = Field(default_factory=PlayerSpec)
    world: WorldSpec = Field(default_factory=WorldSpec)
    obstacles: ObstacleSpec = Field(default_factory=ObstacleSpec)
    collectibles: CollectibleSpec = Field(default_factory=CollectibleSpec)
    difficulty: DifficultySpec = Field(default_factory=DifficultySpec)
    style: StyleSpec = Field(default_factory=StyleSpec)
    audio: AudioSpec = Field(default_factory=AudioSpec)
    ui: UISpec = Field(default_factory=UISpec)

    def to_json_schema(cls) -> dict:
        """Return the JSON schema for Ollama structured output enforcement."""
        return cls.model_json_schema()
