"""Upload task — runs on the heavy 'build' queue.

Packages and uploads build artifacts to Cloudflare R2.
"""

from src.celery_app import app


@app.task(name="src.tasks.upload_task.upload_artifacts", queue="build")
def upload_artifacts(job_id: str, workspace_path: str) -> dict:
    """Package and upload build artifacts.

    Steps:
    1. ZIP Windows build
    2. ZIP mod kit (design_spec.json + tile_sequence.json + README + THIRD_PARTY_NOTICES)
    3. Conditionally: ZIP Unity project (if asset audit gate passed)
    4. Compute SHA256 checksum of build ZIP
    5. Upload all ZIPs to R2
    6. Generate pre-signed URLs (72hr expiry)
    7. Update job in DB with artifact URLs + checksum
    8. Cleanup workspace
    """
    # TODO: Implement
    return {"status": "uploaded", "job_id": job_id}
