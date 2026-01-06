import shutil
from datetime import datetime
from pathlib import Path


def backup_db():
    """
    Create a timestamped backup of learning.db inside ./backups directory.
    Backup is manual (triggered by user action).
    """
    src = Path("learning.db")

    if not src.exists():
        return False, "Database file not found."

    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dest = backup_dir / f"learning_{timestamp}.db"

    shutil.copy2(src, dest)

    return True, f"Backup created: {dest.name}"
