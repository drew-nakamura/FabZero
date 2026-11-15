"""Public demo must keep browser use separate from the local board runner."""
import io
import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import server


class PublicDemoTests(unittest.TestCase):
    def post(self, path, origin="https://siliconos-demo.onrender.com"):
        handler = object.__new__(server.Handler)
        handler.path = path
        handler.server = SimpleNamespace(server_port=8000)
        handler.headers = {"Origin": origin, "Content-Length": "2"}
        handler.rfile = io.BytesIO(b"{}")
        replies = []
        handler.reply = lambda status, body: replies.append((status, body))
        with patch.object(server, "PUBLIC_DEMO", True), patch.dict(os.environ, {"RENDER_EXTERNAL_URL": "https://siliconos-demo.onrender.com"}):
            handler.do_POST()
        return replies[0]

    def test_public_origin_is_accepted_but_other_origins_are_rejected(self):
        status, body = self.post("/api/explore")
        self.assertEqual(status, 400)  # Accepted origin; missing spec reaches validation.
        self.assertNotIn("Cross-origin", body["error"])
        status, body = self.post("/api/explore", "https://unrelated.example")
        self.assertEqual(status, 403)
        self.assertIn("Cross-origin", body["error"])

    def test_public_mode_never_starts_board_or_collects_contacts(self):
        for path in ("/api/board/check", "/api/runs/00000000-0000-0000-0000-000000000000/board-run",
                     "/api/runs/00000000-0000-0000-0000-000000000000/board-result",
                     "/api/pilot", "/api/generate-rtl", "/api/spec"):
            with self.subTest(path=path):
                status, body = self.post(path)
                self.assertEqual(status, 403)
                self.assertIn("public simulation", body["error"])

    def test_status_reports_board_unavailable_without_local_check(self):
        handler = object.__new__(server.Handler)
        handler.path = "/api/status"
        replies = []
        handler.reply = lambda status, body: replies.append((status, body))
        with patch.object(server, "PUBLIC_DEMO", True), patch("server.board.board_status") as board_status:
            handler.do_GET()
        board_status.assert_not_called()
        status, body = replies[0]
        self.assertEqual(status, 200)
        self.assertTrue(body["public_demo"])
        self.assertFalse(body["board"])
        self.assertFalse(body["ai"])
        self.assertIn("Windows JTAG runner", body["board_details"]["reason"])


if __name__ == "__main__":
    unittest.main()
