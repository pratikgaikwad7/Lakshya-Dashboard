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

