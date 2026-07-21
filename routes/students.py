from flask import Blueprint, render_template, request, jsonify, session
import pandas as pd
from models.student_model import get_all_students, add_student, update_student, delete_student, init_db, get_filter_options, normalize_plant_location

students_bp = Blueprint('students', __name__)

# Initialize DB table when this route file is loaded
init_db()

@students_bp.route('/students')
def index():
    if 'username' not in session:
        return render_template('login.html')
    return render_template('students.html')

@students_bp.route('/api/students/filters', methods=['GET'])
def api_get_filters():
    """API endpoint to get dropdown options for filters"""
    try:
        restriction = None
        if session.get('role') == 'SDC Coordinator':
            restriction = session.get('plant_location')
            
        options = get_filter_options(plant_location_restriction=restriction)
        return jsonify(options)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@students_bp.route('/api/students', methods=['GET'])
def api_get_students():
    filters = {
        'plant_location': request.args.get('location'),
        'year': request.args.get('year'),
        'department': request.args.get('department'),
        'batch_no': request.args.get('batch_no'),
        'function': request.args.get('function'),
        'bits_stream': request.args.get('bits_stream'),
        'status': request.args.get('status')
    }
    
    if session.get('role') == 'SDC Coordinator':
        user_loc = session.get('plant_location')
        if user_loc:
            filters['plant_location'] = user_loc
    
    filters = {k: v for k, v in filters.items() if v}
    data = get_all_students(filters)
    return jsonify(data)

