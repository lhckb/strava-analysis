from util.strava_client_interface import StravaWrapper
from util.db_connection import PsycopgConnection

def job1_bronze():
    client = StravaWrapper()
    activities_iterator = client.get_activities()

    pg_client = PsycopgConnection()
    pg_client.insert_activities_bronze(activities_iterator)


if __name__ == "__main__":    
    job1_bronze()