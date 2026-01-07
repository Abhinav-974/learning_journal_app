import streamlit as st
from datetime import date

from db import init_db
from backfill import backfill_days
from entries import save_entry, get_today_entries, get_all_tags
from dashboard import render_dashboard

st.set_page_config(page_title="Daily Learning Tracker", layout="wide")

init_db()
backfill_days()

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Daily Entry", "Monthly Dashboard"])

# ----------------------------
# DAILY ENTRY
# ----------------------------
if page == "Daily Entry":
    st.title("📘 What did you learn today?")

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

    entry_text = st.text_area("Add a new learning", height=100)

    # Tag selector
    existing_tags = get_all_tags()
    selected_tags = st.multiselect(
        "Select existing tags",
        options=existing_tags,
    )

    new_tags_text = st.text_input(
        "Add new tags (comma-separated)",
        placeholder="e.g. system-design, sql",
    )

    if st.button("Save entry"):
        if entry_text.strip():
            all_tags = set(selected_tags)
            if new_tags_text.strip():
                for t in new_tags_text.split(","):
                    if t.strip():
                        all_tags.add(t.strip())

            tags_str = ", ".join(sorted(all_tags)) if all_tags else None
            save_entry(entry_text.strip(), tags_str)
            st.success("Saved! Add another one 👇")
            st.rerun()
        else:
            st.warning("Entry cannot be empty")

else:
    render_dashboard()