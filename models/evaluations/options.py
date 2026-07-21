from models.db import get_db_connection

def get_distinct_semesters():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT semester FROM student_evaluations ORDER BY semester ASC")
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def get_gender_options():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT gender FROM students WHERE gender IS NOT NULL ORDER BY gender ASC")
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def get_distinct_bits_streams():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT bits_stream FROM students WHERE bits_stream IS NOT NULL ORDER BY bits_stream ASC")
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def get_distinct_branches():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT diploma_branch FROM students WHERE diploma_branch IS NOT NULL ORDER BY diploma_branch ASC")
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def get_distinct_functions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT `function` FROM students WHERE `function` IS NOT NULL ORDER BY `function` ASC")
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def get_distinct_locations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT plant_location FROM students WHERE plant_location IS NOT NULL ORDER BY plant_location ASC")
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def get_distinct_batch_nos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT batch_no FROM students WHERE batch_no IS NOT NULL ORDER BY batch_no ASC")
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

