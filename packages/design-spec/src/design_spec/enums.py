"""All enumerations used in the DesignSpec schema."""

from enum import StrEnum


class Setting(StrEnum):
    CYBERPUNK_CITY = "cyberpunk_city"
    FOREST = "forest"
    SPACE = "space"
    DESERT = "desert"
    OCEAN = "ocean"
    MOUNTAIN = "mountain"


class Mood(StrEnum):
    INTENSE = "intense"
    RELAXED = "relaxed"
    MYSTERIOUS = "mysterious"
    PLAYFUL = "playful"


class PlayerArchetype(StrEnum):
    RUNNER = "runner"
    VEHICLE = "vehicle"
    ANIMAL = "animal"
    ROBOT = "robot"


class Ability(StrEnum):
    JUMP = "jump"
    SLIDE = "slide"
    DASH = "dash"
    SHIELD = "shield"


class GroundType(StrEnum):
    ROAD = "road"
    TRACK = "track"
    PATH = "path"
    BRIDGE = "bridge"


class ObstacleType(StrEnum):
    BARRIER = "barrier"
    GAP = "gap"
    WALL_LOW = "wall_low"
    WALL_HIGH = "wall_high"
    MOVING_BLOCK = "moving_block"


class PatternStyle(StrEnum):
    CLUSTERED = "clustered"
    UNIFORM = "uniform"
    MIXED = "mixed"
    PROGRESSIVE = "progressive"


class CollectibleType(StrEnum):
    COIN = "coin"
    GEM = "gem"
    ORB = "orb"
    STAR = "star"


class PowerupType(StrEnum):
    MAGNET = "magnet"
    MULTIPLIER = "multiplier"
    SHIELD = "shield"
    SPEED_BOOST = "speed_boost"


class StylePack(StrEnum):
    NEON_CYBER = "neon_cyber"
    MINIMAL_CLEAN = "minimal_clean"


class LightingMood(StrEnum):
    DARK = "dark"
    BRIGHT = "bright"
    SUNSET = "sunset"
    NEUTRAL = "neutral"


class PostProcessing(StrEnum):
    NONE = "none"
    BLOOM_LIGHT = "bloom_light"
    BLOOM_HEAVY = "bloom_heavy"
    RETRO = "retro"


class SfxPack(StrEnum):
    DEFAULT = "default"
    RETRO_8BIT = "retro_8bit"
    REALISTIC = "realistic"


class HudStyle(StrEnum):
    MINIMAL = "minimal"
    FULL = "full"
    RETRO = "retro"


class ScoreDisplay(StrEnum):
    DISTANCE = "distance"
    POINTS = "points"
    BOTH = "both"


class FontStyle(StrEnum):
    FUTURISTIC = "futuristic"
    PIXEL = "pixel"
    CLEAN = "clean"
    HANDWRITTEN = "handwritten"
