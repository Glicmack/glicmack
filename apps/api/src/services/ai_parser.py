"""LLM prompt → DesignSpec parser using Ollama structured outputs.

This is the "intelligence" of the product. It takes a natural language prompt
and produces a structured DesignSpec JSON using Ollama's format parameter
for schema-constrained generation.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from design_spec.confidence import ConfidenceResult, ConfidenceScorer
from design_spec.models import DesignSpec
from design_spec.validators import DesignSpecValidator, ValidationResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a game design parser for Glicmack, an endless runner game generator.

Your job: convert the user's natural language prompt into a structured JSON game configuration.

Rules:
- Only output valid JSON matching the schema. No explanations.
- If the user doesn't specify something, leave it as the default value.
- Map keywords to appropriate settings (e.g., "neon", "cyber" → neon_cyber style pack).
- Do NOT invent features outside the schema.
- Do NOT include copyrighted character names — use generic equivalents.
- The game is always an endless lane-based runner. Do not change the genre.

Give the game a creative, fitting name based on the prompt.
"""


class ParseResult:
    """Result of parsing a prompt into a DesignSpec."""

    def __init__(
        self,
        spec: DesignSpec,
        validation: ValidationResult,
        confidence: ConfidenceResult,
        raw_llm_output: str,
    ):
        self.spec = spec
        self.validation = validation
        self.confidence = confidence
        self.raw_llm_output = raw_llm_output


class AIParser:
    """Parses user prompts into DesignSpec using Ollama."""

    def __init__(self, ollama_host: str, model: str = "llama3.1:8b"):
        self.ollama_host = ollama_host
        self.model = model

    async def parse(
        self, prompt: str, seed: Optional[int] = None
    ) -> ParseResult:
        """Parse a user prompt into a validated DesignSpec.

        Steps:
        1. Call Ollama with structured output (format=json_schema)
        2. Parse response into DesignSpec via Pydantic
        3. Run game logic validation (auto-correct issues)
        4. Score confidence
        """
        # TODO: Implement Ollama API call
        # response = await self._call_ollama(prompt)
        # spec = DesignSpec.model_validate_json(response)

        # For now, return defaults
        spec = DesignSpec()
        if seed is not None:
            spec.seed = seed

        # Validate
        validation = DesignSpecValidator.validate(spec)

        # Score confidence
        confidence = ConfidenceScorer.score(
            spec, had_validation_corrections=validation.had_corrections
        )

        return ParseResult(
            spec=spec,
            validation=validation,
            confidence=confidence,
            raw_llm_output="{}",  # placeholder
        )

    async def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API with structured output enforcement.

        Uses httpx to POST to Ollama's /api/chat endpoint with
        format=<json_schema> for constrained generation.
        """
        import httpx

        schema = DesignSpec.model_json_schema()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.ollama_host}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    "format": schema,
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
