"""Tests for the DesignSpec models."""

import json

from design_spec.models import DesignSpec, SCHEMA_VERSION
from design_spec.enums import Ability, StylePack, Setting


class TestDesignSpec:
    """Test DesignSpec creation and serialization."""

    def test_default_creation(self):
        """Default DesignSpec should be valid and have all expected fields."""
        spec = DesignSpec()
        assert spec.schema_version == SCHEMA_VERSION
        assert spec.theme.name == "Neon Cyber Runner"
        assert spec.player.lane_count == 3
        assert Ability.JUMP in spec.player.abilities
        assert spec.style.style_pack == StylePack.NEON_CYBER

    def test_json_roundtrip(self):
        """DesignSpec should survive JSON serialization and deserialization."""
        spec = DesignSpec(seed=42)
        json_str = spec.model_dump_json()
        restored = DesignSpec.model_validate_json(json_str)
        assert restored.seed == 42
        assert restored.theme.name == spec.theme.name
        assert restored.player.abilities == spec.player.abilities

    def test_schema_version_present(self):
        """JSON output must include schema_version for template API contract."""
        spec = DesignSpec()
        data = json.loads(spec.model_dump_json())
        assert "schema_version" in data
        assert data["schema_version"] == SCHEMA_VERSION

    def test_custom_values(self):
        """DesignSpec should accept custom values within constraints."""
        spec = DesignSpec(
            seed=12345,
            player={"speed_base": 12.0, "lane_count": 4, "abilities": ["jump", "dash"]},
            difficulty={"starting_difficulty": 0.1, "max_difficulty": 0.8},
            style={"style_pack": "neon_cyber", "color_primary": "#FF0000"},
        )
        assert spec.player.speed_base == 12.0
        assert spec.player.lane_count == 4
        assert spec.difficulty.max_difficulty == 0.8

    def test_json_schema_generation(self):
        """Should generate a valid JSON schema for Ollama structured outputs."""
        schema = DesignSpec.model_json_schema()
        assert "properties" in schema
        assert "schema_version" in schema["properties"]
        assert "theme" in schema["properties"]
        assert "player" in schema["properties"]
