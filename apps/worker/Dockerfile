FROM python:3.11-slim

WORKDIR /app

# Install design-spec package first (shared dependency)
COPY packages/design-spec /app/packages/design-spec
RUN pip install --no-cache-dir /app/packages/design-spec

# Install worker dependencies
COPY apps/worker/pyproject.toml /app/
RUN pip install --no-cache-dir -e .

COPY apps/worker/src /app/src

# Default: parse worker. Override in docker-compose for build worker.
CMD ["celery", "-A", "src.celery_app", "worker", "-Q", "parse", "-c", "2", "--loglevel=info"]
