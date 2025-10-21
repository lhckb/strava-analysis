import stravalib
from stravalib.client import BatchedResultsIterator
from stravalib.model import SummaryActivity
import os
from dotenv import load_dotenv, set_key
import time
from datetime import datetime
from util.logger_setup import get_logger

logger = get_logger()

class StravaWrapper:
    def set_all_new_env(self):
        logger.info("Freshly reading all values from .env")
        load_dotenv(override=True)
        self.STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
        self.STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
        self.STRAVA_ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")
        self.STRAVA_REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")
        self.STRAVA_TOKEN_EXPIRES_AT = float(os.getenv("STRAVA_TOKEN_EXPIRES_AT"))

    def _get_new_client(self):
        logger.info("Acquiring new client object")
        self.set_all_new_env()

        client = stravalib.Client(
            access_token=self.STRAVA_ACCESS_TOKEN, 
            refresh_token=self.STRAVA_REFRESH_TOKEN, 
            token_expires=self.STRAVA_TOKEN_EXPIRES_AT
        )
        return client

    def _pre_request_check(self):
        logger.info("Verifying token validity")
        client = self._get_new_client()
        if time.time() > float(self.STRAVA_TOKEN_EXPIRES_AT):
            new_credentials = client.refresh_access_token(
                client_id=self.STRAVA_CLIENT_ID,
                client_secret=self.STRAVA_CLIENT_SECRET,
                refresh_token=self.STRAVA_REFRESH_TOKEN
            )
            
            logger.info("Saving new credentials")
            for key, value in {
                "STRAVA_ACCESS_TOKEN": new_credentials["access_token"],
                "STRAVA_REFRESH_TOKEN": new_credentials["refresh_token"],
                "STRAVA_TOKEN_EXPIRES_AT": str(new_credentials["expires_at"])
            }.items():
                set_key(".env", key, value)

    def get_activities(
        self,
        before: datetime | str | None = None,
        after: datetime | str | None = None,
        limit: int | None = None
    ) -> BatchedResultsIterator[SummaryActivity]:
        self._pre_request_check()
        client = self._get_new_client()

        logger.info("Getting activities")
        return client.get_activities(before, after, limit)
    
    def get_athlete_personal_info(self):
        self._pre_request_check()
        client = self._get_new_client()

        return client.get_athlete()
    
    def get_athlete_personal_stats(self):
        self._pre_request_check()
        client = self._get_new_client()

        return client.get_athlete_stats()