import streamlit as st
from datetime import date, timedelta
from zoneinfo import ZoneInfo

from analytics import (
    get_total_days,
    get_active_days,
    get_total_entries,
    get_avg_entries_per_active_day,
    get_daily_entry_counts,
    get_entry_counts_between,
)
from missed_days import get_missed_days, save_miss_reason, clear_miss_reason
from entries import get_entries_for_date, update_entry, delete_entry
from backup import backup_db

# ----------------------------
# Timezone configuration (UI configurable)
# ----------------------------
from zoneinfo import available_timezones

# Sensible common defaults
COMMON_TIMEZONES = [
    "Asia/Kolkata",
    "UTC",
    "America/New_York",
    "America/Los_Angeles",
    "Europe/London",
    "Europe/Berlin",
    "Asia/Singapore",
]

# Persist user choice in session
if "timezone" not in st.session_state:
    st.session_state["timezone"] = "Asia/Kolkata"

SELECTED_TZ = ZoneInfo(st.session_state["timezone"])


# ----------------------------
# Heatmap helpers
# ----------------------------

def heat_color(count: int) -> str:
    if count == 0:
        return "#ebedf0"
    if count <= 2:
        return "#9be9a8"
    if count <= 4:
        return "#40c463"
    return "#216e39"


def render_heatmap(year: int):
    st.subheader("Learning Activity Heatmap")

    start = date(year, 1, 1)
    end = date(year, 12, 31)

    counts = get_entry_counts_between(start, end)

    current = start - timedelta(days=start.weekday())
    weeks, week = [], []

    while current <= end:
        count = counts.get(current.isoformat(), 0)
        week.append((current, count))
        if len(week) == 7:
            weeks.append(week)
            week = []
        current += timedelta(days=1)

    cols = st.columns(len(weeks))

    for col, week in zip(cols, weeks):
        with col:
            for day, count in week:
                color = heat_color(count)
                st.markdown(
                    f"""
                    <div title="{day}: {count} entries"
                         style="width:14px;height:14px;margin:2px;
                         background-color:{color};border-radius:3px"></div>
                    """,
                    unsafe_allow_html=True,
                )


# ----------------------------
# Dashboard
# ----------------------------

def render_dashboard():
    # ----------------------------
    # Timezone selector (UI)
    # ----------------------------
    with st.sidebar.expander("⏰ Timezone", expanded=False):
        tz_choice = st.selectbox(
            "Display timestamps in",
            COMMON_TIMEZONES,
            index=COMMON_TIMEZONES.index(st.session_state["timezone"])
            if st.session_state["timezone"] in COMMON_TIMEZONES
            else 0,
        )
        st.session_state["timezone"] = tz_choice
    st.title("📊 Monthly Learning Dashboard")

    # ----------------------------
    # Backup
    # ----------------------------
    with st.expander("💾 Backup Database", expanded=False):
        if st.button("Backup now"):
            success, msg = backup_db()
            st.success(msg) if success else st.error(msg)

    st.divider()

    # ----------------------------
    # Heatmap (default = current year)
    # ----------------------------
    current_year = date.today().year
    year = st.selectbox(
        "Year",
        list(range(current_year - 3, current_year + 1)),
        index=3,
    )
    render_heatmap(year)

    st.divider()

    # ----------------------------
    # Month selector
    # ----------------------------
    default_month = date.today().strftime("%Y-%m")
    month = st.text_input("Month (YYYY-MM)", value=default_month)

    st.divider()

    # ----------------------------
    # KPIs
    # ----------------------------
    total_days = get_total_days(month)
    active_days = get_active_days(month)
    missed_days_count = total_days - active_days
    total_entries = get_total_entries(month)
    avg_entries = get_avg_entries_per_active_day(month)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Days Logged", f"{active_days} / {total_days}")
    c2.metric("Missed Days", missed_days_count)
    c3.metric("Total Entries", total_entries)
    c4.metric("Avg / Active Day", avg_entries)

    st.divider()

    # ----------------------------
    # Missed days (only past dates)
    # ----------------------------
    st.subheader("Missed Days & Reasons")
    missed_days = get_missed_days(month)

    if not missed_days:
        st.success("🎉 No missed days so far!")
    else:
        for day, reason in missed_days:
            with st.expander(day):
                new_reason = st.text_input("Reason", value=reason or "", key=f"r_{day}")
                if st.button("Save", key=f"s_{day}"):
                    save_miss_reason(day, new_reason.strip()) if new_reason.strip() else clear_miss_reason(day)
                    st.experimental_rerun()

    st.divider()

    # ----------------------------
    # Browse / Edit Entries (localized timestamps)
    # ----------------------------
    st.subheader("Browse & Edit Entries")

    selected_date = st.date_input("Select date", value=date.today())
    date_str = selected_date.isoformat()

    entries = get_entries_for_date(date_str)

    if not entries:
        st.info("No entries for this day.")
    else:
        for entry_id, text, tags, created_at in entries:
            local_ts = (
                date.fromisoformat(created_at[:10])
                if created_at
                else None
            )

            with st.expander(f"{created_at} ({st.session_state['timezone']})"):
                edited_text = st.text_area("Edit entry", value=text, key=f"t_{entry_id}")
                edited_tags = st.text_input("Tags", value=tags or "", key=f"g_{entry_id}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Update", key=f"u_{entry_id}"):
                        update_entry(entry_id, edited_text.strip(), edited_tags.strip() or None)
                        st.experimental_rerun()
                with col2:
                    if st.button("Delete", key=f"d_{entry_id}"):
                        delete_entry(entry_id)
                        st.experimental_rerun()