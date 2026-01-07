from datetime import date
from db import get_connection

# ----------------------------
# CREATE
# ----------------------------

def save_entry(entry_text: str, tags: str | None = None):
    conn = get_connection()
    cur = conn.cursor()

    today = date.today().isoformat()

    cur.execute(
        """
        INSERT INTO entries (date, entry_text, tags)
        VALUES (?, ?, ?)
        """,
        (today, entry_text, tags),
    )

    conn.commit()
    conn.close()


# ----------------------------
# READ
# ----------------------------

def get_today_entries():
    conn = get_connection()
    cur = conn.cursor()

    today = date.today().isoformat()

    cur.execute(
        """
        SELECT entry_text, tags
        FROM entries
        WHERE date = ?
        ORDER BY created_at ASC
        """,
        (today,),
    )

    rows = cur.fetchall()
    conn.close()
    return rows


def get_entries_for_date(date_str: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, entry_text, tags, created_at
        FROM entries
        WHERE date = ?
        ORDER BY created_at ASC
        """,
        (date_str,),
    )

    rows = cur.fetchall()
    conn.close()
    return rows


def get_all_tags():
    """Return a sorted list of distinct tags used so far."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT tags FROM entries WHERE tags IS NOT NULL")
    rows = cur.fetchall()
    conn.close()

    tag_set = set()
    for (tag_str,) in rows:
        for tag in tag_str.split(","):
            tag = tag.strip()
            if tag:
                tag_set.add(tag)

    return sorted(tag_set)


# ----------------------------
# UPDATE / DELETE
# ----------------------------

def update_entry(entry_id: int, new_text: str, new_tags: str | None = None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE entries
        SET entry_text = ?, tags = ?
        WHERE id = ?
        """,
        (new_text, new_tags, entry_id),
    )

    conn.commit()
    conn.close()


def delete_entry(entry_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()