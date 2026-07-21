from models.db import get_db_connection

def init_evaluation_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SHOW TABLES LIKE 'student_evaluations'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        create_table = """
            CREATE TABLE student_evaluations (
                id INT AUTO_INCREMENT PRIMARY KEY, student_id INT NOT NULL, semester INT DEFAULT 1,
                semester_status ENUM('ongoing', 'completed') DEFAULT 'ongoing',
                score_attendance INT DEFAULT 0, score_suggestions INT DEFAULT 0, score_projects INT DEFAULT 0,
                score_recognitions INT DEFAULT 0, score_safety INT DEFAULT 0, score_discipline INT DEFAULT 0,
                score_bits_attendance INT DEFAULT 0, score_equipment INT DEFAULT 0, score_shop_task INT DEFAULT 0,
                score_function_output INT DEFAULT 0, training_marks DECIMAL(10, 2) DEFAULT 0, bits_cgpa DECIMAL(5, 2) DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                UNIQUE KEY unique_student_sem (student_id, semester),
                calc_training_total DECIMAL(10, 2) GENERATED ALWAYS AS (ROUND((COALESCE(training_marks, 0) / 100) * 20, 2)) STORED,
                calc_ojt_total DECIMAL(10, 2) GENERATED ALWAYS AS (ROUND(((COALESCE(score_attendance, 0) + COALESCE(score_suggestions, 0) + COALESCE(score_projects, 0) + COALESCE(score_recognitions, 0) + COALESCE(score_safety, 0) + COALESCE(score_discipline, 0) + COALESCE(score_bits_attendance, 0) + COALESCE(score_equipment, 0) + COALESCE(score_shop_task, 0) + COALESCE(score_function_output, 0)) / 100) * 50, 2)) STORED,
                calc_bits_total DECIMAL(10, 2) GENERATED ALWAYS AS (ROUND((COALESCE(bits_cgpa, 0) * 3), 2)) STORED,
                calc_grand_total DECIMAL(10, 2) GENERATED ALWAYS AS (ROUND(COALESCE(calc_training_total, 0) + COALESCE(calc_ojt_total, 0) + COALESCE(calc_bits_total, 0), 2)) STORED
            )
        """
        cursor.execute(create_table)
        conn.commit()
    else:
        cursor.execute("SHOW COLUMNS FROM student_evaluations LIKE 'semester_status'")
        column_exists = cursor.fetchone()
        if not column_exists:
            print("Migrating: Adding semester_status column")
            cursor.execute("ALTER TABLE student_evaluations ADD COLUMN semester_status ENUM('ongoing', 'completed') DEFAULT 'ongoing'")
            conn.commit()

    conn.close()
    print("Database table 'student_evaluations' verified/created.")

