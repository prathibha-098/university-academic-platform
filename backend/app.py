from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "database": os.getenv("DB_NAME", "universitydb"),
    "user": os.getenv("DB_USER", "university"),
    "password": os.getenv("DB_PASSWORD", "password"),
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            department VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            attendance NUMERIC(5,2) NOT NULL,
            marks NUMERIC(5,2) NOT NULL
        )
    """)
    cur.execute("SELECT COUNT(*) FROM students")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
            INSERT INTO students (name, department, email, attendance, marks)
            VALUES (%s, %s, %s, %s, %s)
        """, [
            ("Arun Kumar", "AI & DS", "arun@university.edu", 85, 78),
            ("Priya Sharma", "Computer Science", "priya@university.edu", 68, 55),
            ("Rahul Raj", "Information Technology", "rahul@university.edu", 92, 88),
        ])
    conn.commit()
    cur.close()
    conn.close()

@app.route("/api/health")
def health():
    return jsonify({"status": "healthy", "service": "university-backend"})

@app.route("/api/students", methods=["GET"])
def students():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM students ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)

@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json()
    required = ["name", "department", "email", "attendance", "marks"]
    if not all(k in data for k in required):
        return jsonify({"error": "All fields are required"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            INSERT INTO students (name, department, email, attendance, marks)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """, (
            data["name"], data["department"], data["email"],
            data["attendance"], data["marks"]
        ))
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(row), 201
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id = %s", (student_id,))
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if deleted == 0:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"message": "Student deleted"})

@app.route("/api/risk", methods=["GET"])
def risk_students():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT * FROM students
        WHERE attendance < 75 OR marks < 60
        ORDER BY attendance ASC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)

@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
          COUNT(*) AS total,
          COUNT(*) FILTER (WHERE attendance < 75 OR marks < 60) AS at_risk,
          ROUND(AVG(attendance), 2) AS avg_attendance,
          ROUND(AVG(marks), 2) AS avg_marks
        FROM students
    """)
    row = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify({
        "total_students": row[0],
        "at_risk_students": row[1],
        "average_attendance": float(row[2] or 0),
        "average_marks": float(row[3] or 0)
    })

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
