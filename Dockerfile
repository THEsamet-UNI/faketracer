FROM python:3.11-slim AS builder
WORKDIR /app

# Install minimal build deps in the builder only
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install into an isolated prefix
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --prefix=/install --no-cache-dir -r /app/requirements.txt

FROM python:3.11-slim
WORKDIR /app

# Runtime: keep system packages minimal (only ca-certificates)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application files
COPY . /app

ENV PATH=/usr/local/bin:$PATH
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers", "2"]
