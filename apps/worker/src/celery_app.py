"""Celery application configuration with dual queues.

Two queues:
- 'parse': lightweight workers for AI parsing + validation (concurrency=2+)
- 'build': heavy workers for Unity assembly + build (concurrency=1, serial)
"""

import os

from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery(
    "glicmack",
    broker=redis_url,
    backend=redis_url,
)

app.conf.update(
    # Task routing: each task goes to its designated queue
    task_routes={
        "src.tasks.parse_task.*": {"queue": "parse"},
        "src.tasks.assemble_task.*": {"queue": "build"},
        "src.tasks.build_task.*": {"queue": "build"},
        "src.tasks.upload_task.*": {"queue": "build"},
    },
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Task settings
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # Important for build queue fairness
)

# Auto-discover tasks in the tasks module
app.autodiscover_tasks(["src.tasks"])
