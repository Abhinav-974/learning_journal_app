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
        for text, tags in entries:
            if tags:
                st.markdown(f"- **{text}**  \\n🧩 *Tags:* `{tags}`")
            else:
                st.markdown(f"- **{text}**")
    else:
        st.caption("No entries yet today")

    st.divider()

    # Input box for new entry
    entry_text = st.text_area("Add a new learning", height=100)
    tags_text = st.text_input(
        "Tags (optional, comma-separated)",
        placeholder="e.g. python, sql, backend"
    )

    if st.button("Save entry"):
        if entry_text.strip():
            tags = tags_text.strip() if tags_text.strip() else None
            save_entry(entry_text.strip(), tags)
            st.success("Saved! Add another one 👇")
            st.rerun()
        else:
            st.warning("Entry cannot be empty")

# ----------------------------
# DASHBOARD PAGE
# ----------------------------
else:
    render_dashboard()