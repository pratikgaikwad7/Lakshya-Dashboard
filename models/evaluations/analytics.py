from models.db import get_db_connection
from models.evaluations.filters import _build_filter_conditions

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
    for row in results:
        row['location'] = row['location'] or 'Unknown'
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
        year = row['batch_year'] if row['batch_year'] is not None else 'Unknown'
        loc = row['plant_location'] or 'Unknown'
        count = row['total']
        
        if year not in pivot_data:
            pivot_data[year] = {'_total': 0}
            
        pivot_data[year][loc] = count
        pivot_data[year]['_total'] += count
        all_locations.add(loc)

    sorted_locations = sorted(list(all_locations), key=lambda x: x.replace('_', ' '))
    numeric_years = sorted((year for year in pivot_data if year != 'Unknown'), reverse=True)
    sorted_years = numeric_years + (['Unknown'] if 'Unknown' in pivot_data else [])
    
    return {
        'data': pivot_data,
        'locations': sorted_locations,
        'years': sorted_years
    }

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

    for row in results:
        row['location'] = row['location'] or 'Unknown'

    return results

def get_students_by_cgpa_range(filters, min_cgpa, max_cgpa):
    return get_students_by_score_range(filters, min_cgpa, max_cgpa, 'bits')

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
