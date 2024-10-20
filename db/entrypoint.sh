#!/bin/bash
set -e

# Activate the virtual environment
source .venv/bin/activate

# Run the query_commits.py script
python pipe/query_commits.py

# Keep the container running
tail -f /dev/null