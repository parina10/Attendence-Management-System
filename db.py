"""
Database module for handling SQLite operations
"""
import sqlite3
from datetime import datetime
from contextlib import contextmanager

DATABASE_NAME = "attendance.db"

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize database tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT,
    password_hash TEXT,
    role TEXT DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
        """)

        # Create attendance table
        cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    status TEXT DEFAULT 'Present',
    marked_by TEXT DEFAULT 'self',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, date)
)
""")

        conn.commit()

def create_user(username, email, password_hash):
    """Create a new user"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            conn.commit()
            return True, "User created successfully"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already exists"
        elif "email" in str(e):
            return False, "Email already exists"
        return False, "Error creating user"

def get_user_by_username(username):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        return dict(user) if user else None

def get_user_by_id(user_id):
    """Get user by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        return dict(user) if user else None

def mark_attendance(user_id, marked_by="self"):
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO attendance (user_id, date, time, status, marked_by) VALUES (?, ?, ?, ?, ?)",
                (user_id, current_date, current_time, "Present", marked_by)
            )
            conn.commit()
            return True, "Attendance marked successfully"
    except sqlite3.IntegrityError:
        return False, "Attendance already marked for today"

def get_user_attendance(user_id, start_date=None, end_date=None):
    """Get attendance records for a user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        query = "SELECT * FROM attendance WHERE user_id = ?"
        params = [user_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date DESC, time DESC"

        cursor.execute(query, params)
        records = cursor.fetchall()
        return [dict(record) for record in records]

def get_attendance_stats(user_id):
    """Get attendance statistics for a user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Total days recorded
        cursor.execute(
            "SELECT COUNT(*) as total FROM attendance WHERE user_id = ?",
            (user_id,)
        )
        total_days = cursor.fetchone()['total']

        # Present days
        cursor.execute(
            "SELECT COUNT(*) as present FROM attendance WHERE user_id = ? AND status = 'Present'",
            (user_id,)
        )
        present_days = cursor.fetchone()['present']

        # Calculate percentage
        percentage = (present_days / total_days * 100) if total_days > 0 else 0

        return {
            'total_days': total_days,
            'present_days': present_days,
            'percentage': round(percentage, 2)
        }

def update_user_password(user_id, new_password_hash):
    """Update user password"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (new_password_hash, user_id)
        )
        conn.commit()
        return True

def get_all_users():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, created_at FROM users")
        return [dict(row) for row in cursor.fetchall()]

def get_all_attendance():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, u.username, u.email
            FROM attendance a
            JOIN users u ON a.user_id = u.id
            ORDER BY a.date DESC, a.time DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
