FROM python:3.11-slim AS base
WORKDIR /app

# Install only minimal system deps required at runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder
WORKDIR /tmp
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel
RUN python -m pip wheel --wheel-dir /tmp/wheels -r /tmp/requirements.txt

FROM base
WORKDIR /app
# Copy wheels built in builder stage
COPY --from=builder /tmp/wheels /wheels
RUN python -m pip install --no-cache-dir /wheels/* || python -m pip install --no-cache-dir -r /tmp/requirements.txt

# copy only app sources
COPY . /app

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers", "2"]
