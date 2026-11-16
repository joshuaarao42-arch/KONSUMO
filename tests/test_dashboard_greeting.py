import unittest

from konsumo.web.views import dashboard_page


class DashboardGreetingTests(unittest.TestCase):
    def test_dashboard_greeting_uses_authenticated_username(self):
        html = dashboard_page([], {}, 0, "PHP", "test", "josh_user")
        self.assertIn("Good to see you, josh_user", html)

    def test_dashboard_greeting_has_fallback_without_username(self):
        html = dashboard_page([], {}, 0, "PHP", "test")
        self.assertIn("Good to see you, there", html)


if __name__ == "__main__":
    unittest.main()
