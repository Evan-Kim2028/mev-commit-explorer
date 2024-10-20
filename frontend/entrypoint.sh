#!/bin/sh
# Wait for the backend API to be available
until curl --silent --fail http://backend:8000/tables; do
  echo "Waiting for backend API..."
  sleep 5
done

# Start the Nginx server
nginx -g "daemon off;"


curl -X 'GET'   'http://backend:8000/tables'   -H 'accept: application/json'