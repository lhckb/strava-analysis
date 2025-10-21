import pandas as pd
import sys
from pathlib import Path
import streamlit as st
import altair as alt
import polyline
import pydeck as pdk

# Add the project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from util.db_connection import PsycopgConnection
from util.logger_setup import get_logger

logger = get_logger()

# cache for 12 hours
@st.cache_data(ttl=3600*12)
def get_silver_data_from_pg():
    pg_client = PsycopgConnection()
    conn = pg_client.conn

    sql = "SELECT * FROM activities_silver"
    logger.info(f"[DASHBOARD] Executing SQL statement: {sql}")
    df = pd.read_sql(sql, conn)

    return df



@st.cache_data
def get_bar_plot_sport_count(df: pd.DataFrame):
    sport_counts = df["sport_type"].value_counts().reset_index()
    sport_counts.columns = ["sport_type", "count"]

    # --- Create bar chart using Altair ---
    bars = (
        alt.Chart(sport_counts)
        .mark_bar()
        .encode(
            x=alt.X("sport_type", title=""),
            y=alt.Y(
                "count", 
                title="",
                axis=alt.Axis(
                    grid=True,
                    gridDash=[4,4],       # make grid lines dotted
                    tickMinStep=20        # spacing of ticks every 20
                ),
            ),
            color="sport_type",
            # tooltip=["sport_type", "count"]
            tooltip=[
                alt.Tooltip("sport_type", title="Sport"),
                alt.Tooltip("count", title="Count")
            ],
        )
    )

    # Add text labels on top of the bars
    text = (
        alt.Chart(sport_counts)
        .mark_text(
            dy=-5,  # shift text slightly above the bar
            color='black'
        )
        .encode(
            x=alt.X("sport_type"),
            y=alt.Y("count"),
            # text="count"
        )
    )

    # Combine bars and text
    chart = (bars + text).properties(width=600, height=400)

    return chart, sport_counts

@st.cache_data
def get_bar_plot_sport_time(athlete_stats: dict):
    all_ride = athlete_stats.get("all_ride_totals")
    all_run = athlete_stats.get("all_run_totals")

    tmp_dict = {
        "sport_type": ["Run", "Ride"],
        "moving_time": [
            all_run.get("moving_time", 0) / 3600, 
            all_ride.get("moving_time", 0) / 3600
        ]
    }

    df = pd.DataFrame(tmp_dict)

    # --- Create bar chart using Altair ---
    bars = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("sport_type", title=""),
            y=alt.Y(
                "moving_time", 
                title="",
                axis=alt.Axis(
                    grid=True,
                    gridDash=[4,4],       # make grid lines dotted
                    tickMinStep=20        # spacing of ticks every 20
                ),
            ),
            color="sport_type",
            tooltip=[
                alt.Tooltip("sport_type", title="Sport"),
                alt.Tooltip("moving_time", title="Hours", format=".2f")
            ],
        )
    )

    # Add text labels on top of the bars
    text = (
        alt.Chart(df)
        .mark_text(
            dy=-5,  # shift text slightly above the bar
            color='black'
        )
        .encode(
            x=alt.X("sport_type"),
            y=alt.Y("moving_time"),
            text=alt.Text("moving_time", format=".1f")
        )
    )

    # Combine bars and text
    chart = (bars + text).properties(width=600, height=400)

    return chart, df

@st.cache_data
def get_bar_plot_distance_covered(athlete_stats: dict):
    all_ride = athlete_stats.get("all_ride_totals")
    all_run = athlete_stats.get("all_run_totals")

    tmp_dict = {
        "sport_type": ["Run", "Ride"],
        "distance": [
            all_run.get("distance", 0) / 1000, 
            all_ride.get("distance", 0) / 1000
        ]
    }

    df = pd.DataFrame(tmp_dict)

    # --- Create bar chart using Altair ---
    bars = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("sport_type", title=""),
            y=alt.Y(
                "distance", 
                title="",
                axis=alt.Axis(
                    grid=True,
                    gridDash=[4,4],       # make grid lines dotted
                    tickMinStep=20        # spacing of ticks every 20
                ),
            ),
            color="sport_type",
            tooltip=[
                alt.Tooltip("sport_type", title="Sport"),
                alt.Tooltip("distance", title="Kilometers", format=".2f")
            ],
        )
    )

    # Add text labels on top of the bars
    text = (
        alt.Chart(df)
        .mark_text(
            dy=-5,  # shift text slightly above the bar
            color='black'
        )
        .encode(
            x=alt.X("sport_type"),
            y=alt.Y("distance"),
            text=alt.Text("distance", format=".1f")
        )
    )

    # Combine bars and text
    chart = (bars + text).properties(width=600, height=400)

    return chart, df

# @st.cache_data
def get_map_df_from_run(run_series: pd.Series):
    polyline_str = run_series["map_polyline"]
    coords = polyline.decode(polyline_str)

    path_df = pd.DataFrame({
        # note to self: 1 row with a full list, not many rows each with 1 pair
        # spent >1h figuring out this
        "path": [[ [lon, lat] for lat, lon in coords ]],
    })

    coord_df = pd.DataFrame({
        "lon": [run_series["start_lng"], run_series["end_lng"]],
        "lat": [run_series["start_lat"], run_series["end_lat"]],
        "color": [[0, 255, 0], [255, 0, 0]],   # green=start, red=end
    })

    path_layer = pdk.Layer(
        type="PathLayer",
        data=path_df,
        get_path="path",
        get_color=[255, 110, 0],  # kinda orange
        width_scale=20,
        width_min_pixels=2
    )

    points_layer = pdk.Layer(
        "ScatterplotLayer",
        data=coord_df,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius=25,
        pickable=True
    )

    view_state = pdk.ViewState(
        latitude=sum(lat for lat, lon in coords)/len(coords),
        longitude=sum(lon for lat, lon in coords)/len(coords),
        zoom=13
    )

    return pdk.Deck(layers=[path_layer, points_layer], initial_view_state=view_state)