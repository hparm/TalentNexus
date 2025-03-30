import datetime
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_PATH = os.getenv('DATABASE_PATH')

def get_connection():
    return sqlite3.connect(DATABASE_PATH)

def create_role(record):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO roles (title, description, url, status) VALUES (?, ?, ?, ?)",
               (record["title"], record["description"], record["url"], record["status"]))
    conn.commit()
    conn.close()

def get_candidate(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates WHERE email = ?", (email,))
    column_names = [description[0] for description in cursor.description]
    results = list(cursor.fetchone())
    candidate = dict(zip(column_names, results))
    conn.close()
    return candidate

def get_role(title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM roles WHERE title = ?", (title,))
    column_names = [description[0] for description in cursor.description]
    results = list(cursor.fetchone())
    role = dict(zip(column_names, results))
    conn.close()
    return role

def create_candidate(record):
    conn = get_connection()
    today = datetime.date.today()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO candidates (email, first_name, last_name, resume, submission_date, status) VALUES (?, ?, ?, ?, ?, ?)",
               (record["email"], record["first_name"], record["last_name"], record["resume"], str(today), "Submitted"))
    candidate_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return cursor.lastrowid


def update_candidate_status(candidate_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE candidates SET status = ? WHERE id = ?",
        (new_status, candidate_id)
    )
    conn.commit()
    conn.close()

def create_evaluation(candidate_id, role_id, evaluation):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
            """
            INSERT INTO evaluations 
            (candidate_id, role_id, technical_skills, experience_level, 
            domain_knowledge, culture_fit, overall_match, recommendation,
            analysis_notes) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, 
            (
                candidate_id,
                role_id,
                evaluation.get('technical_skills', 0),
                evaluation.get('experience_level', 0),
                evaluation.get('domain_knowledge', 0),
                evaluation.get('culture_fit', 0),
                evaluation.get('overall_match', 0),
                evaluation.get('recommendation', 0),
                evaluation.get('analysis_notes', 0),
            )
        )
    evaluation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return evaluation_id


    