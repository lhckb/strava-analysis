from util.strava_client_interface import StravaWrapper
from util.db_connection import PsycopgConnection
import argparse
from datetime import timedelta, datetime
import pandas as pd
from util.logger_setup import get_logger
import numpy as np

logger = get_logger()

def job2_silver():
    pg_client = PsycopgConnection()
    conn = pg_client.conn

    sql = "SELECT * FROM bronze_all_activity"
    logger.info(f"Executing SQL statement: {sql}")
    df = pd.read_sql(sql, conn)

    logger.info(f"Transforming dataframe")
    df = df.drop([
        "commute", 
        "device_watts", 
        "flagged", 
        "has_kudoed", 
        "hide_from_home", 
        "kilojoules", 
        "upload_id_str", 
        "workout_type", 
        "utc_offset",
        "location_city",
        "location_state",
        "location_country",
        "has_heartrate",
        "from_accepted_tag",
        "manual",
        "private",
        "type"
    ], axis=1)

    df["athlete_id"] = df["athlete"].apply(lambda x: x["id"]).astype(int)
    df["end_lat"] = df["end_latlng"].apply(lambda x: x[0] if x is not None else None).astype(float)
    df["end_lng"] = df["end_latlng"].apply(lambda x: x[1] if x is not None else None).astype(float)
    df["start_lat"] = df["start_latlng"].apply(lambda x: x[0] if x is not None else None).astype(float)
    df["start_lng"] = df["start_latlng"].apply(lambda x: x[1] if x is not None else None).astype(float)
    df["map_polyline"] = df["map"].apply(lambda x: x["summary_polyline"]).astype(str)
    df["upload_id"] = pd.to_numeric(df["upload_id"], errors='coerce').astype('Int64')
    df = df.drop([
        "athlete",
        "end_latlng",
        "start_latlng",
        "map"
    ], axis=1)

    # type casting over None values causes Nan to appear but pg connector only understands None
    df = df.replace({np.nan: None})

    pg_client.insert_activities_silver(df)


if __name__ == "__main__":
    job2_silver()