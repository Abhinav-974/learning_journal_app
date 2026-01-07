from datetime import date
from db import get_connection

def get_missed_days(month_prefix: str):
    """
    Return missed days ONLY for dates strictly before today.
    A day is missed if it has no entries and the date has already passed.
    """
    conn = get_connection()
    cur = conn.cursor()

    today = date.today().isoformat()

    cur.execute(
        """
        SELECT d.date, d.miss_reason
        FROM days d
        LEFT JOIN entries e ON d.date = e.date
        WHERE d.date LIKE ?
          AND d.date < ?
        GROUP BY d.date
        HAVING COUNT(e.id) = 0
        ORDER BY d.date ASC
        """,
        (f"{month_prefix}%", today),
    )

    rows = cur.fetchall()
    conn.close()
    return rows


def save_miss_reason(date_str: str, reason: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE days SET miss_reason = ? WHERE date = ?",
        (reason, date_str),
    )

    conn.commit()
    conn.close()


def clear_miss_reason(date_str: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE days SET miss_reason = NULL WHERE date = ?",
        (date_str,),
    )

    conn.commit()
    conn.close()