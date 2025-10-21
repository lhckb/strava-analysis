import sys
from pathlib import Path
import streamlit as st

# Add the project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from util.strava_client_interface import StravaWrapper

@st.cache_data
def get_athlete_info_dict():
    _client = StravaWrapper()
    return _client.get_athlete_personal_info().model_dump()
    
@st.cache_data
def get_athlete_stats_dict():
    _client = StravaWrapper()
    return _client.get_athlete_personal_stats().model_dump()