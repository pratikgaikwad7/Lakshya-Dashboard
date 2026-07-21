import datetime

from models.db import get_db_connection
from models.students.helpers import calculate_end_date, normalize_plant_location

def get_filter_options(plant_location_restriction=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    select_distinct = "SELECT DISTINCT {col} FROM students WHERE {col} IS NOT NULL"
    order_by = " ORDER BY {col} ASC"
    
    if plant_location_restriction:
        locations = [plant_location_restriction]
    else:
        cursor.execute(select_distinct.format(col="plant_location") + order_by.format(col="plant_location"))
        locations = [row['plant_location'] for row in cursor.fetchall()]

    dept_query = select_distinct.format(col="department")
    params = []
    if plant_location_restriction:
        dept_query += " AND plant_location = %s"
        params.append(plant_location_restriction)
    
    cursor.execute(dept_query + order_by.format(col="department"), tuple(params))
    departments = [row['department'] for row in cursor.fetchall()]

    branch_query = select_distinct.format(col="diploma_branch")
    if plant_location_restriction:
        branch_query += " AND plant_location = %s"
    cursor.execute(branch_query + order_by.format(col="diploma_branch"), tuple(params))
    branches = [row['diploma_branch'] for row in cursor.fetchall()]

    func_query = select_distinct.format(col="`function`")
    if plant_location_restriction:
        func_query += " AND plant_location = %s"
    
    cursor.execute(func_query + order_by.format(col="`function`"), tuple(params))
    functions = [row['function'] for row in cursor.fetchall()]

    stream_query = select_distinct.format(col="bits_stream")
    if plant_location_restriction:
        stream_query += " AND plant_location = %s"
    
    cursor.execute(stream_query + order_by.format(col="bits_stream"), tuple(params))
    bits_streams = [row['bits_stream'] for row in cursor.fetchall()]

    year_query = select_distinct.format(col="batch_year")
    if plant_location_restriction:
        year_query += " AND plant_location = %s"
        
    cursor.execute(year_query + " ORDER BY batch_year DESC", tuple(params))
    years = [row['batch_year'] for row in cursor.fetchall()]

    batch_query = select_distinct.format(col="batch_no")
    if plant_location_restriction:
        batch_query += " AND plant_location = %s"
        
    cursor.execute(batch_query + order_by.format(col="batch_no"), tuple(params))
    batch_nos = [row['batch_no'] for row in cursor.fetchall()]

    conn.close()
    
    return {
        'locations': locations,
        'departments': departments,
        'branches': branches,
        'functions': functions,
        'bits_streams': bits_streams,
        'years': years,
        'batch_nos': batch_nos
    }

def get_all_students(filters=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            id, email, employee_name, ticket_no, diploma_branch, gender, mobile_no, 
            department, bc_no, reporting_manager, `function`, plant_location, 
            batch_year, batch_no, status, bits_stream,
            DATE_FORMAT(date_of_joining, '%Y-%m-%d') as date_of_joining,
            DATE_FORMAT(end_date, '%Y-%m-%d') as end_date
        FROM students 
        WHERE 1=1
    """
    params = []

    if filters:
        if filters.get('plant_location'):
            query += " AND plant_location = %s"
            params.append(filters['plant_location'])
        
        if filters.get('year'):
            query += " AND batch_year = %s"
            params.append(filters['year'])
            
        if filters.get('department'):
            query += " AND department = %s"
            params.append(filters['department'])
            
        if filters.get('batch_no'):
            query += " AND batch_no = %s"
            params.append(filters['batch_no'])
            
        if filters.get('function'):
            query += " AND `function` = %s"
            params.append(filters['function'])
            
        if filters.get('bits_stream'):
            query += " AND bits_stream = %s"
            params.append(filters['bits_stream'])
        
        if filters.get('student_status'):
            query += " AND status = %s"
            params.append(filters['student_status'])

    query += " ORDER BY id DESC"
    
    cursor.execute(query, tuple(params))
    students = cursor.fetchall()
    conn.close()
    return students

def add_student(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.start_transaction()
        first_name = data.get('first_name', '').strip()
        middle_name = data.get('middle_name', '').strip()
        surname = data.get('surname', '').strip()
        employee_name = " ".join(filter(None, [first_name, middle_name, surname]))
        if not employee_name:
            raise ValueError("Employee name cannot be empty")

        doj = str(data.get('date_of_joining')).strip() if data.get('date_of_joining') else None
        end_date_val = calculate_end_date(doj)
        status_val = data.get('status', 'active')
        if status_val != 'dropped':
            status_val = 'completed' if end_date_val and end_date_val <= datetime.date.today() else 'active'

        clean_location = normalize_plant_location(data.get('plant_location'))
        cursor.execute("""
            INSERT INTO students
            (email, employee_name, ticket_no, diploma_branch, gender, mobile_no, department, bc_no,
             reporting_manager, `function`, date_of_joining, plant_location, batch_year, batch_no,
             status, end_date, bits_stream)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('email') or None, employee_name, data.get('ticket_no', '').strip(),
            data.get('diploma_branch') or None, data.get('gender', '').strip(),
            data.get('mobile_no', '').strip(), data.get('department') or None,
            data.get('bc_no') or None, data.get('reporting_manager') or None,
            data.get('function') or None, doj, clean_location, data.get('batch_year') or None,
            data.get('batch_no') or None, status_val, end_date_val, data.get('bits_stream') or None,
        ))
        student_id = cursor.lastrowid

        if status_val == 'active':
            cursor.execute("""
                INSERT INTO student_evaluations (student_id, semester, semester_status)
                VALUES (%s, 1, 'ongoing')
            """, (student_id,))

        conn.commit()
        return student_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_student_by_id(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, email, employee_name, ticket_no, diploma_branch, gender, mobile_no,
                   department, bc_no, reporting_manager, `function`, plant_location,
                   batch_year, batch_no, status, bits_stream, date_of_joining, end_date
            FROM students
            WHERE id = %s
        """, (student_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def update_student(student_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    first_name = data.get('first_name', '').strip()
    middle_name = data.get('middle_name', '').strip()
    surname = data.get('surname', '').strip()
    
    employee_name = " ".join(filter(None, [first_name, middle_name, surname]))
    
    if not employee_name:
        conn.close()
        raise ValueError("Employee name cannot be empty")

    doj = data.get('date_of_joining')
    
    if doj:
        doj = str(doj).strip()
    else:
        doj = None
        
    end_date_val = calculate_end_date(doj)
    
    current_status = data.get('status', 'active')
    new_status = current_status
    
    if current_status != 'dropped':
        if end_date_val and end_date_val <= datetime.date.today():
            new_status = 'completed'
        else:
            new_status = 'active'
    
    # NORMALIZE LOCATION
    clean_location = normalize_plant_location(data.get('plant_location'))

    query = """
        UPDATE students SET
        email = %s, employee_name = %s, ticket_no = %s, diploma_branch = %s,
        gender = %s, mobile_no = %s, department = %s, bc_no = %s,
        reporting_manager = %s, `function` = %s, date_of_joining = %s,
        plant_location = %s, batch_year = %s, batch_no = %s, status = %s, end_date = %s, bits_stream = %s
        WHERE id = %s
    """
    values = (
        data.get('email') or None, 
        employee_name, 
        data.get('ticket_no', '').strip(),
        data.get('diploma_branch') or None, 
        data.get('gender', '').strip(), 
        data.get('mobile_no', '').strip(),
        data.get('department') or None, 
        data.get('bc_no') or None, 
        data.get('reporting_manager') or None,
        data.get('function') or None, 
        doj, 
        clean_location,
        data.get('batch_year') or None, 
        data.get('batch_no') or None, 
        new_status, end_date_val, 
        data.get('bits_stream') or None,
        student_id
    )
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return True

def delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
    conn.commit()
    conn.close()
    return True

def get_dashboard_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as total FROM students")
    total_students = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(DISTINCT department) as total FROM students WHERE department IS NOT NULL")
    total_departments = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(DISTINCT diploma_branch) as total FROM students WHERE diploma_branch IS NOT NULL")
    total_branches = cursor.fetchone()['total']
    cursor.execute("SELECT * FROM students ORDER BY id DESC LIMIT 5")
    recent_students = cursor.fetchall()
    conn.close()
    return total_students, total_departments, total_branches, recent_students

def get_student_ticket_id_map(plant_location=None, active_only=False):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, ticket_no FROM students WHERE ticket_no IS NOT NULL"
    params = []
    if plant_location:
        query += " AND plant_location = %s"
        params.append(plant_location)
    if active_only:
        query += " AND status = 'active'"
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    ticket_map = {row['ticket_no']: row['id'] for row in rows}
    conn.close()
    return ticket_map
