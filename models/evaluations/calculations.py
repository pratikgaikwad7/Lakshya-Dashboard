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

