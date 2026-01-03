from db import get_connection


def get_total_days(month_prefix: str) -> int:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM days WHERE date LIKE ?",
        (f"{month_prefix}%",)
    )
    total = cur.fetchone()[0]

    conn.close()
    return total


def get_active_days(month_prefix: str) -> int:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT COUNT(DISTINCT d.date)
        FROM days d
        JOIN entries e ON d.date = e.date
        WHERE d.date LIKE ?
        """,
        (f"{month_prefix}%",)
    )

    active = cur.fetchone()[0]
    conn.close()

    return active


def get_total_entries(month_prefix: str) -> int:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM entries WHERE date LIKE ?",
        (f"{month_prefix}%",)
    )

    total = cur.fetchone()[0]
    conn.close()

    return total


def get_avg_entries_per_active_day(month_prefix: str) -> float:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            CASE
                WHEN COUNT(DISTINCT date) = 0 THEN 0
                ELSE COUNT(*) * 1.0 / COUNT(DISTINCT date)
            END
        FROM entries
        WHERE date LIKE ?
        """,
        (f"{month_prefix}%",)
    )

    avg = cur.fetchone()[0]
    conn.close()

    return round(avg, 2)


def get_daily_entry_counts(month_prefix: str):
    """
    Returns a dict: {date: entry_count}
    Used for calendar-style views.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT date, COUNT(*)
        FROM entries
        WHERE date LIKE ?
        GROUP BY date
        """,
        (f"{month_prefix}%",)
    )

    rows = cur.fetchall()
    conn.close()

    return {date: count for date, count in rows}