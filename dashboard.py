import streamlit as st
from datetime import date

from analytics import (
    get_total_days,
    get_active_days,
    get_total_entries,
    get_avg_entries_per_active_day,
    get_daily_entry_counts,
)
from missed_days import get_missed_days, save_miss_reason, clear_miss_reason
from entries import get_entries_for_date, update_entry, delete_entry


def render_dashboard():
    st.title("📊 Monthly Learning Dashboard")

    # ----------------------------
    # Month selector
    # ----------------------------
    today = date.today()
    default_month = today.strftime("%Y-%m")

    month = st.text_input(
        "Month (YYYY-MM)",
        value=default_month,
        help="Enter month in YYYY-MM format"
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
    # Calendar-style overview
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
    # Missed days + reasons
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
                    key=f"reason_{day}"
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Save", key=f"save_{day}"):
                        if new_reason.strip():
                            save_miss_reason(day, new_reason.strip())
                        else:
                            clear_miss_reason(day)
                        st.experimental_rerun()

                with col2:
                    if st.button("Clear", key=f"clear_{day}"):
                        clear_miss_reason(day)
                        st.experimental_rerun()

    st.divider()

    # ----------------------------
    # Browse / Edit Entries
    # ----------------------------
    st.subheader("Browse & Edit Entries")

    selected_date = st.date_input(
        "Select date",
        value=date.today(),
        key="browse_date"
    )

    date_str = selected_date.isoformat()
    entries = get_entries_for_date(date_str)

    if not entries:
        st.info("No entries for this day.")
    else:
        for entry_id, text, created_at in entries:
            with st.expander(f"{created_at}"):
                edited_text = st.text_area(
                    "Edit entry",
                    value=text,
                    key=f"edit_{entry_id}"
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Update", key=f"update_{entry_id}"):
                        if edited_text.strip():
                            update_entry(entry_id, edited_text.strip())
                            st.success("Entry updated")
                            st.experimental_rerun()

                with col2:
                    if st.button("Delete", key=f"delete_{entry_id}"):
                        delete_entry(entry_id)
                        st.warning("Entry deleted")
                        st.experimental_rerun()