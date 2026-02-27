"""Project assembler — orchestrates DesignSpec → configured Unity project.

This is the core pipeline orchestrator. It:
1. Creates an isolated workspace
2. Copies the template
3. Writes JSON configs (design_spec.json + tile_sequence.json)
4. Triggers the Unity build on the dedicated build machine
5. Archives logs
6. Packages output (build ZIP + mod kit ZIP)
7. Cleans up the workspace
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from design_spec.models import DesignSpec

from .tile_generator import TileGenerator


@dataclass
class AssemblyResult:
    """Result of project assembly."""

    workspace_path: str
    design_spec_path: str
    tile_sequence_path: str
    request_hash: str
    safe_mode_activated: bool


class ProjectAssembler:
    """Assembles a configured Unity project from a DesignSpec."""

    def __init__(
        self,
        template_path: str,
        builds_root: str,
        tile_catalog: dict,
    ):
        self.template_path = Path(template_path)
        self.builds_root = Path(builds_root)
        self.tile_catalog = tile_catalog
        self.tile_generator = TileGenerator(tile_catalog)

    def compute_request_hash(
        self,
        sanitized_prompt: str,
        seed: int,
        template_commit: str,
        tile_catalog_version: str,
        style_catalog_version: str,
    ) -> str:
        """Compute idempotency hash for a generation request."""
        payload = f"{sanitized_prompt}|{seed}|{template_commit}|{tile_catalog_version}|{style_catalog_version}"
        return hashlib.sha256(payload.encode()).hexdigest()

    def assemble(self, spec: DesignSpec, job_id: str) -> AssemblyResult:
        """Assemble a configured Unity project.

        Creates a clean workspace, copies template, writes JSON configs,
        generates tile sequences.
        """
        # 1. Create isolated workspace
        workspace = self.builds_root / job_id
        workspace.mkdir(parents=True, exist_ok=True)

        project_dir = workspace / "project"

        # 2. Copy template
        shutil.copytree(
            self.template_path,
            project_dir,
            dirs_exist_ok=True,
        )

        # 3. Write design_spec.json
        streaming_assets = project_dir / "Assets" / "StreamingAssets"
        streaming_assets.mkdir(parents=True, exist_ok=True)

        spec_path = streaming_assets / "design_spec.json"
        spec_path.write_text(spec.model_dump_json(indent=2))

        # 4. Generate and write tile_sequence.json
        gen_result = self.tile_generator.generate(spec)
        tile_path = streaming_assets / "tile_sequence.json"
        tile_path.write_text(self.tile_generator.to_json(gen_result))

        # 5. Compute request hash
        request_hash = self.compute_request_hash(
            sanitized_prompt="",  # Will be passed from task
            seed=spec.seed,
            template_commit="HEAD",  # Will be resolved from git
            tile_catalog_version=self.tile_catalog.get("catalog_version", "unknown"),
            style_catalog_version="1.0.0",
        )

        return AssemblyResult(
            workspace_path=str(workspace),
            design_spec_path=str(spec_path),
            tile_sequence_path=str(tile_path),
            request_hash=request_hash,
            safe_mode_activated=gen_result.safe_mode_activated,
        )

    def cleanup(self, job_id: str) -> None:
        """Remove workspace after build completion/failure."""
        workspace = self.builds_root / job_id
        if workspace.exists():
            shutil.rmtree(workspace)
