import streamlit as st
import pandas as pd
from activity_data_helpers import (
    get_silver_data_from_pg, 
    get_bar_plot_sport_count, 
    get_bar_plot_sport_time, 
    get_bar_plot_distance_covered,
    get_map_df_from_run
)
from athlete_data_helpers import get_athlete_info_dict, get_athlete_stats_dict
from text_helpers import elapsed_since, convert_meterssecond_to_min_per_km
from datetime import timedelta
import polyline
import pydeck as pdk

df = get_silver_data_from_pg()
run_df = df[df["sport_type"] == "Run"]
athlete_info = get_athlete_info_dict()
athlete_stats = get_athlete_stats_dict()

st.title("Strava Data Dashboard")

tab1, tab2, tab3 = st.tabs(["🏃‍♂️ Athlete", "🏃 Running", "🚴 Cycling"])

with tab1:
    created_at = athlete_info.get("created_at")
    first_name = athlete_info.get("firstname")

    st.subheader(f"Hello, {first_name}")
    st.text(f"""You have been training with Strava since {created_at.strftime("%m/%d/%Y")}. That's {elapsed_since(created_at)} now!""")

    # sport type count
    st.subheader("Number of Activities on Strava")
    st.text("The number of logged activities by every type of activity you ever registered in the app")
    bar_plot_sporttype_count, sport_counts = get_bar_plot_sport_count(df)
    st.altair_chart(bar_plot_sporttype_count)

    max_row = sport_counts.loc[sport_counts['count'].idxmax()]
    highest_label = max_row['sport_type']
    highest_count = max_row['count']
    st.text(f"Your most logged activity ever is {highest_label} with {highest_count} occurrences.")

    # sport time distribution
    st.subheader("Hours Moving")
    st.text("The number of hours logged by each type of activity between Running and Cycling")
    bar_plot_sport_time, sport_times = get_bar_plot_sport_time(athlete_stats)
    st.altair_chart(bar_plot_sport_time)

    # sport km distribution
    st.subheader("Kilometers Covered")
    bar_plot_distance, sport_distances = get_bar_plot_distance_covered(athlete_stats)
    st.altair_chart(bar_plot_distance)

with tab2:
    # longest run
    longest_run = run_df.loc[run_df["distance"].idxmax()]
    
    st.subheader("Longest Run")
    st.markdown(f"""
                Title: **{longest_run["name"]}** |
                Distance: **{longest_run["distance"]/1000:.2f}km** |
                Average pace: **{convert_meterssecond_to_min_per_km(longest_run["average_speed"])}** |
                Duration: **{str(timedelta(seconds=float(longest_run["elapsed_time"])))}**
                """)

    deck = get_map_df_from_run(longest_run)
    st.pydeck_chart(deck)



with tab3:
    st.header("Cycling Stats")
