FROM python:3.12.6-slim

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

# Use Rye to set up the environment
RUN rye sync

# Set up the entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

