import unittest
from unittest.mock import patch

from app import create_app
from config import TestingConfig
from exceptions import ForbiddenError
from models.evaluations.lifecycle import bulk_upsert_evaluations, promote_student_semester
from models.student_model import add_student
from models.user_model import (
    User,
    ensure_admin_user,
    reset_admin_password,
    update_user_credentials,
)
from services.student_service import update_existing_student


class CSRFTestingConfig(TestingConfig):
    WTF_CSRF_ENABLED = True


class BootstrapTestingConfig(TestingConfig):
    AUTO_CREATE_ADMIN = True
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "strong-test-password"


def user(role, plant_location=None, user_id=1):
    return User({
        "id": user_id,
        "username": role.lower().replace(" ", "_"),
        "role": role,
        "plant_location": plant_location,
    })


class AccessControlTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()

    def authenticated_request(self, authenticated_user, method, path, **kwargs):
        with self.client.session_transaction() as session:
            session["_user_id"] = str(authenticated_user.id)
            session["_fresh"] = True
        with patch("models.user_model.get_user_by_id", return_value=authenticated_user):
            return getattr(self.client, method)(path, **kwargs)

    def test_student_api_requires_authentication(self):
        response = self.client.get('/api/students')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()['code'], 'unauthorized')

    def test_non_management_role_cannot_read_student_api(self):
        response = self.authenticated_request(user('HR Head', 'Plant_A'), 'get', '/api/students')
        self.assertEqual(response.status_code, 403)

    def test_sdc_student_list_forces_assigned_plant(self):
        coordinator = user('SDC Coordinator', 'Plant_A')
        with patch('services.student_service.get_all_students', return_value=[]) as get_students:
            response = self.authenticated_request(
                coordinator, 'get', '/api/students?location=Plant_B&student_status=active'
            )
        self.assertEqual(response.status_code, 200)
        filters = get_students.call_args.args[0]
        self.assertEqual(filters['plant_location'], 'Plant_A')
        self.assertEqual(filters['student_status'], 'active')

    def test_sdc_without_plant_is_denied(self):
        response = self.authenticated_request(user('SDC Coordinator'), 'get', '/api/students')
        self.assertEqual(response.status_code, 403)

    def test_pmo_can_read_students_without_plant_override(self):
        with patch('services.student_service.get_all_students', return_value=[]) as get_students:
            response = self.authenticated_request(user('PMO'), 'get', '/api/students?location=Plant_B')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_students.call_args.args[0]['plant_location'], 'Plant_B')

    def test_sdc_cannot_update_student_from_another_plant(self):
        coordinator = user('SDC Coordinator', 'Plant_A')
        with patch('services.student_service.get_student_by_id', return_value={'plant_location': 'Plant_B'}), \
             patch('services.student_service.update_student') as update_student:
            with self.assertRaises(ForbiddenError):
                update_existing_student(7, {
                    'first_name': 'Trainee', 'ticket_no': 'T-7', 'gender': 'Male'
                }, coordinator)
        update_student.assert_not_called()

    def test_dashboard_api_ignores_requested_plant_for_sdc(self):
        coordinator = user('SDC Coordinator', 'Plant_A')
        with patch('routes.user_dashboard.get_performance_distribution', return_value=[]) as distribution:
            response = self.authenticated_request(
                coordinator,
                'post',
                '/get-performance-data',
                json={'plant_location': ['Plant_B'], 'student_status': ['active'], 'score_type': 'all'},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(distribution.call_args.args[0]['plant_location'], ['Plant_A'])

    def test_logout_is_post_only(self):
        self.assertEqual(self.client.get('/logout').status_code, 405)

    def test_admin_can_update_username_without_changing_password(self):
        administrator = user('Admin', user_id=12)
        with patch('routes.users.update_user_credentials') as update_credentials:
            response = self.authenticated_request(
                administrator,
                'post',
                '/users/update/7',
                data={
                    'username': 'updated_user',
                    'password': '',
                    'password_confirmation': '',
                },
            )
        self.assertEqual(response.status_code, 302)
        update_credentials.assert_called_once_with(7, 'updated_user', None)

    def test_user_update_rejects_password_confirmation_mismatch(self):
        administrator = user('Admin', user_id=12)
        with patch('routes.users.update_user_credentials') as update_credentials:
            response = self.authenticated_request(
                administrator,
                'post',
                '/users/update/7',
                data={
                    'username': 'updated_user',
                    'password': 'strong-password',
                    'password_confirmation': 'different-password',
                },
            )
        self.assertEqual(response.status_code, 400)
        update_credentials.assert_not_called()

    def test_non_admin_cannot_update_user_credentials(self):
        response = self.authenticated_request(
            user('PMO'),
            'post',
            '/users/update/7',
            data={
                'username': 'updated_user',
                'password': '',
                'password_confirmation': '',
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_cannot_delete_active_account(self):
        administrator = user('Admin', user_id=12)
        with patch('routes.users.delete_user') as delete_account:
            response = self.authenticated_request(
                administrator,
                'post',
                '/users/delete/12',
            )
        self.assertEqual(response.status_code, 400)
        delete_account.assert_not_called()

    def test_configured_admin_is_checked_only_once_per_app_process(self):
        app = create_app(BootstrapTestingConfig)
        client = app.test_client()
        with patch('models.user_model.ensure_admin_user', return_value=True) as ensure_admin:
            self.assertEqual(client.get('/login').status_code, 200)
            self.assertEqual(client.get('/login').status_code, 200)
        ensure_admin.assert_called_once_with('admin', 'strong-test-password')

class CSRFTests(unittest.TestCase):
    def test_mutating_request_without_csrf_token_is_rejected(self):
        app = create_app(CSRFTestingConfig)
        response = app.test_client().post('/login', data={'username': 'x', 'password': 'y'})
        self.assertEqual(response.status_code, 400)

    def test_login_form_contains_csrf_token(self):
        app = create_app(CSRFTestingConfig)
        response = app.test_client().get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="csrf_token"', response.data)

    def test_user_update_requires_csrf_token(self):
        app = create_app(CSRFTestingConfig)
        response = app.test_client().post(
            '/users/update/7',
            data={'username': 'updated_user'},
        )
        self.assertEqual(response.status_code, 400)


class FakeCursor:
    def __init__(self, fetch_results=None, fail_on_evaluation_insert=False):
        self.fetch_results = list(fetch_results or [])
        self.fail_on_evaluation_insert = fail_on_evaluation_insert
        self.queries = []
        self.params = []
        self.rowcount = 0
        self.lastrowid = 42

    def execute(self, query, params=None):
        normalized = ' '.join(query.split())
        self.queries.append(normalized)
        self.params.append(params)
        if self.fail_on_evaluation_insert and normalized.startswith('INSERT INTO student_evaluations'):
            raise RuntimeError('evaluation insert failed')
        self.rowcount = 1

    def executemany(self, query, values):
        self.queries.append(' '.join(query.split()))
        self.rowcount = len(values)

    def fetchone(self):
        return self.fetch_results.pop(0) if self.fetch_results else None


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.commits = 0
        self.rollbacks = 0
        self.closed = False

    def cursor(self, dictionary=False):
        return self._cursor

    def start_transaction(self):
        pass

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True


class DataIntegrityTests(unittest.TestCase):
    def test_password_update_stores_a_hash_and_commits_once(self):
        cursor = FakeCursor(fetch_results=[{'id': 7}])
        connection = FakeConnection(cursor)
        with patch('models.user_model.get_db_connection', return_value=connection):
            update_user_credentials(7, 'renamed_user', 'strong-password')
        username, password_hash, user_id = cursor.params[1]
        self.assertEqual(username, 'renamed_user')
        self.assertEqual(user_id, 7)
        self.assertNotEqual(password_hash, 'strong-password')
        from werkzeug.security import check_password_hash
        self.assertTrue(check_password_hash(password_hash, 'strong-password'))
        self.assertEqual(connection.commits, 1)
        self.assertEqual(connection.rollbacks, 0)

    def test_username_only_update_does_not_write_password(self):
        cursor = FakeCursor(fetch_results=[{'id': 7}])
        connection = FakeConnection(cursor)
        with patch('models.user_model.get_db_connection', return_value=connection):
            update_user_credentials(7, 'renamed_user')
        self.assertEqual(cursor.params[1], ('renamed_user', 7))
        self.assertNotIn('password', cursor.queries[1].lower())
        self.assertEqual(connection.commits, 1)

    def test_existing_admin_is_never_overwritten_by_bootstrap(self):
        cursor = FakeCursor(fetch_results=[{'id': 1, 'role': 'Admin'}])
        connection = FakeConnection(cursor)
        with patch('models.user_model.get_db_connection', return_value=connection):
            created = ensure_admin_user('admin', 'new-password')
        self.assertFalse(created)
        self.assertFalse(any(query.startswith('INSERT INTO users') for query in cursor.queries))
        self.assertEqual(connection.commits, 0)

    def test_bootstrap_rejects_existing_non_admin_username(self):
        cursor = FakeCursor(fetch_results=[{'id': 1, 'role': 'PMO'}])
        connection = FakeConnection(cursor)
        with patch('models.user_model.get_db_connection', return_value=connection):
            with self.assertRaisesRegex(ValueError, "is not an Admin"):
                ensure_admin_user('existing-user', 'new-password')
        self.assertEqual(connection.rollbacks, 1)
        self.assertEqual(connection.commits, 0)

    def test_existing_admin_password_can_be_reset_explicitly(self):
        cursor = FakeCursor(fetch_results=[{'id': 1, 'role': 'Admin'}])
        connection = FakeConnection(cursor)
        with patch('models.user_model.get_db_connection', return_value=connection):
            reset_admin_password('admin', 'new-strong-password')
        password_hash, user_id = cursor.params[1]
        self.assertEqual(user_id, 1)
        self.assertNotEqual(password_hash, 'new-strong-password')
        from werkzeug.security import check_password_hash
        self.assertTrue(check_password_hash(password_hash, 'new-strong-password'))
        self.assertEqual(connection.commits, 1)

    def test_student_and_initial_semester_rollback_together(self):
        cursor = FakeCursor(fail_on_evaluation_insert=True)
        connection = FakeConnection(cursor)
        payload = {
            'first_name': 'Trainee', 'middle_name': '', 'surname': '', 'ticket_no': 'T-1',
            'gender': 'Male', 'mobile_no': '', 'status': 'active',
        }
        with patch('models.students.repository.get_db_connection', return_value=connection):
            with self.assertRaises(RuntimeError):
                add_student(payload)
        self.assertEqual(connection.commits, 0)
        self.assertEqual(connection.rollbacks, 1)

    def test_promotion_locks_and_conditionally_completes_semester(self):
        cursor = FakeCursor(fetch_results=[{'status': 'active'}, {'id': 9, 'semester': 2}])
        connection = FakeConnection(cursor)
        with patch('models.evaluations.lifecycle.get_db_connection', return_value=connection):
            success, _ = promote_student_semester(4)
        self.assertTrue(success)
        self.assertTrue(any('FOR UPDATE' in query for query in cursor.queries))
        self.assertTrue(any("semester_status = 'ongoing'" in query and query.startswith('UPDATE') for query in cursor.queries))
        self.assertEqual(connection.commits, 1)

    def test_bulk_success_count_is_captured_before_follow_up_queries(self):
        cursor = FakeCursor(fetch_results=[{'id': 3}])
        connection = FakeConnection(cursor)
        records = [{
            'student_id': 1, 'semester': 1, 'semester_status': 'completed',
        }]
        with patch('models.evaluations.lifecycle.get_db_connection', return_value=connection):
            count = bulk_upsert_evaluations(records)
        self.assertEqual(count, 1)


if __name__ == '__main__':
    unittest.main()
