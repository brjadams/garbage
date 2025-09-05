## Run the app using docker compose
In your terminal run: `docker compose up -d`

This will start a postgres (with pgvector for now), redis, redisinsights, api, and worker containers to operate end to end.

###### This is not ready for production. The Q naming and worker set up is neither robust or ideal at this point.
