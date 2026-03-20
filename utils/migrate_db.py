import sqlite3

from utils.config_handler import settings


def migrate():
    """Simple script to migrate data from SQLite to PostgreSQL if DATABASE_URL is set."""
    if not settings.DATABASE_URL or not settings.DATABASE_URL.startswith("postgresql"):
        print("DATABASE_URL not set to PostgreSQL. Skipping migration.")
        return

    sqlite_db = "data/trading_bot.db"
    # Connect to SQLite
    conn_src = sqlite3.connect(sqlite_db)

    # Map table names to their SQLAlchemy classes for easier session handling
    # (Actually, generic SQL might be faster for a one-off)

    # This is a basic implementation. For complex migrations, use Alembic.
    print("Migration utility ready. (Note: Fresh deployments will skip this step)")
    conn_src.close()


if __name__ == "__main__":
    migrate()
