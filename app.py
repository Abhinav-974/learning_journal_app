import streamlit as st
from datetime import date

from db import init_db
from backfill import backfill_days
from entries import save_entry, get_today_entries
from dashboard import render_dashboard

# ----------------------------
# App Initialization
# ----------------------------
st.set_page_config(page_title="Daily Learning Tracker", layout="wide")

init_db()
backfill_days()

# ----------------------------
# Sidebar Navigation
# ----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Daily Entry", "Monthly Dashboard"])

# ----------------------------
# DAILY ENTRY PAGE (DEFAULT)
# ----------------------------
if page == "Daily Entry":
    st.title("📘 What did you learn today?")

    today = date.today().isoformat()

    # Show existing entries
    st.subheader("Today's entries")
    entries = get_today_entries()
    if entries:
        for e in entries:
            st.markdown(f"- {e}")
    else:
        st.caption("No entries yet today")

    st.divider()

    # Input box
    entry_text = st.text_area("Add a new learning", height=100)

    if st.button("Save entry"):
        if entry_text.strip():
            save_entry(entry_text.strip())
            st.success("Saved! Add another one 👇")
            st.rerun()
        else:
            st.warning("Entry cannot be empty")

# ----------------------------
# DASHBOARD PAGE
# ----------------------------
else:
    render_dashboard()