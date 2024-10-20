# mev-commit explorer



# Testing purposes
1. Load the db separately `sudo docker-compose up --build db`. The db persists over time in the docker container.
2. Load the backend API `sudo docker-compose up --build backend`. Sanity check that backend APi is running with this `curl http://localhost:8000/tables/row_counts`
3. Load the frontend `sudo docker-compose up --build frontend` and access website via `http://localhost/`


 ### fastAPI
 `curl http://localhost:8000/tables`
