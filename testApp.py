import unittest
import sqlite3
from app import app

class URLShortenerTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

        self.db_path = "test_database.db"
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("DROP TABLE IF EXISTS urls")
        self.conn.execute("""
            CREATE TABLE urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_code TEXT UNIQUE NOT NULL
            )
        """)
        self.conn.commit()

        # ✅ Test sırasında Flask uygulamasına bu veritabanını kullandır
        def test_get_db_connection():
            return sqlite3.connect(self.db_path)
        app.get_db_connection = test_get_db_connection

    def tearDown(self):
        self.conn.close()
        import os
        os.remove(self.db_path)

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("URL Kısaltıcı API", response.get_data(as_text=True))

    def test_shorten_url(self):
        data = {"url": "https://www.google.com"}
        response = self.client.post("/shorten", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("short_url", response.get_json())

    def test_missing_url_field(self):
        response = self.client.post("/shorten", json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_redirect_existing_short_code(self):
        original_url = "https://example.com"
        short_code = "test123"

        self.conn.execute("INSERT INTO urls (original_url, short_code) VALUES (?, ?)", (original_url, short_code))
        self.conn.commit()

        response = self.client.get(f"/{short_code}")
        self.assertEqual(response.status_code, 302)
        self.assertIn(original_url, response.location)

    def test_redirect_nonexistent_code(self):
        response = self.client.get("/nonexistent")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
