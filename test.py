from database.sqlite_manager import SQLiteManager

db = SQLiteManager()

with db.get_connection() as conn:
    rows = conn.execute(
        "SELECT id, username FROM users"
    ).fetchall()

for row in rows:
    print(row)