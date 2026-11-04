"""PATCH 3 - in tests/test_konsumo.py:
  (a) add `import threading` at the top of the file;
  (b) in TestCRUD.test_validation, DELETE the third `with self.assertRaises(...)` block
      (the add_record("electricity", "2026-01-01", 1, ...) call is valid and would fail).
      Keep the gas, not-a-date and amount=0 cases;
  (c) replace the Flask-based TestWebApp class with the class below.
It relies on names already defined in that test file: DB, seed, list_records, get_record.
"""


class TestWebApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.path.exists(DB):
            os.remove(DB)
        seed(DB, days=120, verbose=False)
        from konsumo.web.app import create_server
        cls.server = create_server(DB, "127.0.0.1", 0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def req(self, method, path, body=None, headers=None):
        import http.client
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=15)
        conn.request(method, path, body=body, headers=headers or {})
        r = conn.getresponse()
        data, location = r.read(), r.getheader("Location")
        status = r.status
        conn.close()
        return status, data, location

    def test_dashboard(self):
        status, data, _ = self.req("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"Dashboard", data)

    def test_records_page(self):
        self.assertEqual(self.req("GET", "/records")[0], 200)

    def test_add_edit_delete_via_http(self):
        from urllib.parse import urlencode
        form = {"resource": "electricity", "recorded_at": "2026-10-10T10:00",
                "amount": "7.5", "cost": "", "notes": "http test"}
        status, _, loc = self.req("POST", "/records/new",
                                  urlencode(form),
                                  {"Content-Type": "application/x-www-form-urlencoded"})
        self.assertEqual(status, 302)
        self.assertEqual(loc, "/records")
        rid = list_records(db_path=DB)[0]["id"]
        form["amount"] = "8.0"
        form["notes"] = "edited"
        self.assertEqual(self.req("POST", f"/records/{rid}/edit", urlencode(form),
                                  {"Content-Type": "application/x-www-form-urlencoded"})[0], 302)
        self.assertEqual(get_record(rid, db_path=DB)["amount"], 8.0)
        self.assertEqual(self.req("POST", f"/records/{rid}/delete")[0], 302)
        self.assertIsNone(get_record(rid, db_path=DB))

    def test_bad_input_returns_400(self):
        from urllib.parse import urlencode
        form = {"resource": "electricity", "recorded_at": "2026-10-10T10:00",
                "amount": "-3", "cost": "", "notes": ""}
        self.assertEqual(self.req("POST", "/records/new", urlencode(form),
                                  {"Content-Type": "application/x-www-form-urlencoded"})[0], 400)

    def test_api_endpoints(self):
        import json as _json
        for url in ("/api/daily/electricity", "/api/monthly/water",
                    "/api/forecast/electricity", "/api/stats/water"):
            self.assertEqual(self.req("GET", url)[0], 200, url)
        status, data, _ = self.req("POST", "/api/quote",
                                   _json.dumps({"resource": "water", "amount": 5}),
                                   {"Content-Type": "application/json"})
        self.assertEqual(status, 200)
        self.assertIn("cost", _json.loads(data))
        self.assertEqual(self.req("POST", "/api/quote",
                                  _json.dumps({"resource": "water", "amount": -1}),
                                  {"Content-Type": "application/json"})[0], 400)

    def test_anomalies_and_recommendations_pages(self):
        for url in ("/anomalies", "/recommendations", "/forecast", "/analytics"):
            self.assertEqual(self.req("GET", url)[0], 200, url)
