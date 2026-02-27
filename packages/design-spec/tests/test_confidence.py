"""Tests for the confidence scoring system."""

from design_spec.confidence import ConfidenceScorer
from design_spec.models import DesignSpec


class TestConfidenceScorer:
    """Test spec confidence scoring."""

    def test_default_spec_low_confidence(self):
        """Default spec should have low confidence (LLM didn't parse anything)."""
        spec = DesignSpec()
        result = ConfidenceScorer.score(spec)
        # Default theme name means "prompt_understood" fails
        assert result.score < 1.0
        assert not result.checks["prompt_understood"]

    def test_custom_spec_high_confidence(self):
        """Spec with non-default theme should have higher confidence."""
        spec = DesignSpec(
            theme={"name": "Dark Neon Highway"},
        )
        result = ConfidenceScorer.score(spec)
        assert result.checks["prompt_understood"]

    def test_corrections_reduce_confidence(self):
        """Specs that needed corrections should score lower."""
        spec = DesignSpec(theme={"name": "My Custom Game"})
        result_clean = ConfidenceScorer.score(spec, had_validation_corrections=False)
        result_corrected = ConfidenceScorer.score(spec, had_validation_corrections=True)
        assert result_corrected.score < result_clean.score

    def test_needs_review_threshold(self):
        """Scores below 0.8 should need review."""
        spec = DesignSpec()  # Default = low confidence
        result = ConfidenceScorer.score(spec)
        assert result.needs_review
