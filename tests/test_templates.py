import unittest
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


class TemplateTests(unittest.TestCase):
    def test_all_templates_and_partials_parse(self):
        template_root = Path(__file__).parents[1] / "templates"
        environment = Environment(loader=FileSystemLoader(template_root))

        for template in template_root.rglob("*.html"):
            with self.subTest(template=template):
                environment.parse(template.read_text())

    def test_dashboard_live_ui_assets_and_accessibility_hooks_are_present(self):
        project_root = Path(__file__).parents[1]
        dashboard_template = (project_root / "templates/user_dashboard.html").read_text()
        filter_partial = (
            project_root / "templates/partials/dashboard/filters.html"
        ).read_text()
        dashboard_css = (project_root / "static/css/user_dashboard.css").read_text()
        chart_animations = (
            project_root / "static/js/dashboard/chart-animations.js"
        ).read_text()

        for asset in (
            "animations.js",
            "loading-state.js",
            "chart-animations.js",
            "live-updates.js",
        ):
            self.assertIn(asset, dashboard_template)
            self.assertTrue((project_root / "static/js/dashboard" / asset).exists())

        self.assertIn('id="dashboardFilterForm"', filter_partial)
        self.assertIn('aria-hidden="true"', filter_partial)
        self.assertIn('prefers-reduced-motion: reduce', dashboard_css)
        self.assertIn('sidebar-backdrop', dashboard_css)
        self.assertIn('delay: reducedMotionQuery.matches ? 0 : 140', chart_animations)

    def test_filter_surfaces_use_the_shared_visual_system(self):
        project_root = Path(__file__).parents[1]
        shared_css = project_root / "static/css/filter-system.css"
        self.assertTrue(shared_css.exists())
        self.assertIn(".lakshya-filter-surface", shared_css.read_text())

        expected_hooks = {
            "templates/partials/evaluations/list_filters.html": (
                "lakshya-filter-surface",
                "lakshya-filter-control",
                "lakshya-filter-actions",
            ),
            "templates/students.html": (
                "students-filter-sidebar",
                "lakshya-filter-control",
                "lakshya-filter-secondary",
            ),
        }
        for relative_path, hooks in expected_hooks.items():
            contents = (project_root / relative_path).read_text()
            for hook in hooks:
                with self.subTest(template=relative_path, hook=hook):
                    self.assertIn(hook, contents)

    def test_evaluation_surfaces_link_directly_to_full_progress_profile(self):
        project_root = Path(__file__).parents[1]
        list_table = (
            project_root / "templates/partials/evaluations/list_table.html"
        ).read_text()
        list_template = (
            project_root / "templates/student_evaluation.html"
        ).read_text()
        profile_template = (
            project_root / "templates/student_progress_profile.html"
        ).read_text()
        sheet_template = (
            project_root / "templates/trainee_sheet.html"
        ).read_text()
        sheet_header = (
            project_root / "templates/partials/evaluations/sheet_header.html"
        ).read_text()
        sheet_journey = (
            project_root / "templates/partials/evaluations/sheet_semester_journey.html"
        ).read_text()
        sheet_script = (
            project_root / "static/js/evaluations/sheet.js"
        ).read_text()

        self.assertIn("student_progress_profile", list_table)
        self.assertNotIn("openStudentModal", list_table)
        self.assertNotIn("list_student_modal", list_template)
        self.assertIn('data-semester-target="semester-', profile_template)
        self.assertIn("data-semester-panel", profile_template)
        self.assertIn("ScrollTrigger.min.js", profile_template)
        self.assertIn("Trainee profile", profile_template)
        self.assertNotIn("Trainee intelligence profile", profile_template)
        self.assertNotIn("Performance telemetry", profile_template)
        self.assertIn('id="sheetScrollProgress"', sheet_template)
        self.assertIn("ScrollTrigger.min.js", sheet_template)
        self.assertIn("student-progress-profile.css", sheet_template)
        self.assertIn("sheet_semester_journey.html", sheet_template)
        self.assertIn("student_progress_profile", sheet_header)
        self.assertIn("Promote to Sem", sheet_header)
        self.assertIn("Evaluate", sheet_header)
        self.assertNotIn("<select", sheet_header)
        self.assertNotIn("Evaluation Sheet", sheet_header)
        self.assertNotIn("View:", sheet_header)
        self.assertIn("range(1, 8)", sheet_journey)
        self.assertIn("initSheetMotion", sheet_script)

    def test_enterprise_dialog_replaces_native_project_confirmations(self):
        project_root = Path(__file__).parents[1]
        dialog_css = (
            project_root / "static/css/components/enterprise-dialog.css"
        ).read_text()
        dialog_script = (
            project_root / "static/js/components/enterprise-dialog.js"
        ).read_text()
        sheet_header = (
            project_root / "templates/partials/evaluations/sheet_header.html"
        ).read_text()

        self.assertIn(".enterprise-dialog-panel", dialog_css)
        self.assertIn("window.LakshyaDialog", dialog_script)
        self.assertIn("data-enterprise-confirm", sheet_header)
        self.assertIn("Promote to Semester", sheet_header)
        self.assertNotIn("return confirm(", sheet_header)

        for relative_path in (
            "templates/trainee_sheet.html",
            "templates/users.html",
            "templates/students.html",
        ):
            contents = (project_root / relative_path).read_text()
            with self.subTest(template=relative_path):
                self.assertIn("enterprise-dialog.css", contents)
                self.assertIn("enterprise-dialog.js", contents)

        native_dialog_sources = (
            "static/js/evaluations/sheet.js",
            "static/js/pages/users.js",
            "static/js/students/form.js",
            "static/js/students/upload.js",
        )
        for relative_path in native_dialog_sources:
            contents = (project_root / relative_path).read_text()
            with self.subTest(source=relative_path):
                self.assertNotIn("window.confirm(", contents)
                self.assertNotIn("if (!confirm(", contents)
                self.assertNotIn(" alert(", contents)

    def test_admin_dashboard_uses_enterprise_saas_visual_system(self):
        project_root = Path(__file__).parents[1]
        template = (project_root / "templates/admin_dashboard.html").read_text()
        stylesheet = (
            project_root / "static/css/pages/admin-dashboard.css"
        ).read_text()
        script = (
            project_root / "static/js/pages/admin-dashboard.js"
        ).read_text()

        for hook in (
            "admin-hero__aurora",
            "admin-stat-grid",
            "admin-action-grid",
            "admin-dashboard.js",
        ):
            self.assertIn(hook, template)

        self.assertIn("admin-navy", stylesheet)
        self.assertIn("backdrop-filter", stylesheet)
        self.assertIn("prefers-reduced-motion: reduce", stylesheet)
        self.assertIn("window.gsap", script)

    def test_user_dashboard_student_entries_open_full_profiles(self):
        project_root = Path(__file__).parents[1]
        table = (
            project_root / "templates/partials/dashboard/content.html"
        ).read_text()
        chart = (
            project_root / "static/js/dashboard/evaluation-chart.js"
        ).read_text()

        self.assertIn("student_progress_profile", table)
        self.assertNotIn("openStudentModal", table)
        self.assertIn("dataset.profileUrl", chart)
        self.assertIn("/evaluations/${encodeURIComponent(student.id)}/profile", chart)
        self.assertNotIn("openStudentModal(studentData)", chart)

    def test_evaluations_list_uses_compact_enterprise_visual_system(self):
        project_root = Path(__file__).parents[1]
        template = (project_root / "templates/student_evaluation.html").read_text()
        header = (
            project_root / "templates/partials/evaluations/list_header.html"
        ).read_text()
        table = (
            project_root / "templates/partials/evaluations/list_table.html"
        ).read_text()
        stylesheet = (
            project_root / "static/css/pages/student-evaluation.css"
        ).read_text()
        script = (
            project_root / "static/js/evaluations/list.js"
        ).read_text()

        self.assertIn("evaluation-list-page", template)
        self.assertNotIn("gsap.min.js", template)
        self.assertIn("evaluation-list-header__aurora", header)
        self.assertIn("evaluation-data-grid", table)
        self.assertIn("min-height: 72px", stylesheet)
        self.assertIn("backdrop-filter", stylesheet)
        self.assertIn("prefers-reduced-motion: reduce", stylesheet)
        self.assertNotIn("window.gsap", script)
        self.assertIn("Sr. No.", table)
        self.assertIn("fetch(nextUrl", script)

    def test_evaluation_upload_explains_format_and_provides_template(self):
        project_root = Path(__file__).parents[1]
        template = (project_root / "templates/upload_evaluations.html").read_text()
        script = (project_root / "static/js/evaluations/upload.js").read_text()
        self.assertIn("download_evaluation_template", template)
        self.assertIn("Ticket No", template)
        self.assertIn("Score Attendance", template)
        self.assertIn('id="evaluationUploadButton"', template)
        self.assertIn("disabled", template)
        self.assertIn("10 * 1024 * 1024", script)
        self.assertTrue((project_root / "outputs/evaluation-upload-template/evaluation-upload-template.xlsx").exists())

    def test_students_page_matches_compact_enterprise_visual_system(self):
        project_root = Path(__file__).parents[1]
        template = (project_root / "templates/students.html").read_text()
        stylesheet = (
            project_root / "static/css/pages/students.css"
        ).read_text()
        script = (
            project_root / "static/js/students/list.js"
        ).read_text()
        evaluation_header = (
            project_root / "templates/partials/evaluations/list_header.html"
        ).read_text()

        self.assertNotIn("/admin-dashboard", template)
        self.assertNotIn("/admin-dashboard", evaluation_header)
        self.assertIn("students-header__aurora", template)
        self.assertIn("students-data-grid", template)
        self.assertIn("gsap.min.js", template)
        self.assertIn("backdrop-filter", stylesheet)
        self.assertIn("prefers-reduced-motion: reduce", stylesheet)
        self.assertIn("initStudentsMotion", script)

    def test_user_dashboard_uses_saas_visual_override_without_structure_changes(self):
        project_root = Path(__file__).parents[1]
        template = (project_root / "templates/user_dashboard.html").read_text()
        content = (
            project_root / "templates/partials/dashboard/content.html"
        ).read_text()
        stylesheet = (
            project_root / "static/css/pages/user-dashboard.css"
        ).read_text()

        self.assertIn("partials/dashboard/content.html", template)
        self.assertIn("Gender Diversity", content)
        self.assertIn("Diploma Branch Wise", content)
        self.assertIn("Evaluation Score Distribution", content)
        self.assertIn("--user-dashboard-navy", stylesheet)
        self.assertIn("dashboardAuroraDrift", stylesheet)
        self.assertIn("backdrop-filter", stylesheet)
        self.assertIn("#studentTableContainer", stylesheet)
        self.assertIn("dashboard-kpi-card--students", content)
        self.assertIn("dashboard-kpi-card--attrition", content)
        self.assertIn("dashboard-kpi-card--batches", content)
        self.assertIn("dashboard-kpi-card--branches", content)
        self.assertIn(".dashboard-kpi-card--branches", stylesheet)


if __name__ == "__main__":
    unittest.main()
