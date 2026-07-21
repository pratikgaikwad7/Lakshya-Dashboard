"""Add student uniqueness, reporting indexes, and evaluation range checks."""


def _index_exists(cursor, table, index):
    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.statistics
        WHERE table_schema = DATABASE() AND table_name = %s AND index_name = %s
    """, (table, index))
    return cursor.fetchone()[0] > 0


def _constraint_exists(cursor, table, constraint):
    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.table_constraints
        WHERE table_schema = DATABASE() AND table_name = %s AND constraint_name = %s
    """, (table, constraint))
    return cursor.fetchone()[0] > 0


def _add_index(cursor, table, name, columns, unique=False):
    if not _index_exists(cursor, table, name):
        kind = "UNIQUE INDEX" if unique else "INDEX"
        cursor.execute(f"ALTER TABLE `{table}` ADD {kind} `{name}` ({columns})")


def _add_check(cursor, table, name, expression):
    if not _constraint_exists(cursor, table, name):
        cursor.execute(f"ALTER TABLE `{table}` ADD CONSTRAINT `{name}` CHECK ({expression})")


def upgrade(cursor):
    _add_index(cursor, "students", "unique_student_ticket_no", "`ticket_no`", unique=True)
    _add_index(cursor, "students", "idx_students_plant_status", "`plant_location`, `status`")
    _add_index(cursor, "students", "idx_students_batch", "`batch_year`, `batch_no`")
    _add_index(cursor, "students", "idx_students_department", "`department`")
    _add_index(
        cursor,
        "student_evaluations",
        "idx_evaluations_status_semester",
        "`semester_status`, `semester`",
    )

    checks = {
        "chk_semester_range": "semester BETWEEN 1 AND 7",
        "chk_training_marks": "training_marks BETWEEN 0 AND 100",
        "chk_bits_cgpa": "bits_cgpa BETWEEN 0 AND 10",
        "chk_score_attendance": "score_attendance BETWEEN 0 AND 10",
        "chk_score_suggestions": "score_suggestions BETWEEN 0 AND 10",
        "chk_score_projects": "score_projects BETWEEN 0 AND 10",
        "chk_score_recognitions": "score_recognitions BETWEEN 0 AND 10",
        "chk_score_safety": "score_safety BETWEEN 0 AND 10",
        "chk_score_discipline": "score_discipline BETWEEN 0 AND 10",
        "chk_score_bits_attendance": "score_bits_attendance BETWEEN 0 AND 10",
        "chk_score_equipment": "score_equipment BETWEEN 0 AND 10",
        "chk_score_shop_task": "score_shop_task BETWEEN 0 AND 10",
        "chk_score_function_output": "score_function_output BETWEEN 0 AND 10",
    }
    for name, expression in checks.items():
        _add_check(cursor, "student_evaluations", name, expression)
