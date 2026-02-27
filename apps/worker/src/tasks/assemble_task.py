"""Assembly task — runs on the heavy 'build' queue (concurrency=1).

Takes a validated DesignSpec and assembles a configured Unity project.
"""

from src.celery_app import app


@app.task(name="src.tasks.assemble_task.assemble_project", queue="build")
def assemble_project(job_id: str, design_spec: dict, seed: int) -> dict:
    """Assemble a Unity project from a DesignSpec.

    Steps:
    1. Check idempotency cache (request_hash)
    2. Create clean workspace: /builds/{job_id}/
    3. Copy base template into workspace
    4. Write design_spec.json → StreamingAssets/
    5. Generate tile_sequence.json → StreamingAssets/
    6. Chain to build task
    """
    # TODO: Implement
    return {"status": "assembled", "job_id": job_id}
