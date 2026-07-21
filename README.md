# Lakshya Dashboard

Lakshya Dashboard is a Flask and MySQL application for managing trainees, semester evaluations, Excel imports, user access, and aggregate performance reporting across plant locations.

## Features

- Student registration, updates, filtering, status tracking, and Excel import
- Semester 1–7 evaluation entry and controlled semester progression
- Evaluation Excel import with row-level validation feedback
- Admin and user dashboards with location, batch, branch, gender, and score analysis
- Role-aware access for Admin, PMO, SDC Coordinator, HR Head, and other dashboard users
- Plant-location restrictions for SDC Coordinator and HR Head dashboard data

## Project structure

```text
app.py                         Flask application factory and blueprint registration
config.py                      Development, testing, and production configuration
extensions.py                  CSRF, login manager, and rate limiter instances
exceptions.py                  Stable application/domain errors
security/                      Authentication, role, and plant-access policies
schemas/                       Request normalization and validation
models/
  db.py                        MySQL connection factory
  evaluation_model.py          Backward-compatible evaluation API
  evaluations/                 Evaluation schema, queries, lifecycle, and analytics
  student_model.py             Backward-compatible student API
  students/                    Student schema, repository, and normalization helpers
  user_model.py                User persistence and authentication queries
routes/                         HTTP blueprints only
services/student_service.py     Authorized student business operations
services/excel/                Reusable student and evaluation workbook import services
migrations/                    Versioned SQL integrity and index migrations
scripts/                       Database initialization and migration commands
templates/
  partials/                    Page sections composed by Jinja templates
static/
  css/pages/                   Page-specific styles extracted from templates
  js/dashboard/                Dashboard behavior grouped by responsibility
  js/evaluations/              Evaluation list and sheet behavior
  js/students/                 Student list, form, batch, and upload behavior
docs/PRD.md                    Product requirements
docs/SRS.md                    Software requirements and technical specification
tests/                          Pure logic and application-structure tests
```

The `models/evaluation_model.py` and `models/student_model.py` files intentionally remain as compatibility facades. Existing imports keep working while new code can target the focused modules.

## Local setup

1. Create and activate a Python virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a MySQL database and a user with permission to create and alter tables:

   ```sql
   CREATE DATABASE lakshya_dashboard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

4. Copy `.env.example` to `.env` and set the database credentials and a strong `SECRET_KEY`:

   ```bash
   cp .env.example .env
   ```

5. Initialize the base application tables, then apply versioned migrations:

   ```bash
   python3 -m scripts.init_database
   python3 -m scripts.apply_migrations
   ```

   Existing databases must not contain duplicate ticket numbers, invalid scores, or multiple ongoing semesters before migration `001_security_integrity.py` is applied.

6. Create the first database-backed administrator. For local development,
   setting `AUTO_CREATE_ADMIN=true` creates it automatically on the first
   request after startup:

   ```bash
   flask --app app create-admin
   ```

   The command is only needed when automatic creation is disabled. It reads
   `LAKSHYA_BOOTSTRAP_ADMIN_USERNAME` and `LAKSHYA_BOOTSTRAP_ADMIN_PASSWORD`
   from `.env`, so it can also run without interactive prompts. Neither method
   overwrites an existing account. Login
   always checks the hashed database password. Automatic creation is forcibly
   disabled by the production configuration.

7. Run the application:

   ```bash
   python3 app.py
   ```

8. Open `http://127.0.0.1:5001`.

The database itself must already exist. Schema changes are explicit commands and never run as a side effect of importing routes or starting a worker.

Expired active students are updated explicitly, never during GET requests:

```bash
flask --app app update-student-statuses
```

## Development checks

Install development dependencies, then run:

```bash
pip install -r requirements-dev.txt
python3 -m unittest discover -s tests
python3 -m compileall -q app.py config.py extensions.py exceptions.py models routes schemas security services scripts utils
```

JavaScript syntax can be checked when Node.js is available:

```bash
find static/js -name '*.js' -print0 | xargs -0 -n1 node --check
```

## Excel formats

The sample student workbook is stored at `File format/Stdent records.xlsx`. Student imports require `Full Name`, `Ticket No`, and `Gender`. Evaluation imports require `Ticket No` and `Semester`; score columns are optional and default to zero. `.xlsx` uses `openpyxl`, while legacy `.xls` support uses `xlrd`.

## Security notes

- Never commit `.env`; it is ignored by Git.
- Student management is restricted to Admin, PMO, and SDC Coordinator. Coordinator requests are always forced to the assigned plant and fail closed when no plant is assigned.
- Evaluation management is restricted to Admin and SDC Coordinator, including plant-scoped evaluation imports.
- All cookie-authenticated mutations require CSRF tokens, and logout is POST-only.
- Login attempts and workbook uploads are rate limited.
- Run behind a production WSGI server with TLS and debug mode disabled in production.
- Set `APP_ENV=production`, `SESSION_COOKIE_SECURE=true`, and a shared production rate-limit storage URI.
- Restrict database permissions and rotate credentials regularly.

Example production command:

```bash
APP_ENV=production gunicorn --workers 3 --bind 0.0.0.0:5001 app:app
```

Product scope and acceptance criteria are in [docs/PRD.md](docs/PRD.md). Technical behavior and interfaces are in [docs/SRS.md](docs/SRS.md).
