### Dev db run
docker run -d \          
  --name strava-analysis-postgres \
  -e POSTGRES_USER=luis \  
  -e POSTGRES_PASSWORD=devpassword \
  -e POSTGRES_DB=strava_analysis \
  -p 5432:5432 \
  postgres:latest