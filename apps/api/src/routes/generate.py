"""Generation endpoints — the core API for creating games from prompts."""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class GenerateRequest(BaseModel):
    """Request body for /api/v1/generate."""

    prompt: str = Field(..., min_length=5, max_length=500)
    seed: int | None = None
    auto_approve: bool = False


class GenerateResponse(BaseModel):
    """Response for /api/v1/generate."""

    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    """Response for /api/v1/generate/{job_id}."""

    job_id: str
    status: str
    original_prompt: str
    sanitized_prompt: str | None = None
    design_spec: dict | None = None
    confidence_score: float | None = None
    artifacts: dict | None = None
    created_at: str | None = None
    completed_at: str | None = None


@router.post("/generate", response_model=GenerateResponse, status_code=202)
async def create_generation(request: GenerateRequest):
    """Submit a new game generation request.

    Flow: prompt → content filter → AI parse → validation → founder review → build
    """
    # TODO: Content filter (genericify copyrighted names)
    # TODO: Enqueue parse task on 'parse' Celery queue
    # TODO: Store job in DB with original_prompt + sanitized_prompt
    # TODO: Return job_id for polling/WebSocket

    return GenerateResponse(
        job_id="placeholder-uuid",
        status="pending",
        message="Generation request received. Use GET /generate/{job_id} to check status.",
    )


@router.get("/generate/{job_id}", response_model=JobStatusResponse)
async def get_generation_status(job_id: str):
    """Get the status and results of a generation job."""
    # TODO: Look up job in DB
    # TODO: Return current status, spec, artifacts
    raise HTTPException(status_code=404, detail="Job not found")


@router.get("/generate/{job_id}/spec")
async def get_spec(job_id: str):
    """Get the design spec for a generation job (for review)."""
    # TODO: Return the design_spec JSONB from the job
    raise HTTPException(status_code=404, detail="Job not found")


@router.patch("/generate/{job_id}/spec")
async def update_spec(job_id: str, spec_updates: dict):
    """Update the design spec (founder review edit)."""
    # TODO: Validate updates against DesignSpec schema
    # TODO: Update job's design_spec in DB
    raise HTTPException(status_code=404, detail="Job not found")


@router.post("/generate/{job_id}/approve")
async def approve_job(job_id: str):
    """Approve a spec and trigger the build pipeline."""
    # TODO: Change job status to 'assembling'
    # TODO: Enqueue build task on 'build' Celery queue
    raise HTTPException(status_code=404, detail="Job not found")


@router.get("/generate/{job_id}/logs")
async def get_build_logs(job_id: str):
    """Get build logs for a generation job (archived in R2)."""
    # TODO: Return pre-signed URLs for log files
    raise HTTPException(status_code=404, detail="Job not found")


@router.post("/parse-only")
async def parse_only(request: GenerateRequest):
    """Parse a prompt into a design spec without triggering a build.

    Useful for previewing what the AI would generate.
    """
    # TODO: Run AI parser synchronously or with short timeout
    # TODO: Return the DesignSpec + confidence score
    return {"message": "Not implemented yet"}