@students_bp.route('/api/students', methods=['POST'])
def api_add_student():
    try:
        data = request.json
        
        if session.get('role') == 'SDC Coordinator':
            data['plant_location'] = session.get('plant_location')

        # MODIFIED: Removed 'surname' from required list to handle single names
        required = ['first_name', 'ticket_no', 'gender']
        for field in required:
            if not data.get(field) or str(data.get(field)).strip() == "":
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400
        
        new_id = add_student(data)
        return jsonify({'success': True, 'id': new_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@students_bp.route('/api/students/<int:id>', methods=['PUT'])
def api_update_student(id):
    try:
        data = request.json
        
        # MODIFIED: Removed 'surname' from required list to handle single names
        required = ['first_name', 'ticket_no', 'gender']
        for field in required:
            if not data.get(field) or str(data.get(field)).strip() == "":
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400
        
        if session.get('role') == 'SDC Coordinator':
            user_loc = session.get('plant_location')
            if user_loc:
                data['plant_location'] = user_loc

        update_student(id, data)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@students_bp.route('/api/students/<int:id>', methods=['DELETE'])
def api_delete_student(id):
    try:
        delete_student(id)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- EXCEL UPLOAD ROUTE ---
@students_bp.route('/api/students/upload-excel', methods=['POST'])
def upload_excel():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if not file.filename.endswith(('.xlsx', '.xls')):
         return jsonify({'error': 'Invalid file type. Only .xlsx or .xls allowed'}), 400

    try:
        df = pd.read_excel(file)
        
        # ---------------------------------------------------------
        # ROBUST COLUMN MAPPING (CASE INSENSITIVE)
        # ---------------------------------------------------------
        # 1. Strip whitespace from column names
        df.columns = df.columns.str.strip()
        
        # 2. Create a mapping dictionary: { 'normalized_name': 'Actual DataFrame Name' }
        col_map = {}
        for col in df.columns:
            # Lowercase and remove spaces/underscores for matching
            clean_key = str(col).lower().replace(' ', '').replace('_', '')
            col_map[clean_key] = col

        # 3. Helper to get value regardless of case/format
        def get_val(row, standard_name):
            # Convert standard name "Ticket No" -> "ticketno"
            key = standard_name.lower().replace(' ', '').replace('_', '')
            if key in col_map:
                real_col_name = col_map[key]
                val = row.get(real_col_name)
                return val
            return None

        # Check for required columns using the flexible matcher
        required_columns_std = ['Full Name', 'Ticket No', 'Gender']
        missing_cols = []
        for col in required_columns_std:
            key = col.lower().replace(' ', '')
            if key not in col_map:
                missing_cols.append(col)
        
        if missing_cols:
            return jsonify({'error': f'Missing required columns: {", ".join(missing_cols)}'}), 400
        
        # ---------------------------------------------------------

        total_rows = len(df)
        inserted_count = 0
        skipped_count = 0
        failed_rows = []
        
        from models.db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ticket_no FROM students")
        existing_tickets = set(row[0] for row in cursor.fetchall())
        conn.close()

        for index, row in df.iterrows():
            row_num = index + 2 
            
            missing_fields = []
            for field in required_columns_std:
                val = get_val(row, field)
                if pd.isna(val) or str(val).strip() == '':
                    missing_fields.append(field)
            
            if missing_fields:
                failed_rows.append(f"Row {row_num}: Missing fields - {', '.join(missing_fields)}")
                continue

            ticket_no = str(get_val(row, 'Ticket No')).strip()
            if ticket_no in existing_tickets:
                skipped_count += 1
                continue

            full_name = str(get_val(row, 'Full Name')).strip()
            name_parts = full_name.split()
            
            # ---------------------------------------------------------
            # MODIFIED: Logic to handle single names (Mononyms)
            # ---------------------------------------------------------
            if not name_parts:
                failed_rows.append(f"Row {row_num}: Full Name is empty.")
                continue

            first_name = name_parts[0]
            
            if len(name_parts) == 1:
                # If only one name is provided, use it as first_name, leave surname empty
                surname = ''
                middle_name = ''
            else:
                # Standard logic for 2+ names
                surname = name_parts[-1]
                middle_name = ' '.join(name_parts[1:-1]) if len(name_parts) > 2 else ''
            # ---------------------------------------------------------

            doj_raw = get_val(row, 'Date of Joining')
            doj_formatted = None
            if pd.notna(doj_raw):
                try:
                    doj_formatted = pd.to_datetime(doj_raw).strftime('%Y-%m-%d')
                except:
                    pass

            status_raw = get_val(row, 'Status')
            status_val = str(status_raw).strip().lower() if pd.notna(status_raw) else 'active'

            bits_stream_raw = get_val(row, 'Bits Stream')
            
            # NORMALIZE LOCATION FROM EXCEL
            raw_location = get_val(row, 'Plant Location')
            clean_location = normalize_plant_location(raw_location)

            student_payload = {
                'first_name': first_name,
                'middle_name': middle_name,
                'surname': surname,
                'ticket_no': ticket_no,
                'gender': str(get_val(row, 'Gender')).strip(),
                'mobile_no': str(get_val(row, 'Mobile No')).strip(),
                'email': str(get_val(row, 'Email')).strip() if pd.notna(get_val(row, 'Email')) else None,
                'diploma_branch': str(get_val(row, 'Diploma Branch')).strip() if pd.notna(get_val(row, 'Diploma Branch')) else None,
                'department': str(get_val(row, 'Department')).strip() if pd.notna(get_val(row, 'Department')) else None,
                'bc_no': str(get_val(row, 'BC No')).strip() if pd.notna(get_val(row, 'BC No')) else None,
                'reporting_manager': str(get_val(row, 'Reporting Manager')).strip() if pd.notna(get_val(row, 'Reporting Manager')) else None,
                'function': str(get_val(row, 'Function')).strip() if pd.notna(get_val(row, 'Function')) else None,
                'date_of_joining': doj_formatted,
                'plant_location': clean_location,
                'batch_year': int(get_val(row, 'Batch Year')) if pd.notna(get_val(row, 'Batch Year')) else None,
                'batch_no': int(get_val(row, 'Batch No')) if pd.notna(get_val(row, 'Batch No')) else None,
                'status': status_val,
                'bits_stream': str(bits_stream_raw).strip() if pd.notna(bits_stream_raw) else None
            }

            if session.get('role') == 'SDC Coordinator':
                user_loc = session.get('plant_location')
                if student_payload['plant_location'] and student_payload['plant_location'] != user_loc:
                    failed_rows.append(f"Row {row_num}: Location mismatch. You cannot add students for {student_payload['plant_location']}.")
                    continue
                else:
                    student_payload['plant_location'] = user_loc

            try:
                add_student(student_payload)
                inserted_count += 1
                existing_tickets.add(ticket_no)
            except Exception as e:
                failed_rows.append(f"Row {row_num}: {str(e)}")

        return jsonify({
            'message': 'Upload processed',
            'total_rows': total_rows,
            'inserted': inserted_count,
            'skipped': skipped_count,
            'failed': len(failed_rows),
            'errors': failed_rows
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500