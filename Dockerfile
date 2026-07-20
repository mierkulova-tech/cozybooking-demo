# ==============================================================================
# Dockerfile for CozyBooking Backend Service
# ==============================================================================
# Description:
#   Optimized production Dockerfile for running a Python 3.12 Django backend
#   service with Gunicorn and PostgreSQL support.
#
# Base Image:
#   python:3.12-slim
# ==============================================================================

FROM python:3.12-slim

# Prevent Python from writing pyc files to disc and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required for PostgreSQL adapter (libpq-dev)
# and Python package compilation (build-essential, pkg-config)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
        build-essential \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project source code into the container
COPY . .

# Grant execution permissions to the container entrypoint script
RUN chmod +x entrypoint.sh

# Expose port 8000 for web traffic (Gunicorn)
EXPOSE 8000

# Set the default entrypoint to the initialization and startup script
ENTRYPOINT ["./entrypoint.sh"]