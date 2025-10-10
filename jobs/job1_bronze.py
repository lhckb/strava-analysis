from util.strava_client_interface import StravaWrapper
from util.db_connection import PsycopgConnection
import argparse
from datetime import timedelta, datetime

def job1_bronze(after_days_ago: int):
    date_days_ago = datetime.now() - timedelta(days=after_days_ago)
    date_days_ago = date_days_ago.replace(hour=0, minute=0, second=0, microsecond=0) # first microsecond of the day after_days_ago

    client = StravaWrapper()
    activities_iterator = client.get_activities(after=date_days_ago)

    pg_client = PsycopgConnection()
    pg_client.insert_activities(activities_iterator)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Strava activities and insert into PostgreSQL.")
    parser.add_argument("after_days_ago", help="How many days ago to consider start of date range. Will fetch from x days ago until latest")
    
    args = parser.parse_args()
    
    job1_bronze(int(args.after_days_ago))