def create_initial_evaluation(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT IGNORE INTO student_evaluations (student_id, semester, semester_status)
            VALUES (%s, 1, 'ongoing')
        """
        cursor.execute(query, (student_id,))
        conn.commit()
    except Exception as e:
        print(f"Error creating initial evaluation: {e}")
        conn.rollback()
    finally:
        conn.close()

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

# ---------------------------------------------------------
# HELPER TO BUILD WHERE CLAUSE (UPDATED FOR LIST SUPPORT)
# ---------------------------------------------------------
def _build_filter_conditions(filters, table_prefix_student='s', table_prefix_eval='e'):
    conditions = []
    params = []

    # Helper to handle single value or list
    def _add_condition(col_name, value, operator='='):
        if value is None or value == '':
            return
        if isinstance(value, list):
            if len(value) > 0:
                placeholders = ','.join(['%s'] * len(value))
                conditions.append(f"{col_name} IN ({placeholders})")
                params.extend(value)
        else:
            if operator == 'LIKE':
                conditions.append(f"{col_name} LIKE %s")
                params.append(f"%{value}%")
            else:
                conditions.append(f"{col_name} = %s")
                params.append(value)

    if filters.get('semester'):
        _add_condition(f"{table_prefix_eval}.semester", filters['semester'])

    if filters.get('student_status'):
        _add_condition(f"{table_prefix_student}.status", filters['student_status'])

    if filters.get('semester_status'):
        _add_condition(f"{table_prefix_eval}.semester_status", filters['semester_status'])

    if filters.get('year'):
        _add_condition(f"{table_prefix_student}.batch_year", filters['year'])

    if filters.get('batch_no'):
        _add_condition(f"{table_prefix_student}.batch_no", filters['batch_no'])

    if filters.get('branch'):
        _add_condition(f"{table_prefix_student}.diploma_branch", filters['branch'])

    if filters.get('department'):
        _add_condition(f"{table_prefix_student}.department", filters['department'])

    if filters.get('gender'):
        _add_condition(f"{table_prefix_student}.gender", filters['gender'])

    if filters.get('function'):
        _add_condition(f"{table_prefix_student}.`function`", filters['function'])

    if filters.get('bits_stream'):
        _add_condition(f"{table_prefix_student}.bits_stream", filters['bits_stream'])

    if filters.get('ticket_no'):
        _add_condition(f"{table_prefix_student}.ticket_no", filters['ticket_no'], 'LIKE')

    if filters.get('employee_name'):
        _add_condition(f"{table_prefix_student}.employee_name", filters['employee_name'], 'LIKE')

    if filters.get('plant_location'):
        _add_condition(f"{table_prefix_student}.plant_location", filters['plant_location'])

    if filters.get('reporting_manager'):
        _add_condition(f"{table_prefix_student}.reporting_manager", filters['reporting_manager'])

    if filters.get('doj_start'):
        conditions.append(f"{table_prefix_student}.date_of_joining >= %s")
        params.append(filters['doj_start'])

    if filters.get('doj_end'):
        conditions.append(f"{table_prefix_student}.date_of_joining <= %s")
        params.append(filters['doj_end'])

    if filters.get('bits_cgpa_min'):
        conditions.append(f"{table_prefix_eval}.bits_cgpa >= %s")
        params.append(filters['bits_cgpa_min'])

    if filters.get('bits_cgpa_max'):
        conditions.append(f"{table_prefix_eval}.bits_cgpa <= %s")
        params.append(filters['bits_cgpa_max'])

    if filters.get('training_marks_min'):
        conditions.append(f"{table_prefix_eval}.training_marks >= %s")
        params.append(filters['training_marks_min'])

    if filters.get('training_marks_max'):
        conditions.append(f"{table_prefix_eval}.training_marks <= %s")
        params.append(filters['training_marks_max'])

    if filters.get('grand_total_min'):
        conditions.append(f"{table_prefix_eval}.calc_grand_total >= %s")
        params.append(filters['grand_total_min'])

    if filters.get('grand_total_max'):
        conditions.append(f"{table_prefix_eval}.calc_grand_total <= %s")
        params.append(filters['grand_total_max'])
        
    return conditions, params


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

def get_evaluation_dashboard_stats(filters):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    conditions, params = _build_filter_conditions(filters)
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    
    summary_query = f"""
        SELECT 
            COUNT(DISTINCT s.id) as total_count,
            COUNT(DISTINCT CASE WHEN s.gender = 'Male' THEN s.id END) as male_count,
            COUNT(DISTINCT CASE WHEN s.gender = 'Female' THEN s.id END) as female_count,
            COUNT(DISTINCT s.batch_no) as batch_count
        FROM students s
        LEFT JOIN student_evaluations e ON s.id = e.student_id
        {where_clause}
    """
    
    cursor.execute(summary_query, tuple(params))
    summary_data = cursor.fetchone()
    
    sem_query = f"""
        SELECT 
            e.semester,
            COUNT(DISTINCT s.id) as total_count,
            COUNT(DISTINCT CASE WHEN s.gender = 'Male' THEN s.id END) as male_count,
            COUNT(DISTINCT CASE WHEN s.gender = 'Female' THEN s.id END) as female_count
        FROM students s
        LEFT JOIN student_evaluations e ON s.id = e.student_id
        {where_clause}
        GROUP BY e.semester
        ORDER BY e.semester ASC
    """
    
    cursor.execute(sem_query, tuple(params))
    semester_data = cursor.fetchall()
    
    conn.close()
    
    return {
        'summary': {
            'total': summary_data['total_count'] or 0,
            'male': summary_data['male_count'] or 0,
            'female': summary_data['female_count'] or 0,
            'batches': summary_data['batch_count'] or 0
        },
        'semester_breakdown': semester_data
    }

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

        cursor.execute("SELECT id, semester FROM student_evaluations WHERE student_id = %s AND semester_status = 'ongoing' ORDER BY semester DESC LIMIT 1", (student_id,))
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
        
        cursor.execute("UPDATE student_evaluations SET semester_status = 'completed' WHERE id = %s", (current['id'],))
        cursor.execute("INSERT INTO student_evaluations (student_id, semester, semester_status) VALUES (%s, %s, 'ongoing')", (student_id, next_sem))
        
        conn.commit()
        conn.close()
        return True, f"Promoted to Semester {next_sem}"
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

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

        cursor.execute("SELECT id, semester FROM student_evaluations WHERE student_id = %s AND semester_status = 'ongoing' ORDER BY semester DESC LIMIT 1", (student_id,))
        current = cursor.fetchone()
        
        if not current:
            conn.rollback()
            conn.close()
            return False, "No active semester found."
            
        if current['semester'] != 7:
            conn.rollback()
            conn.close()
            return False, "Can only end Semester 7."

        cursor.execute("UPDATE student_evaluations SET semester_status = 'completed' WHERE id = %s", (current['id'],))
        
        conn.commit()
        conn.close()
        return True, "Semester 7 Ended Successfully!"
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

def upsert_evaluation_scores(student_id, semester, data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT status FROM students WHERE id = %s", (student_id,))
    student = cursor.fetchone()
    
    if not student or student['status'] != 'active':
        conn.close()
        return False, "Evaluation locked: Student is not active."

    cursor.execute("SELECT id, semester_status FROM student_evaluations WHERE student_id = %s AND semester = %s", (student_id, semester))
    record = cursor.fetchone()
    
    if not record or record['semester_status'] != 'ongoing':
        conn.close()
        return False, "Evaluation locked: Semester is not ongoing."

    if semester < 1 or semester > 7:
        conn.close()
        return False, "Invalid semester."

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
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return True, "Scores updated successfully."

def calculate_final_evaluation(student):
    ojt_marks = (
        (student.get("score_attendance") or 0) +
        (student.get("score_suggestions") or 0) +
        (student.get("score_projects") or 0) +
        (student.get("score_recognitions") or 0) +
        (student.get("score_safety") or 0) +
        (student.get("score_discipline") or 0) +
        (student.get("score_bits_attendance") or 0) +
        (student.get("score_equipment") or 0) +
        (student.get("score_shop_task") or 0) +
        (student.get("score_function_output") or 0)
    )

    return {
        "training_marks": float(student.get("training_marks") or 0),
        "ojt_marks": float(ojt_marks),
        "bits_cgpa": float(student.get("bits_cgpa") or 0),

        "training_total": float(student.get("calc_training_total") or 0),
        "ojt_total": float(student.get("calc_ojt_total") or 0),
        "bits_total": float(student.get("calc_bits_total") or 0),

        "grand_total": float(student.get("calc_grand_total") or 0)
    }

def get_batch_performance_trend():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            s.batch_year,
            e.semester,
            AVG(e.calc_grand_total) as avg_score
        FROM students s
        JOIN student_evaluations e ON s.id = e.student_id
        WHERE s.batch_year IS NOT NULL AND e.semester IS NOT NULL
        GROUP BY s.batch_year, e.semester
        ORDER BY s.batch_year DESC, e.semester ASC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    performance_data = {}
    years = set()
    
    for row in results:
        year = row['batch_year']
        sem = row['semester']
        score = row['avg_score']
        
        if year not in performance_data:
            performance_data[year] = {}
        
        performance_data[year][sem] = round(score, 2) if score else 0
        years.add(year)
        
    return {
        'data': performance_data,
        'years': sorted(list(years), reverse=True)
    }

def get_location_breakdown(filters):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    conditions, params = _build_filter_conditions(filters)
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT
            s.plant_location AS location,
            COUNT(DISTINCT s.id) AS total,
            COUNT(DISTINCT CASE
                WHEN LOWER(TRIM(s.gender)) = 'male' THEN s.id
            END) AS male,
            COUNT(DISTINCT CASE
                WHEN LOWER(TRIM(s.gender)) = 'female' THEN s.id
            END) AS female
        FROM students s
        LEFT JOIN student_evaluations e ON s.id = e.student_id
        {where_clause}
        GROUP BY s.plant_location
        ORDER BY total DESC
    """

    cursor.execute(query, tuple(params))
    results = cursor.fetchall()

    conn.close()
    return results

def get_batch_breakdown(filters):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    conditions, params = _build_filter_conditions(filters)
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    
    query = f"""
        SELECT 
            s.batch_year,
            s.plant_location,
            COUNT(DISTINCT s.id) as total
        FROM students s
        LEFT JOIN student_evaluations e ON s.id = e.student_id
        {where_clause}
        GROUP BY s.batch_year, s.plant_location
    """
    
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    conn.close()

    pivot_data = {}
    all_locations = set()

    for row in results:
        year = row['batch_year']
        loc = row['plant_location']
        count = row['total']
        
        if year not in pivot_data:
            pivot_data[year] = {'_total': 0}
            
        pivot_data[year][loc] = count
        pivot_data[year]['_total'] += count
        all_locations.add(loc)

    sorted_locations = sorted(list(all_locations), key=lambda x: x.replace('_', ' '))
    sorted_years = sorted(pivot_data.keys(), reverse=True)
    
    return {
        'data': pivot_data,
        'locations': sorted_locations,
        'years': sorted_years
    }

# ---------------------------------------------------------
# UPDATED PERFORMANCE DISTRIBUTION (COMPLETED ONLY)
# ---------------------------------------------------------
def get_performance_distribution(filters, score_type='all'):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Determine Column and Ranges based on score_type
    if score_type == 'bits':
        target_col = 'e.calc_bits_total'
        buckets = [
            ("0-5", 0, 5), ("5-10", 5, 10), ("10-15", 10, 15),
            ("15-20", 15, 20), ("20-25", 20, 25), ("25-30", 25, 30.01)
        ]
    elif score_type == 'ojt':
        target_col = 'e.calc_ojt_total'
        buckets = [
            ("0-10", 0, 10), ("10-20", 10, 20), ("20-30", 20, 30),
            ("30-40", 30, 40), ("40-50", 40, 50.01)
        ]
    elif score_type == 'training':
        target_col = 'e.calc_training_total'
        buckets = [
            ("0-5", 0, 5), ("5-10", 5, 10), ("10-15", 10, 15), ("15-20", 15, 20.01)
        ]
    else: # 'all' -> Grand Total
        target_col = 'e.calc_grand_total'
        buckets = [
            ("0-40", 0, 40), ("40-50", 40, 50), ("50-60", 50, 60),
            ("60-70", 60, 70), ("70-80", 70, 80), ("80-100", 80, 100.01)
        ]

    # Build Filter Conditions
    conditions, params = _build_filter_conditions(filters)
    
    # IMPORTANT: Only include COMPLETED semesters in charts
    conditions.append("e.semester_status = 'completed'")
    
    # Only count rows where the target score is not null
    conditions.append(f"{target_col} IS NOT NULL")
    
    where_clause = " AND ".join(conditions)
    
    # Dynamic SQL Generation for Buckets
    select_parts = []
    for label, low, high in buckets:
        op = "<" if high != buckets[-1][1] else "<="
        if low == 0:
            part = f"SUM(CASE WHEN {target_col} >= {low} AND {target_col} {op} {high} THEN 1 ELSE 0 END) AS `bucket_{label}`"
        else:
            part = f"SUM(CASE WHEN {target_col} >= {low} AND {target_col} {op} {high} THEN 1 ELSE 0 END) AS `bucket_{label}`"
        select_parts.append(part)
    
    query = f"""
        SELECT {', '.join(select_parts)}
        FROM students s
        JOIN student_evaluations e ON s.id = e.student_id
        WHERE {where_clause}
    """
    
    cursor.execute(query, tuple(params))
    row = cursor.fetchone()
    conn.close()
    
    result = []
    if row:
        for label, low, high in buckets:
            key = f"bucket_{label}"
            result.append({
                "range": label,
                "count": row.get(key, 0) or 0
            })
        
    return result

def get_attrition_by_location(filters):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    conditions, params = _build_filter_conditions(filters)
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT
            s.plant_location AS location,
            COUNT(DISTINCT s.id) AS total_students,
            COUNT(DISTINCT CASE 
                WHEN s.status = 'dropped' THEN s.id
            END) AS dropped_students
        FROM students s
        LEFT JOIN student_evaluations e ON s.id = e.student_id
        {where_clause}
        GROUP BY s.plant_location
        ORDER BY total_students DESC
    """

    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    conn.close()

    return results

# ---------------------------------------------------------
# UPDATED BULK UPSERT (WITH SEMESTER PROGRESSION)
# ---------------------------------------------------------
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
        affected_rows = cursor.rowcount
        conn.close()
        return affected_rows
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e
  
# Keeping existing function for backward compatibility
def get_students_by_cgpa_range(filters, min_cgpa, max_cgpa):
    return get_students_by_score_range(filters, min_cgpa, max_cgpa, 'bits')

# ---------------------------------------------------------
# NEW GENERIC SCORE RANGE FUNCTION (COMPLETED ONLY)
# ---------------------------------------------------------
def get_students_by_score_range(filters, min_score, max_score, score_type='all'):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Map score_type to column
    col_map = {
        'bits': 'e.calc_bits_total',
        'ojt': 'e.calc_ojt_total',
        'training': 'e.calc_training_total',
        'all': 'e.calc_grand_total'
    }
    target_col = col_map.get(score_type, 'e.calc_grand_total')

    query = """
        SELECT 
            s.id, s.employee_name, s.ticket_no, s.gender, s.department, s.plant_location,
            s.email, s.mobile_no, s.bc_no, s.diploma_branch, s.function, s.reporting_manager,
            s.bits_stream, s.batch_year, s.batch_no, s.date_of_joining, s.status as student_status,
            e.semester, e.semester_status, e.bits_cgpa,
            e.calc_training_total, e.calc_bits_total, e.calc_ojt_total, e.calc_grand_total
        FROM students s
        JOIN student_evaluations e ON s.id = e.student_id
    """
    
    conditions, params = _build_filter_conditions(filters)
    
    # IMPORTANT: Chart modal should only show COMPLETED semesters
    conditions.append("e.semester_status = 'completed'")
    
    # Add Score Range Condition
    max_possible = {
        'bits': 30, 'ojt': 50, 'training': 20, 'all': 100
    }.get(score_type, 100)

    if max_score >= max_possible:
        conditions.append(f"{target_col} >= %s")
        params.append(min_score)
    else:
        conditions.append(f"{target_col} >= %s AND {target_col} < %s")
        params.extend([min_score, max_score])

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    
    query += where_clause + f" ORDER BY {target_col} DESC"

    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    conn.close()
    return results
def get_branch_location_breakdown(filters):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    conditions, params = _build_filter_conditions(filters)
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    
    query = f"""
        SELECT 
            s.diploma_branch,
            s.plant_location,
            COUNT(DISTINCT s.id) as total
        FROM students s
        LEFT JOIN student_evaluations e ON s.id = e.student_id
        {where_clause}
        GROUP BY s.diploma_branch, s.plant_location
    """
    
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    conn.close()

    pivot_data = {}
    all_locations = set()

    for row in results:
        branch = row['diploma_branch'] or 'Unknown'
        loc = row['plant_location'] or 'Unknown'
        count = row['total']
        
        if branch not in pivot_data:
            pivot_data[branch] = {'_total': 0}
            
        pivot_data[branch][loc] = count
        pivot_data[branch]['_total'] += count
        all_locations.add(loc)

    sorted_locations = sorted(list(all_locations), key=lambda x: x.replace('_', ' '))
    sorted_branches = sorted(pivot_data.keys())
    
    return {
        'data': pivot_data,
        'locations': sorted_locations,
        'branches': sorted_branches
    }