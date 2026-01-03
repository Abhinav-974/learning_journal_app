from db import get_connection


def get_missed_days(month_prefix: str):
    """
    Return all missed days for a given month.
    A missed day = exists in `days` but has zero entries.

    month_prefix format: YYYY-MM
    Returns: list of (date, miss_reason)
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT d.date, d.miss_reason
        FROM days d
        LEFT JOIN entries e ON d.date = e.date
        WHERE e.id IS NULL
          AND d.date LIKE ?
        ORDER BY d.date ASC
        """,
        (f"{month_prefix}%",)
    )

    rows = cur.fetchall()
    conn.close()

    return rows


def save_miss_reason(date_str: str, reason: str):
    """Save or update a reason for missing a specific day."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE days
        SET miss_reason = ?
        WHERE date = ?
        """,
        (reason, date_str)
    )

    conn.commit()
    conn.close()


def clear_miss_reason(date_str: str):
    """Clear an existing miss reason for a day."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE days
        SET miss_reason = NULL
        WHERE date = ?
        """,
        (date_str,)
    )

    conn.commit()
    conn.close()