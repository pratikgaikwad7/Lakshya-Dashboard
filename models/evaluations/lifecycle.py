from models.db import get_db_connection

def promote_student_semester(student_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        conn.start_transaction()
        
        cursor.execute("SELECT status FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        if not student or student['status'] != 'active':
            conn.rollback()
            conn.close()
            return False, "Cannot promote non-active student."

        cursor.execute("SELECT id, semester FROM student_evaluations WHERE student_id = %s AND semester_status = 'ongoing' ORDER BY semester DESC LIMIT 1 FOR UPDATE", (student_id,))
        current = cursor.fetchone()
        
        if not current:
            conn.rollback()
            conn.close()
            return False, "No active semester found."
        
        current_sem = current['semester']
        
        if current_sem >= 7:
            conn.rollback()
            conn.close()
            return False, "Maximum semester limit (7) reached. Use 'End 7th Semester'."

        next_sem = current_sem + 1
        
        cursor.execute("UPDATE student_evaluations SET semester_status = 'completed' WHERE id = %s AND semester_status = 'ongoing'", (current['id'],))
        if cursor.rowcount != 1:
            conn.rollback()
            conn.close()
            return False, "Semester was already completed by another request."
        cursor.execute("INSERT INTO student_evaluations (student_id, semester, semester_status) VALUES (%s, %s, 'ongoing')", (student_id, next_sem))
        
        conn.commit()
        conn.close()
        return True, f"Promoted to Semester {next_sem}"
    except Exception:
        conn.rollback()
        conn.close()
        raise

def end_seventh_semester(student_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        conn.start_transaction()
        
        cursor.execute("SELECT status FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        if not student or student['status'] != 'active':
            conn.rollback()
            conn.close()
            return False, "Student is not active."

        cursor.execute("SELECT id, semester FROM student_evaluations WHERE student_id = %s AND semester_status = 'ongoing' ORDER BY semester DESC LIMIT 1 FOR UPDATE", (student_id,))
        current = cursor.fetchone()
        
        if not current:
            conn.rollback()
            conn.close()
            return False, "No active semester found."
            
        if current['semester'] != 7:
            conn.rollback()
            conn.close()
            return False, "Can only end Semester 7."

        cursor.execute("UPDATE student_evaluations SET semester_status = 'completed' WHERE id = %s AND semester_status = 'ongoing'", (current['id'],))
        if cursor.rowcount != 1:
            conn.rollback()
            conn.close()
            return False, "Semester was already completed by another request."
        
        conn.commit()
        conn.close()
        return True, "Semester 7 Ended Successfully!"
    except Exception:
        conn.rollback()
        conn.close()
        raise

def upsert_evaluation_scores(student_id, semester, data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        UPDATE student_evaluations SET
        score_attendance = %s, score_suggestions = %s, score_projects = %s, score_recognitions = %s,
        score_safety = %s, score_discipline = %s, score_bits_attendance = %s, score_equipment = %s,
        score_shop_task = %s, score_function_output = %s, training_marks = %s, bits_cgpa = %s
        WHERE student_id = %s AND semester = %s
    """
    values = (
        data.get('score_attendance', 0), data.get('score_suggestions', 0), 
        data.get('score_projects', 0), data.get('score_recognitions', 0), 
        data.get('score_safety', 0), data.get('score_discipline', 0), 
        data.get('score_bits_attendance', 0), data.get('score_equipment', 0), 
        data.get('score_shop_task', 0), data.get('score_function_output', 0),
        data.get('training_marks', 0), data.get('bits_cgpa', 0),
        student_id, semester
    )
    try:
        conn.start_transaction()
        cursor.execute("SELECT status FROM students WHERE id = %s FOR UPDATE", (student_id,))
        student = cursor.fetchone()
        if not student or student['status'] != 'active':
            conn.rollback()
            return False, "Evaluation locked: Student is not active."
        if semester < 1 or semester > 7:
            conn.rollback()
            return False, "Invalid semester."

        query = query.replace(
            "WHERE student_id = %s AND semester = %s",
            "WHERE student_id = %s AND semester = %s AND semester_status = 'ongoing'",
        )
        cursor.execute(query, values)
        if cursor.rowcount != 1:
            conn.rollback()
            return False, "Evaluation locked: Semester is not ongoing."
        conn.commit()
        return True, "Scores updated successfully."
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def bulk_upsert_evaluations(records):
    if not records:
        return 0

    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        INSERT INTO student_evaluations 
        (student_id, semester, semester_status, score_attendance, score_suggestions, 
         score_projects, score_recognitions, score_safety, score_discipline, 
         score_bits_attendance, score_equipment, score_shop_task, score_function_output, 
         training_marks, bits_cgpa)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        semester_status = VALUES(semester_status),
        score_attendance = VALUES(score_attendance),
        score_suggestions = VALUES(score_suggestions),
        score_projects = VALUES(score_projects),
        score_recognitions = VALUES(score_recognitions),
        score_safety = VALUES(score_safety),
        score_discipline = VALUES(score_discipline),
        score_bits_attendance = VALUES(score_bits_attendance),
        score_equipment = VALUES(score_equipment),
        score_shop_task = VALUES(score_shop_task),
        score_function_output = VALUES(score_function_output),
        training_marks = VALUES(training_marks),
        bits_cgpa = VALUES(bits_cgpa)
    """
    
    values = []
    for rec in records:
        values.append(
            (
                rec.get('student_id'),
                rec.get('semester'),
                rec.get('semester_status', 'ongoing'),
                rec.get('score_attendance', 0),
                rec.get('score_suggestions', 0),
                rec.get('score_projects', 0),
                rec.get('score_recognitions', 0),
                rec.get('score_safety', 0),
                rec.get('score_discipline', 0),
                rec.get('score_bits_attendance', 0),
                rec.get('score_equipment', 0),
                rec.get('score_shop_task', 0),
                rec.get('score_function_output', 0),
                rec.get('training_marks', 0),
                rec.get('bits_cgpa', 0)
            )
        )
    
    try:
        cursor.executemany(query, values)
        success_count = cursor.rowcount
        
        # ---------------------------------------------------------
        # NEW: AUTO SEMESTER PROGRESSION LOGIC
        # ---------------------------------------------------------
        for rec in records:
            student_id = rec.get('student_id')
            semester = int(rec.get('semester') or 1)
            semester_status = str(rec.get('semester_status', 'ongoing')).lower().strip()

            # If uploaded semester is completed and < 7, create next semester
            if semester_status == 'completed' and semester < 7:
                next_sem = semester + 1
                
                # Check if next semester already exists
                cursor.execute("""
                    SELECT id FROM student_evaluations
                    WHERE student_id = %s AND semester = %s
                """, (student_id, next_sem))
                
                if not cursor.fetchone():
                    # Create next semester as ongoing
                    cursor.execute("""
                        INSERT INTO student_evaluations
                        (student_id, semester, semester_status)
                        VALUES (%s, %s, 'ongoing')
                    """, (student_id, next_sem))
        
        conn.commit()
        conn.close()
        return success_count
    except Exception:
        conn.rollback()
        conn.close()
        raise
