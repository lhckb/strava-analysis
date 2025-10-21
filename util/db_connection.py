import psycopg2
from psycopg2.extras import execute_values
from stravalib.model import SummaryActivity
from stravalib.client import BatchedResultsIterator
import json
from util.logger_setup import get_logger
import pandas as pd
import numpy as np

logger = get_logger()

class PsycopgConnection:
    def __init__(self):
        logger.info("Creating db connection object")
        self.conn = psycopg2.connect(
            database = "strava_analysis", 
            user = "luis", 
            host= "localhost",
            password = "devpassword",
            port = 5432
        )

    def sql(self, query: str):
        cursor = self.conn.cursor()
        logger.info("Executing sql statement")
        cursor.execute(query)
        cursor.close()
        self.conn.commit()

    def insert_activities_bronze(self, activities: BatchedResultsIterator[SummaryActivity]):
        """
        Insert activities from a BatchedResultsIterator[SummaryActivity]
        into the bronze_all_activity table.
        """
        insert_query = """
            INSERT INTO bronze_all_activity (
                id, achievement_count, athlete, athlete_count, average_speed, average_watts,
                comment_count, commute, device_watts, distance, elapsed_time, elev_high,
                elev_low, end_latlng, external_id, flagged, gear_id, has_kudoed,
                hide_from_home, kilojoules, kudos_count, manual, map, max_speed,
                max_watts, moving_time, name, photo_count, private, sport_type,
                start_date, start_date_local, start_latlng, timezone, total_elevation_gain,
                total_photo_count, trainer, type, upload_id, upload_id_str,
                weighted_average_watts, workout_type, utc_offset, location_city,
                location_state, location_country, pr_count, suffer_score, has_heartrate,
                average_heartrate, max_heartrate, average_cadence, from_accepted_tag,
                visibility
            )
            VALUES %s
            ON CONFLICT (id) DO NOTHING
        """

        # Collect rows for batch insert
        rows = []
        for activity in activities:
            a = activity.to_dict() if hasattr(activity, "to_dict") else dict(activity)

            row = (
                a.get("id"),
                a.get("achievement_count"),
                a.get("athlete").json(),
                a.get("athlete_count"),
                a.get("average_speed"),
                a.get("average_watts"),
                a.get("comment_count"),
                a.get("commute"),
                a.get("device_watts"),
                a.get("distance"),
                a.get("elapsed_time"),
                a.get("elev_high"),
                a.get("elev_low"),
                list(a.get("end_latlng").root) if a.get("end_latlng") else None,
                a.get("external_id"),
                a.get("flagged"),
                a.get("gear_id"),
                a.get("has_kudoed"),
                a.get("hide_from_home"),
                a.get("kilojoules"),
                a.get("kudos_count"),
                a.get("manual"),
                a.get("map").json(),
                a.get("max_speed"),
                a.get("max_watts"),
                a.get("moving_time"),
                a.get("name"),
                a.get("photo_count"),
                a.get("private"),
                str(a.get("sport_type").root),
                a.get("start_date"),
                a.get("start_date_local"),
                list(a.get("start_latlng").root) if a.get("start_latlng") else None,
                a.get("timezone"),
                a.get("total_elevation_gain"),
                a.get("total_photo_count"),
                a.get("trainer"),
                str(a.get("type").root),
                a.get("upload_id"),
                a.get("upload_id_str"),
                a.get("weighted_average_watts"),
                a.get("workout_type"),
                a.get("utc_offset"),
                a.get("location_city"),
                a.get("location_state"),
                a.get("location_country"),
                a.get("pr_count"),
                a.get("suffer_score"),
                a.get("has_heartrate"),
                a.get("average_heartrate"),
                a.get("max_heartrate"),
                a.get("average_cadence"),
                a.get("from_accepted_tag"),
                a.get("visibility"),
            )
            rows.append(row)

        if not rows:
            logger.info("No activities to insert, returning")
            return

        with self.conn.cursor() as cur:
            logger.info("Inserting activities from iterator")
            execute_values(cur, insert_query, rows, page_size=1000)
        self.conn.commit()

    def insert_activities_silver(self, df: pd.DataFrame):
        columns = list(df.columns)
        col_str = ', '.join(columns)

        sql = f"""
        INSERT INTO activities_silver ({col_str})
        VALUES %s
        ON CONFLICT (id) DO UPDATE
        SET {', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'id'])};
        """

        # Convert DataFrame to list of tuples
        records = [tuple(x) for x in df.where(pd.notna(df), None).to_numpy()]

        logger.info(f"Executing SQL statement: {sql}")
        with self.conn.cursor() as cur:
            execute_values(cur, sql, records)
        self.conn.commit()
