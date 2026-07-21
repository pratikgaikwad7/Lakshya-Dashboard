from models.db import get_db_connection

def init_db():
    """Creates table if not exists and handles migrations."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    create_table = """
    CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255),
        employee_name VARCHAR(255) NOT NULL,
        ticket_no VARCHAR(100) NOT NULL,
        diploma_branch VARCHAR(255),
        gender VARCHAR(50) NOT NULL,
        mobile_no VARCHAR(20) NOT NULL,
        department VARCHAR(255),
        bc_no VARCHAR(100),
        reporting_manager VARCHAR(255),
        erc_operation VARCHAR(255),
        date_of_joining DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_table)
    conn.commit()

    # MIGRATION LOGIC
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'students' AND column_name = 'function'
    """)
    function_exists = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.columns 
        WHERE table_schema = DATABASE() AND table_name = 'students' AND column_name = 'erc_operation'
    """)
    erc_exists = cursor.fetchone()[0]

    if erc_exists and not function_exists:
        print("Migrating database: Renaming 'erc_operation' to 'function'")
        cursor.execute("ALTER TABLE students CHANGE COLUMN erc_operation `function` VARCHAR(255)")
        conn.commit()
    
    def column_exists(column_name):
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_schema = DATABASE() AND table_name = 'students' AND column_name = %s
        """, (column_name,))
        return cursor.fetchone()[0] > 0

    if not column_exists('plant_location'):
        cursor.execute("ALTER TABLE students ADD COLUMN plant_location VARCHAR(100)")

    if not column_exists('batch_year'):
        cursor.execute("ALTER TABLE students ADD COLUMN batch_year INT")

    if not column_exists('batch_no'):
        cursor.execute("ALTER TABLE students ADD COLUMN batch_no INT")

    if not column_exists('status'):
        print("Migrating database: Adding 'status' column")
        cursor.execute("ALTER TABLE students ADD COLUMN status VARCHAR(50) DEFAULT 'active'")
        conn.commit()

    if not column_exists('end_date'):
        print("Migrating database: Adding 'end_date' column")
        cursor.execute("ALTER TABLE students ADD COLUMN end_date DATE")
        conn.commit()
        
    if not column_exists('bits_stream'):
        print("Migrating database: Adding 'bits_stream' column")
        cursor.execute("ALTER TABLE students ADD COLUMN bits_stream VARCHAR(255)")
        conn.commit()

    conn.commit()
    conn.close()

def check_and_update_completion_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            UPDATE students 
            SET status = 'completed' 
            WHERE status = 'active' 
            AND end_date IS NOT NULL 
            AND end_date <= CURDATE()
        """
        cursor.execute(query)
        conn.commit()
        return cursor.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
