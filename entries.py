from datetime import date

from db import get_connection

# ----------------------------
# CREATE
# ----------------------------

def save_entry(entry_text: str):
    """Save a new learning entry for today."""
    conn = get_connection()
    cur = conn.cursor()

    today = date.today().isoformat()

    cur.execute(
        """
        INSERT INTO entries (date, entry_text)
        VALUES (?, ?)
        """,
        (today, entry_text)
    )

    conn.commit()
    conn.close()


# ----------------------------
# READ
# ----------------------------

def get_today_entries():
    """Return all entries logged today (ordered by time)."""
    conn = get_connection()
    cur = conn.cursor()

    today = date.today().isoformat()

    cur.execute(
        """
        SELECT entry_text
        FROM entries
        WHERE date = ?
        ORDER BY created_at ASC
        """,
        (today,)
    )

    rows = cur.fetchall()
    conn.close()

    return [r[0] for r in rows]


def get_entries_for_date(date_str: str):
    """Return all entries for a specific date."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, entry_text, created_at
        FROM entries
        WHERE date = ?
        ORDER BY created_at ASC
        """,
        (date_str,)
    )

    rows = cur.fetchall()
    conn.close()

    return rows


def get_entries_for_month(month_prefix: str):
    """
    Fetch all entries for a given month.
    month_prefix format: YYYY-MM
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT date, entry_text, created_at
        FROM entries
        WHERE date LIKE ?
        ORDER BY date ASC, created_at ASC
        """,
        (f"{month_prefix}%",)
    )

    rows = cur.fetchall()
    conn.close()

    return rows


# ----------------------------
# UPDATE / DELETE
# ----------------------------

def update_entry(entry_id: int, new_text: str):
    """Update an existing entry by id."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE entries
        SET entry_text = ?
        WHERE id = ?
        """,
        (new_text, entry_id)
    )

    conn.commit()
    conn.close()


def delete_entry(entry_id: int):
    """Delete an entry by id."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM entries WHERE id = ?",
        (entry_id,)
    )

    conn.commit()
    conn.close()