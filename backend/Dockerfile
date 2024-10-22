FROM ubuntu:22.04
FROM python:3.12.5-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    git \
    curl && \
    rm -rf /var/lib/apt/lists/*

# Install Rye non-interactively
RUN curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION="--yes" bash

# Set the PATH
ENV PATH="/root/.rye/bin:/root/.rye/shims:${PATH}"

# Copy project files
COPY . .

# Ensure the db_data directory has appropriate permissions
RUN mkdir -p /app/db/data && chmod -R 755 /app/db/data
# Use Rye to set up the environment
RUN rye sync

# Set up the entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]