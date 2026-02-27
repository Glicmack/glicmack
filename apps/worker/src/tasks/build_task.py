"""Build task — runs on the heavy 'build' queue (concurrency=1).

SSHs into the dedicated build machine and triggers a Unity CLI build.
"""

from src.celery_app import app


@app.task(name="src.tasks.build_task.build_project", queue="build")
def build_project(job_id: str, workspace_path: str) -> dict:
    """Trigger Unity CLI build on the dedicated build machine.

    Steps:
    1. SSH to build machine
    2. Run: unity-editor -batchmode -nographics -projectPath ... -executeMethod BuildScript.Build
    3. Run smoke test: BuildScript.RunSmokeTest
    4. Archive logs (Editor.log, build_output.log, smoke_test.log) → R2
    5. If smoke test passes → chain to upload task
    6. If fails → mark job as failed, logs available for debugging
    7. Cleanup workspace
    """
    # TODO: Implement
    return {"status": "built", "job_id": job_id}
