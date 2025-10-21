seed:
	uv run python -m scripts.seed_bronze

create_bronze:
	psql -h localhost -p 5432 -U luis -d strava_analysis -f ddl/01_create_bronze_table.sql

create_silver:
	psql -h localhost -p 5432 -U luis -d strava_analysis -f ddl/02_create_silver_table.sql

migrate_all:
	PGPASSWORD='devpassword' psql -h localhost -p 5432 -U luis -d strava_analysis -f ddl/01_create_bronze_table.sql
	PGPASSWORD='devpassword' psql -h localhost -p 5432 -U luis -d strava_analysis -f ddl/02_create_silver_table.sql

create_dev_db:
	docker run -d \
	--name strava-analysis-postgres \
	-e POSTGRES_USER=luis \
	-e POSTGRES_PASSWORD=devpassword \
	-e POSTGRES_DB=strava_analysis \
	-p 5432:5432 \
	-v strava_pg_data:/var/lib/postgresql/data \
	postgres:latest

main:
	uv run python main.py