from models.db import get_db_connection
from models.evaluations.filters import _build_filter_conditions

def get_filtered_students_for_eval(filters):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    active_sem_subquery = """
        (SELECT semester FROM student_evaluations se2 
         WHERE se2.student_id = s.id 
         AND se2.semester_status = 'ongoing' 
         ORDER BY se2.semester DESC 
         LIMIT 1)
    """

    query = f"""
        SELECT 
            s.id,
            s.email,
            s.employee_name,
            s.ticket_no,
            s.diploma_branch,
            s.gender,
            s.mobile_no,
            s.department,
            s.bc_no,
            s.reporting_manager,
            s.`function`,
            s.date_of_joining,
            s.plant_location,
            s.batch_year,
            s.batch_no,
            s.status AS student_status,
            s.bits_stream,
            s.end_date,

            e.semester,
            e.semester_status,
            e.score_attendance,
            e.score_suggestions,
            e.score_projects,
            e.score_recognitions,
            e.score_safety,
            e.score_discipline,
            e.score_bits_attendance,
            e.score_equipment,
            e.score_shop_task,
            e.score_function_output,
            e.training_marks,
            e.bits_cgpa,
            e.calc_training_total,
            e.calc_ojt_total,
            e.calc_bits_total,
            e.calc_grand_total,

            {active_sem_subquery} AS active_semester

        FROM students s
        LEFT JOIN student_evaluations e 
            ON s.id = e.student_id
    """

    conditions, params = _build_filter_conditions(filters)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY s.employee_name ASC, e.semester ASC"

    cursor.execute(query, tuple(params))
    results = cursor.fetchall()

    conn.close()
    return results

def get_student_active_evaluation(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT * FROM student_evaluations 
        WHERE student_id = %s AND semester_status = 'ongoing'
        ORDER BY semester DESC LIMIT 1
    """
    cursor.execute(query, (student_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_student_last_evaluation(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT e.*, s.plant_location 
        FROM student_evaluations e
        JOIN students s ON e.student_id = s.id
        WHERE e.student_id = %s 
        ORDER BY e.semester DESC 
        LIMIT 1
    """
    
    cursor.execute(query, (student_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_student_evaluation_by_sem(student_id, semester):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT s.*, 
               e.id AS evaluation_id, e.semester, e.semester_status,
               e.score_attendance, e.score_suggestions, e.score_projects, e.score_recognitions, 
               e.score_safety, e.score_discipline, e.score_bits_attendance, e.score_equipment, 
               e.score_shop_task, e.score_function_output, 
               e.training_marks, e.bits_cgpa,
               e.calc_training_total, e.calc_ojt_total, e.calc_bits_total, e.calc_grand_total
        FROM students s
        JOIN student_evaluations e ON s.id = e.student_id
        WHERE s.id = %s AND e.semester = %s
    """
    cursor.execute(query, (student_id, semester))
    result = cursor.fetchone()
    conn.close()
    return result

def get_student_all_evaluations_list(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT semester, semester_status 
        FROM student_evaluations 
        WHERE student_id = %s 
        ORDER BY semester ASC
    """
    cursor.execute(query, (student_id,))
    results = cursor.fetchall()
    conn.close()
    return results

