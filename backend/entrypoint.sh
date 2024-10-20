#!/bin/bash
set -e

# Activate the virtual environment
source .venv/bin/activate

# Run the FastAPI application
exec rye run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
