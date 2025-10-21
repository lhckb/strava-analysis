import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta

@st.cache_data
def elapsed_since(date: datetime) -> str | None:
    # past_date = datetime.strptime(date_str, fmt).date()
    date = date.replace(tzinfo=None)
    today = datetime.today().date()

    diff = relativedelta(today, date)

    parts = []
    if diff.years:
        parts.append(f"{diff.years} year{'s' if diff.years != 1 else ''}")
    if diff.months:
        parts.append(f"{diff.months} month{'s' if diff.months != 1 else ''}")
    if diff.days:
        parts.append(f"{diff.days} day{'s' if diff.days != 1 else ''}")

    if not parts:
        return None

    return ', '.join(parts)

@st.cache_data
def convert_meterssecond_to_min_per_km(meters_per_second):
    if meters_per_second <= 0:
        return "—"
    total_minutes = 1000 / (meters_per_second * 60)
    minutes = int(total_minutes)
    seconds = int((total_minutes - minutes) * 60)
    return f"{minutes}:{seconds:02d}/km"