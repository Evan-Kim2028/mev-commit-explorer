#!/bin/bash
# Wait for the backend API to be available
until curl -s http://backend_api:8000/tables/row_counts; do
  echo "Waiting for backend API..."
  sleep 5
done

# Start the Nginx server (or whatever server you're using)
nginx -g "daemon off;"