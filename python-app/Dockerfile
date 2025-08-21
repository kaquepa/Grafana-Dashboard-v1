FROM python:3.11-slim-bullseye AS builder

# Install build dependencies only for compiling Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies (cached if requirements.txt hasn't changed)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Final lightweight image
FROM python:3.11-slim-bullseye

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY . .

CMD ["python", "main.py"]
