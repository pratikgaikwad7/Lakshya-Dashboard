"""Backward-compatible evaluation model API."""

from models.evaluations.analytics import (
    get_attrition_by_location,
    get_batch_breakdown,
    get_batch_performance_trend,
    get_branch_location_breakdown,
    get_evaluation_dashboard_stats,
    get_location_breakdown,
    get_performance_distribution,
    get_students_by_cgpa_range,
    get_students_by_score_range,
)
from models.evaluations.calculations import calculate_final_evaluation
from models.evaluations.lifecycle import (
    bulk_upsert_evaluations,
    end_seventh_semester,
    promote_student_semester,
    upsert_evaluation_scores,
)
from models.evaluations.options import (
    get_distinct_batch_nos,
    get_distinct_bits_streams,
    get_distinct_branches,
    get_distinct_functions,
    get_distinct_locations,
    get_distinct_semesters,
    get_gender_options,
)
from models.evaluations.queries import (
    get_filtered_students_for_eval,
    get_student_active_evaluation,
    get_student_all_evaluations_list,
    get_student_evaluation_by_sem,
    get_student_last_evaluation,
)
from models.evaluations.schema import create_initial_evaluation, init_evaluation_db

__all__ = [
    "bulk_upsert_evaluations", "calculate_final_evaluation", "create_initial_evaluation",
    "end_seventh_semester", "get_attrition_by_location", "get_batch_breakdown",
    "get_batch_performance_trend", "get_branch_location_breakdown",
    "get_distinct_batch_nos", "get_distinct_bits_streams", "get_distinct_branches",
    "get_distinct_functions", "get_distinct_locations", "get_distinct_semesters",
    "get_evaluation_dashboard_stats", "get_filtered_students_for_eval",
    "get_gender_options", "get_location_breakdown", "get_performance_distribution",
    "get_student_active_evaluation", "get_student_all_evaluations_list",
    "get_student_evaluation_by_sem", "get_student_last_evaluation",
    "get_students_by_cgpa_range", "get_students_by_score_range",
    "init_evaluation_db", "promote_student_semester", "upsert_evaluation_scores",
]
