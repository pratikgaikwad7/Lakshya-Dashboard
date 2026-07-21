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
                "lakshya-filter-inline",
                "lakshya-filter-control",
                "lakshya-filter-primary",
            ),
            "templates/partials/evaluations/sheet_header.html": (
                "lakshya-compact-filter",
                "lakshya-filter-control",
            ),
        }
        for relative_path, hooks in expected_hooks.items():
            contents = (project_root / relative_path).read_text()
            for hook in hooks:
                with self.subTest(template=relative_path, hook=hook):
                    self.assertIn(hook, contents)


if __name__ == "__main__":
    unittest.main()
