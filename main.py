from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

# This creates the FastAPI app
app = FastAPI(title="Students Database CRUD Application")

# 1. Database Setup (Creates the database file and table automatically)
def init_db():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            contact TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# 2. Define how the input data should look
class StudentInput(BaseModel):
    name: str
    dob: str
    contact: str

# Helper function to connect to database
def get_db_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row  # Makes data return as a dictionary
    return conn

# 3. CREATE a new student
@app.post("/students")
def create_student(student: StudentInput):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (name, dob, contact) VALUES (?, ?, ?)",
        (student.name, student.dob, student.contact)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"message": "Student created successfully!", "student_id": new_id}

# 4. READ (List all students)
@app.get("/students")
def get_all_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return students

# 5. READ (View a specific student by ID)
@app.get("/students/{student_id}")
def get_student(student_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()
    conn.close()
    
    # Missing-record handling (Required in your PDF checklist)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# 6. UPDATE a student's details
@app.put("/students/{student_id}")
def update_student(student_id: int, student: StudentInput):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if student exists first
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Student not found")

    cursor.execute(
        "UPDATE students SET name = ?, dob = ?, contact = ? WHERE student_id = ?",
        (student.name, student.dob, student.contact, student_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Student updated successfully!"}

# 7. DELETE a student
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if student exists first
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Student not found")

    cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()
    return {"message": "Student deleted successfully!"}