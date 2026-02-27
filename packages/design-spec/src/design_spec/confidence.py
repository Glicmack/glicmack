"""Spec confidence scoring — determines whether a parsed spec needs founder review.

A confidence score of 0.0–1.0 is computed based on how well the LLM understood
the prompt. Low-confidence specs are automatically routed to founder review.
"""

from __future__ import annotations

from dataclasses import dataclass

from design_spec.enums import StylePack
from design_spec.models import DesignSpec


@dataclass
class ConfidenceResult:
    """Confidence scoring breakdown."""

    score: float
    checks: dict[str, bool]

    @property
    def needs_review(self) -> bool:
        """Scores at or below 0.8 should be reviewed by the founder."""
        return self.score <= 0.8


# All available style packs (expand as packs are added)
_AVAILABLE_STYLE_PACKS = {pack.value for pack in StylePack}


class ConfidenceScorer:
    """Scores how confidently the LLM parsed the user prompt.

    Each check returns True (confident) or False (uncertain).
    The final score is the ratio of passing checks.
    """

    @classmethod
    def score(cls, spec: DesignSpec, had_validation_corrections: bool = False) -> ConfidenceResult:
        checks = {
            "prompt_understood": cls._check_prompt_understood(spec),
            "style_pack_valid": cls._check_style_pack_valid(spec),
            "obstacle_density_sane": cls._check_density_sane(spec),
            "abilities_present": cls._check_abilities_present(spec),
            "no_corrections_needed": not had_validation_corrections,
        }

        passing = sum(1 for v in checks.values() if v)
        score = passing / len(checks) if checks else 0.0

        return ConfidenceResult(score=round(score, 3), checks=checks)

    @staticmethod
    def _check_prompt_understood(spec: DesignSpec) -> bool:
        """Did the LLM produce a non-default theme name?"""
        return spec.theme.name != "Neon Cyber Runner"

    @staticmethod
    def _check_style_pack_valid(spec: DesignSpec) -> bool:
        """Is the selected style pack one we actually have?"""
        return spec.style.style_pack.value in _AVAILABLE_STYLE_PACKS

    @staticmethod
    def _check_density_sane(spec: DesignSpec) -> bool:
        """Is obstacle density in a reasonable range?"""
        return 0.1 <= spec.obstacles.density <= 0.7

    @staticmethod
    def _check_abilities_present(spec: DesignSpec) -> bool:
        """Does the player have at least one ability?"""
        return len(spec.player.abilities) >= 1
