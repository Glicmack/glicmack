"""Parse task — runs on the lightweight 'parse' queue.

Takes a user prompt and produces a validated DesignSpec.
"""

from src.celery_app import app


@app.task(name="src.tasks.parse_task.parse_prompt", queue="parse")
def parse_prompt(job_id: str, sanitized_prompt: str, seed: int | None = None) -> dict:
    """Parse a prompt into a DesignSpec.

    Steps:
    1. Call Ollama with structured output
    2. Validate with Pydantic
    3. Run game logic validation
    4. Score confidence
    5. Update job in DB with spec + confidence
    6. If auto_approve and high confidence → chain to assemble task
    """
    # TODO: Implement
    return {"status": "parsed", "job_id": job_id}
