import sqlite3
from datetime import datetime

def get_db():
    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            date TEXT,
            timestamp TEXT,
            status TEXT,
            FOREIGN KEY(student_id) REFERENCES students(student_id),
            UNIQUE(student_id, date)
        );
    """)

    conn.commit()
    conn.close()


def add_student(student_id, name):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO students (student_id, name) VALUES (?, ?)", (student_id, name))
        conn.commit()
        return True, "Student added successfully"
    except sqlite3.IntegrityError:
        return False, "Student ID already exists"
    finally:
        conn.close()


def remove_student(student_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    cur.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()


def mark_attendance(student_id, status):
    conn = get_db()
    cur = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cur.execute(
            "INSERT INTO attendance (student_id, date, timestamp, status) VALUES (?, ?, ?, ?)",
            (student_id, today, timestamp, status)
        )
        conn.commit()
        return True, f"Attendance marked as {status}"
    except sqlite3.IntegrityError:
        cur.execute(
            "UPDATE attendance SET status = ?, timestamp = ? WHERE student_id = ? AND date = ?",
            (status, timestamp, student_id, today)
        )
        conn.commit()
        return True, f"Attendance updated to {status}"
    finally:
        conn.close()


def get_students():
    conn = get_db()
    cur = conn.cursor()
    result = cur.execute("SELECT * FROM students ORDER BY name").fetchall()
    conn.close()
    return result


def get_attendance(date=None):
    conn = get_db()
    cur = conn.cursor()
    
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    result = cur.execute("""
        SELECT s.student_id, s.name, a.status, a.timestamp
        FROM students s
        LEFT JOIN attendance a ON s.student_id = a.student_id AND a.date = ?
        ORDER BY s.name
    """, (date,)).fetchall()
    
    conn.close()
    return result


def get_student_by_id(student_id):
    conn = get_db()
    cur = conn.cursor()
    result = cur.execute("SELECT * FROM students WHERE student_id = ?", (student_id,)).fetchone()
    conn.close()
    return result


def get_attendance_stats():
    conn = get_db()
    cur = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    total_students = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    
    present_today = cur.execute(
        "SELECT COUNT(*) FROM attendance WHERE date = ? AND status = 'Present'",
        (today,)
    ).fetchone()[0]
    
    absent_today = total_students - present_today
    
    conn.close()
    
    return {
        'total': total_students,
        'present': present_today,
        'absent': absent_today,
        'date': today
    }
