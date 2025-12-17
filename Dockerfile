FROM python:3.11-slim AS builder
WORKDIR /tmp

# Build dependencies (only in builder stage)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel
# Install into an isolated prefix to copy only runtime files later
RUN python -m pip install --prefix=/install --no-cache-dir -r /tmp/requirements.txt

FROM python:3.11-slim
WORKDIR /app

# Runtime libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application source (dockerignore will exclude large files)
COPY . /app

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers", "2"]
