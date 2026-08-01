import sqlite3

conn = sqlite3.connect("data/database/memoryai.db")  # adjust path if needed
conn.row_factory = sqlite3.Row

print("=== USERS ===")
for row in conn.execute("SELECT * FROM users"):
    print(dict(row))

print("\n=== CHAT SESSIONS ===")
for row in conn.execute("SELECT * FROM chat_sessions"):
    print(dict(row))

print("\n=== MESSAGES ===")
for row in conn.execute("SELECT * FROM messages"):
    print(dict(row))

conn.close()