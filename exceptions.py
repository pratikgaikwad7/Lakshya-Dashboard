class AppError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message=None):
        super().__init__(message or "An unexpected error occurred.")
        self.message = message or "An unexpected error occurred."


class ValidationError(AppError):
    status_code = 400
    code = "validation_error"


class UnauthorizedError(AppError):
    status_code = 401
    code = "unauthorized"


class ForbiddenError(AppError):
    status_code = 403
    code = "forbidden"


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"
