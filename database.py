import sqlite3

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    attendance INTEGER NOT NULL,
    internal_marks INTEGER NOT NULL,
    assignment_completion INTEGER NOT NULL
)
""")

conn.commit()
conn.close()

print("Database ready successfully!")
