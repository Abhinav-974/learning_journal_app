import streamlit as st
from datetime import date, timedelta

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

    # Align grid to Monday
    current = start - timedelta(days=start.weekday())

    weeks = []
    week = []

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
    st.title("📊 Monthly Learning Dashboard")

    # ----------------------------
    # Manual backup
    # ----------------------------
    with st.expander("💾 Backup Database", expanded=False):
        st.caption("Create a manual backup of your learning.db file")
        if st.button("Backup now"):
            success, msg = backup_db()
            if success:
                st.success(msg)
            else:
                st.error(msg)

    st.divider()

    # ----------------------------
    # Heatmap
    # ----------------------------
    current_year = date.today().year
    year = st.selectbox("Year", list(range(current_year - 3, current_year + 1)))
    render_heatmap(year)

    st.divider()

    # ----------------------------
    # Month selector
    # ----------------------------
    today = date.today()
    default_month = today.strftime("%Y-%m")

    month = st.text_input(
        "Month (YYYY-MM)",
        value=default_month,
        help="Enter month in YYYY-MM format",
    )

    st.divider()

    # ----------------------------
    # KPI Metrics
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
    # Daily overview
    # ----------------------------
    st.subheader("Daily Activity Overview")
    daily_counts = get_daily_entry_counts(month)

    if not daily_counts:
        st.caption("No entries this month yet")
    else:
        for day, count in sorted(daily_counts.items()):
            st.write(f"{day} → {count} entr{'y' if count == 1 else 'ies'}")

    st.divider()

    # ----------------------------
    # Missed days & reasons
    # ----------------------------
    st.subheader("Missed Days & Reasons")
    missed_days = get_missed_days(month)

    if not missed_days:
        st.success("🎉 No missed days this month!")
    else:
        for day, reason in missed_days:
            with st.expander(day):
                new_reason = st.text_input(
                    "Reason",
                    value=reason or "",
                    key=f"reason_{day}",
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Save", key=f"save_{day}"):
                        if new_reason.strip():
                            save_miss_reason(day, new_reason.strip())
                        else:
                            clear_miss_reason(day)
                        st.rerun()
                with col2:
                    if st.button("Clear", key=f"clear_{day}"):
                        clear_miss_reason(day)
                        st.rerun()

    st.divider()

    # ----------------------------
    # Browse / Edit Entries (with tags)
    # ----------------------------
    st.subheader("Browse & Edit Entries")

    selected_date = st.date_input(
        "Select date",
        value=date.today(),
        key="browse_date",
    )

    date_str = selected_date.isoformat()
    entries = get_entries_for_date(date_str)

    if not entries:
        st.info("No entries for this day.")
    else:
        for entry_id, text, tags, created_at in entries:
            with st.expander(f"{created_at}"):
                edited_text = st.text_area(
                    "Edit entry",
                    value=text,
                    key=f"edit_text_{entry_id}",
                )

                edited_tags = st.text_input(
                    "Tags (comma-separated)",
                    value=tags or "",
                    key=f"edit_tags_{entry_id}",
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Update", key=f"update_{entry_id}"):
                        if edited_text.strip():
                            final_tags = edited_tags.strip() or None
                            update_entry(entry_id, edited_text.strip(), final_tags)
                            st.success("Entry updated")
                            st.rerun()
                with col2:
                    if st.button("Delete", key=f"delete_{entry_id}"):
                        delete_entry(entry_id)
                        st.warning("Entry deleted")
                        st.rerun()