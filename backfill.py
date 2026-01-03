from datetime import date, timedelta

from db import get_connection


def backfill_days():
    """
    Ensure there is exactly one row in `days` for every calendar day
    from the last recorded date up to today.

    This guarantees:
    - No missing days
    - Missed days can be detected later (days with zero entries)
    """
    conn = get_connection()
    cur = conn.cursor()

    # Get the most recent day already stored
    cur.execute("SELECT MAX(date) FROM days")
    last_date = cur.fetchone()[0]

    today = date.today()

    # If no rows exist yet, start from yesterday
    if last_date:
        last_date = date.fromisoformat(last_date)
    else:
        last_date = today - timedelta(days=1)

    # Insert missing days up to today
    d = last_date + timedelta(days=1)
    while d <= today:
        cur.execute(
            "INSERT OR IGNORE INTO days (date) VALUES (?)",
            (d.isoformat(),)
        )
        d += timedelta(days=1)

    conn.commit()
    conn.close()