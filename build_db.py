"""
Stores the courses from data/courses.json in data/courses.db, which the
search reads. Re-run after fetch_courses.py when courses change.
"""

import json
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def build_db():
    with open(os.path.join(BASE_DIR, "data", "courses.json"), "r", encoding="utf-8") as f:
        courses = json.load(f)

    conn = sqlite3.connect(os.path.join(BASE_DIR, "data", "courses.db"))
    # Rebuilt from scratch so removed courses disappear too.
    conn.execute("DROP TABLE IF EXISTS courses")
    conn.execute("""
        CREATE TABLE courses (
            id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            url TEXT
        )
    """)
    conn.executemany(
        "INSERT INTO courses (id, title, description, url) VALUES (?, ?, ?, ?)",
        [(c["id"], c["title"], c["description"], c["url"]) for c in courses],
    )
    conn.commit()
    conn.execute("VACUUM")
    conn.close()
    print(f"Stored {len(courses)} courses.")


if __name__ == "__main__":
    build_db()
