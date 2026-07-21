from schemas.common import ensure_list, require_mapping


LIST_FILTERS = (
    "year", "plant_location", "semester", "student_status", "bits_stream", "gender"
)
SINGLE_FILTERS = ("department", "function", "branch", "batch_no", "ticket_no")


def dashboard_filters_from_json(payload):
    data = require_mapping(payload)
    filters = {name: ensure_list(data.get(name)) for name in LIST_FILTERS}
    filters.update({name: data.get(name) for name in SINGLE_FILTERS})
    return filters


def dashboard_filters_from_query(args):
    filters = {name: args.getlist(name) for name in LIST_FILTERS}
    filters.update({
        "department": args.getlist("department"),
        "function": args.getlist("function"),
        "branch": args.getlist("branch"),
        "batch_no": args.getlist("batch_no"),
        "ticket_no": args.get("ticket_no", ""),
    })
    if not filters["student_status"]:
        filters["student_status"] = ["active"]
    return filters
