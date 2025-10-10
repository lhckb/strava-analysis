from util.strava_client_interface import StravaWrapper
from util.db_connection import PsycopgConnection

def main():
    client = StravaWrapper()
    all_activities_iterator = client.get_activities()

    pg_client = PsycopgConnection()
    pg_client.insert_activities(all_activities_iterator)


if __name__ == "__main__":
    main()