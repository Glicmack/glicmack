FROM python:3.11-slim

WORKDIR /app

# Install design-spec package first (shared dependency)
COPY packages/design-spec /app/packages/design-spec
RUN pip install --no-cache-dir /app/packages/design-spec

# Install API dependencies
COPY apps/api/pyproject.toml /app/
RUN pip install --no-cache-dir -e .

COPY apps/api/src /app/src

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
