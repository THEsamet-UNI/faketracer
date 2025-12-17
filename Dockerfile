FROM python:3.11-slim AS builder
WORKDIR /tmp

# Build dependencies (only in builder stage)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    FROM python:3.11-slim AS builder
    WORKDIR /app

    # Build-time system deps (only in builder)
    RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        libgl1 \
        libglib2.0-0 \
        && rm -rf /var/lib/apt/lists/*

    # copy requirements and install into an isolated prefix
    COPY requirements.txt /app/requirements.txt
    RUN python -m pip install --upgrade pip setuptools wheel
    RUN pip install --prefix=/install --no-cache-dir -r /app/requirements.txt

    FROM python:3.11-slim
    WORKDIR /app

    # runtime system deps (keep small)
    RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        libgl1 \
        libglib2.0-0 \
        && rm -rf /var/lib/apt/lists/*

    # copy installed packages from builder
    COPY --from=builder /install /usr/local

    # copy application files
    COPY . /app

    ENV PATH=/usr/local/bin:$PATH
    ENV FLASK_APP=app.py
    ENV FLASK_RUN_HOST=0.0.0.0
    EXPOSE 5000

    CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers", "2"]
