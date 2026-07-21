# Software Requirements Specification — Lakshya Dashboard

## 1. System overview

Lakshya Dashboard is a server-rendered Flask application backed by MySQL. Jinja templates provide the page structure, Tailwind CDN classes and page CSS provide styling, and browser JavaScript handles tables, filters, charts, modals, and Excel upload interactions.

## 2. Runtime dependencies

- Python 3.10 or newer
- Flask and Werkzeug
- Flask-WTF, Flask-Login, and Flask-Limiter
- MySQL 8-compatible server
- `mysql-connector-python`
- pandas, openpyxl, and xlrd for workbook imports
- Modern browser with JavaScript enabled
- Network access to configured Tailwind, Font Awesome, Google Fonts, and Chart.js CDNs

## 3. Configuration

| Variable | Required | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | Yes | Signs Flask session cookies |
| `DB_HOST` | Yes | MySQL host |
| `DB_USER` | Yes | MySQL user |
| `DB_PASSWORD` | Yes | MySQL password |
| `DB_NAME` | Yes | Existing application database |

Configuration is loaded from the process environment and local `.env` file. `.env` must not be committed.

After creating the configured database, `python3 -m scripts.init_database` creates base tables and `python3 -m scripts.apply_migrations` applies versioned integrity changes.

## 4. Architecture

```text
Browser
  -> Flask blueprint routes
      -> Excel services (for workbook workflows)
      -> compatibility model APIs
          -> focused student/evaluation modules
              -> MySQL connection factory
  <- Jinja templates + partials + static CSS/JavaScript
```

### Module responsibilities

- `routes/`: request parsing, service calls, and response selection
- `security/`: authentication, role checks, and fail-closed plant scoping
- `schemas/`: consistent request conversion and validation
- `services/student_service.py`: authorized student workflows
- `services/excel/`: workbook parsing, normalization, validation, result assembly
- `models/evaluations/schema.py`: evaluation table creation/migration
- `models/evaluations/queries.py`: evaluation record reads
- `models/evaluations/lifecycle.py`: score updates, promotion, semester completion, bulk persistence
- `models/evaluations/analytics.py`: dashboard aggregates and score drill-downs
- `models/evaluations/calculations.py`: evaluation presentation calculations
- `models/evaluations/options.py`: distinct filter-option queries
- `models/students/schema.py`: student table creation/migration and automatic completion
- `models/students/repository.py`: student reads and writes
- `models/students/helpers.py`: location and date normalization
- compatibility facades: preserve the original `models.*_model` import contract

## 5. Data model

### `users`

Stores username, password hash, role, optional plant location, and creation timestamp. Username is unique.

### `students`

Stores identity/contact details, ticket number, diploma and organizational placement, function, joining/end dates, plant, batch, status, and BITS stream. Status values used by the application are `active`, `dropped`, and `completed`.

### `student_evaluations`

Stores a student/semester record, semester status, ten OJT component scores, training marks, BITS CGPA, update timestamp, and generated weighted totals. `(student_id, semester)` is unique. Deleting a student cascades to evaluations.

Weighted totals remain:

- Training total: `(training_marks / 100) * 20`
- OJT total: `(sum of ten OJT scores / 100) * 50`
- BITS total: `bits_cgpa * 3`
- Grand total: training + OJT + BITS totals

## 6. HTTP interfaces

| Method | Path | Purpose |
| --- | --- | --- |
| GET/POST | `/login` | Show login / authenticate |
| POST | `/logout` | Clear session |
| GET | `/admin-dashboard` | Administrative summary |
| GET | `/user_dashboard` | Filtered analytics dashboard |
| POST | `/get-performance-data` | Score distribution data |
| POST | `/get-students-in-range` | Score bucket drill-down |
| GET | `/students` | Student management page |
| GET/POST | `/api/students` | List / create students |
| PUT/DELETE | `/api/students/<id>` | Update / delete a student |
| GET | `/api/students/filters` | Student filter options |
| POST | `/api/students/upload-excel` | Import student workbook |
| GET | `/evaluations` | Evaluation list |
| GET/POST | `/evaluations/<student_id>` | View / update a semester |
| POST | `/evaluations/<student_id>/promote` | Complete and promote Semester 1–6 |
| POST | `/evaluations/<student_id>/end-semester-seven` | Complete Semester 7 |
| GET/POST | `/evaluations/upload-excel` | Show / process evaluation import |
| GET | `/users` | List users |
| POST | `/users/add` | Create a user |
| POST | `/users/delete/<user_id>` | Delete a user |

## 7. Validation and authorization rules

- Protected evaluation and dashboard routes require an authenticated session.
- Student management is restricted to Admin, PMO, and SDC Coordinator.
- Evaluation management is restricted to Admin and SDC Coordinator.
- Every SDC Coordinator student/evaluation read and write is forced to the assigned plant; accounts without a plant are denied.
- HR Head and SDC Coordinator dashboard filters are forced to the assigned plant.
- All state-changing requests require a valid CSRF token.
- Required student fields are first name, ticket number, and gender.
- Semester must be between 1 and 7.
- Each OJT score must be 0–10, training marks 0–100, and BITS CGPA 0–10.
- Completed or inactive evaluation records reject score changes.

## 8. Error handling

- JSON student endpoints return an `error` field and appropriate 4xx/5xx status.
- Evaluation form routes return access/validation errors or redirect after success.
- Workbook imports isolate row validation errors and show row number, ticket number, and reason.
- Database transactions roll back semester lifecycle and bulk-import failures.

## 9. Verification requirements

- All Python modules compile without syntax errors.
- All Jinja templates and partials parse successfully.
- All JavaScript assets pass `node --check` when Node.js is available.
- Pure calculation, filtering, and normalization behavior is covered by local tests using Python's built-in `unittest` runner.
- Route/security tests run without schema side effects; full persistence verification uses an isolated MySQL test database.

## 10. Deployment constraints

The development server in `app.py` is not a production server. Production deployment must use a WSGI server, disable debug mode, provide TLS through the hosting layer, set a strong secret key and secure session cookies, configure shared rate-limit storage, and use least-privilege database credentials.
