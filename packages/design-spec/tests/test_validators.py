"""Tests for the DesignSpec game logic validators."""

from design_spec.enums import Ability, ObstacleType
from design_spec.models import DesignSpec
from design_spec.validators import DesignSpecValidator


class TestDesignSpecValidator:
    """Test game logic validation and auto-correction."""

    def test_default_spec_passes(self):
        """Default spec should pass validation without corrections."""
        spec = DesignSpec()
        result = DesignSpecValidator.validate(spec)
        assert not result.had_corrections

    def test_adds_avoidance_ability(self):
        """Player with no avoidance abilities gets jump added."""
        spec = DesignSpec(player={"abilities": ["shield"]})
        result = DesignSpecValidator.validate(spec)
        assert result.had_corrections
        assert Ability.JUMP in spec.player.abilities

    def test_clamps_density_overflow(self):
        """Density + spawn_rate > 0.95 gets scaled down."""
        spec = DesignSpec(
            obstacles={"density": 0.7},
            collectibles={"spawn_rate": 0.7},
        )
        result = DesignSpecValidator.validate(spec)
        assert result.had_corrections
        assert spec.obstacles.density + spec.collectibles.spawn_rate <= 0.95

    def test_fixes_difficulty_consistency(self):
        """starting_difficulty >= max_difficulty gets corrected."""
        spec = DesignSpec(
            difficulty={"starting_difficulty": 0.9, "max_difficulty": 0.5}
        )
        result = DesignSpecValidator.validate(spec)
        assert result.had_corrections
        assert spec.difficulty.starting_difficulty < spec.difficulty.max_difficulty

    def test_scales_gap_to_speed(self):
        """min_gap_tiles increases for faster player speeds."""
        spec = DesignSpec(
            player={"speed_base": 16.0},
            obstacles={"min_gap_tiles": 1},
        )
        result = DesignSpecValidator.validate(spec)
        assert spec.obstacles.min_gap_tiles > 1

    def test_warns_on_ability_mismatch(self):
        """Warns when obstacles require abilities the player doesn't have."""
        spec = DesignSpec(
            player={"abilities": ["jump"]},
            obstacles={"types": ["wall_low"]},
        )
        result = DesignSpecValidator.validate(spec)
        assert len(result.warnings) > 0
        assert "slide" in result.warnings[0].lower()
