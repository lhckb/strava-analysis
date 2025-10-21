### Dev db run
docker run -d \
  --name strava-analysis-postgres \
  -e POSTGRES_USER=luis \
  -e POSTGRES_PASSWORD=devpassword \
  -e POSTGRES_DB=strava_analysis \
  -p 5432:5432 \
  -v strava_pg_data:/var/lib/postgresql/data \
  postgres:latest

# Job 1 - Bronze
Collect activities from n days prior
Upload to bronze table

# Job 2 - Silver
Collect activities from Bronze table, perform cleanup and transformations.
Drop unused cols, normalize data, fix data types
Push to silver table

# Job 3 - Gold
Enrich?

# All Activities
...

# Run
- longest run
- fastest pace run (avg)
- highest elevation gain
- most PRs (or achievements?)
- suffer score TS view

TREND LINE FOR ALL BELOW
- AVG HR TS view
- AVG cadence TS view
- AVG pace TS view

- plot heatmap of start and end locations
- frequency of trainer or not (treadmill)


# Cycling