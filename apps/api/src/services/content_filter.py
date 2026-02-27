"""Content safety filter — auto-genericify copyrighted names in prompts.

Detects copyrighted character/brand names and replaces them with generic
equivalents before sending to the LLM. Returns both original and sanitized
prompts for storage.
"""

from __future__ import annotations

from dataclasses import dataclass

# Mapping of copyrighted terms to generic replacements.
# Expand this as needed. Case-insensitive matching.
_REPLACEMENTS: dict[str, str] = {
    # Characters
    "mario": "plumber hero",
    "luigi": "tall sidekick",
    "sonic": "fast hedgehog",
    "spider-man": "web hero",
    "spiderman": "web hero",
    "batman": "dark knight hero",
    "superman": "flying hero",
    "pikachu": "electric creature",
    "pokemon": "creature collector",
    "link": "green adventurer",
    "zelda": "fantasy kingdom",
    "master chief": "armored soldier",
    "crash bandicoot": "spinning marsupial",
    "lara croft": "treasure hunter",
    "tomb raider": "treasure adventure",
    # Games/Brands
    "gta": "open city",
    "grand theft auto": "open city",
    "minecraft": "block world",
    "fortnite": "battle royale",
    "call of duty": "military shooter",
    "overwatch": "hero team",
    "league of legends": "hero arena",
    "roblox": "game platform",
    # Companies
    "nintendo": "game company",
    "disney": "animation studio",
    "marvel": "superhero universe",
    "dc comics": "superhero universe",
}


@dataclass
class FilterResult:
    """Result of content filtering."""

    original_prompt: str
    sanitized_prompt: str
    replacements_made: list[str]

    @property
    def was_modified(self) -> bool:
        return len(self.replacements_made) > 0


def filter_prompt(prompt: str) -> FilterResult:
    """Filter copyrighted content from a prompt.

    Returns the original prompt, the sanitized version, and a list of
    replacements that were made.
    """
    sanitized = prompt
    replacements: list[str] = []

    prompt_lower = prompt.lower()

    for term, replacement in _REPLACEMENTS.items():
        if term in prompt_lower:
            # Case-insensitive replacement
            import re

            pattern = re.compile(re.escape(term), re.IGNORECASE)
            sanitized = pattern.sub(replacement, sanitized)
            replacements.append(f"'{term}' → '{replacement}'")

    return FilterResult(
        original_prompt=prompt,
        sanitized_prompt=sanitized,
        replacements_made=replacements,
    )
