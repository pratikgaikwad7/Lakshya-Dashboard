import logging

from models.db import get_db_connection


logger = logging.getLogger(__name__)

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
    except Exception:
        conn.rollback()
        logger.exception("Could not create the initial evaluation for student %s", student_id)
        raise
    finally:
        conn.close()
