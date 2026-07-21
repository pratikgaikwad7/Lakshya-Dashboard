# Product Requirements Document — Lakshya Dashboard

## 1. Purpose

Lakshya Dashboard provides a single operational view of trainee records and their seven-semester evaluation journey. It supports data entry, bulk onboarding, controlled evaluation progression, location-aware access, and management reporting.

## 2. Product goals

- Maintain one reliable record for each trainee and ticket number.
- Track training, on-the-job, and BITS performance per semester.
- Prevent edits to inactive students and completed semesters.
- Reduce manual entry through validated Excel imports.
- Give management actionable views by location, batch, branch, gender, and score range.
- Restrict location-scoped roles to their assigned plant data.

## 3. Users and roles

| Role | Primary needs |
| --- | --- |
| Admin | Full access to users, students, evaluations, and dashboards |
| PMO | Operational overview and student management across plants |
| SDC Coordinator | Manage students and evaluations for one assigned plant |
| HR Head | View dashboard data restricted to the assigned plant |
| Other authenticated user | View the user dashboard according to granted role |

## 4. Functional requirements

### Authentication and access

- Users can sign in and sign out.
- Successful login routes users to the appropriate dashboard.
- Protected pages require an authenticated session.
- Role and plant restrictions apply on the server, not only in the interface.
- State-changing requests require CSRF protection and logout uses POST.

### Student management

- Users can list and filter students by location, year, department, batch, function, BITS stream, and status.
- Authorized users can add, edit, and delete students.
- Full names may contain one or more parts.
- Plant locations are normalized to the established database format.
- End date is calculated as five years after date of joining, including leap-day handling.
- Active students whose end date has passed become completed.
- Creating an active student creates an ongoing Semester 1 evaluation.

### Evaluation management

- Evaluations store ten OJT scores, training marks, and BITS CGPA for each semester.
- Calculated training, OJT, BITS, and grand totals use the existing weighted formulas.
- Only an active student's ongoing semester can be edited.
- Semesters 1–6 can be completed and promoted to the next semester.
- Semester 7 can be ended without creating Semester 8.
- Historical completed semesters remain viewable.

### Bulk imports

- Student and evaluation data can be imported from `.xlsx` or `.xls` files.
- Column matching is case-, space-, and underscore-insensitive.
- Imports report inserted, skipped, and failed rows without hiding row-level errors.
- Evaluation score ranges are validated before persistence.
- Completing a semester through evaluation import creates the next ongoing semester when appropriate.

### Reporting

- Dashboard summary shows total trainees, gender counts, and batch counts.
- Reports support multi-value filtering where provided by the interface.
- Score-distribution charts use completed semesters only.
- Users can drill from a score bucket into matching trainee records.
- Location, batch, branch, performance, and attrition breakdowns honor active filters and role restrictions.

## 5. Non-functional requirements

- Preserve server-side authorization for restricted data.
- Use parameterized SQL for user-provided values.
- Keep credentials and secret keys outside source control.
- Support current desktop browsers with JavaScript enabled.
- Keep route, service, model, template, and static-asset responsibilities separated.
- Provide validation feedback that identifies the affected workbook row.

## 6. Success criteria

- Existing routes and workflows operate after structural changes.
- A coordinator cannot manage or view out-of-location student evaluation data through restricted endpoints.
- An evaluation can progress from Semester 1 through Semester 7 without duplicate semester records.
- Valid workbooks import successfully and invalid rows return actionable feedback.
- Dashboard totals and drill-down results reflect the same filters.

## 7. Out of scope for this refactor

- Changing score formulas, statuses, role definitions, or visual design
- Replacing MySQL or Flask
- Adding new business workflows
- Production deployment automation
- Redesigning the supplied Excel formats
