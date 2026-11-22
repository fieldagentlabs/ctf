"""Unit tests for fa_grader. Run: python3 -m unittest discover -s platform/grader/tests"""
import contextlib
import hashlib
import hmac
import io
import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fa_grader as fa  # noqa: E402

TEST_KEY = "unit-test-key-not-a-real-season-key"


class FakeShop(BaseHTTPRequestHandler):
    """Answers /api/Challenges/?key=... like Juice Shop does."""
    solved = {"scoreBoardChallenge": True, "loginAdminChallenge": False}

    def do_GET(self):
        from urllib.parse import parse_qs, urlparse
        url = urlparse(self.path)
        if url.path.rstrip("/") != "/api/Challenges":
            self.send_response(404)
            self.end_headers()
            return
        key = parse_qs(url.query).get("key", [""])[0]
        data = [{"key": key, "solved": self.solved[key]}] if key in self.solved else []
        body = json.dumps({"status": "success", "data": data}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class ShopTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), FakeShop)
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()


class TestFlags(unittest.TestCase):
    def test_mission_flag_matches_spec(self):
        expected = hmac.new(TEST_KEY.encode(), b"S1-K4", hashlib.sha256).hexdigest()[:12]
        with mock.patch.dict(os.environ, {"CTF_KEY": TEST_KEY}):
            self.assertEqual(fa.mission_flag("S1-K4"), f"FA{{s1_k4_{expected}}}")

    def test_mission_flag_suffixed_id(self):
        with mock.patch.dict(os.environ, {"CTF_KEY": TEST_KEY}):
            self.assertRegex(fa.mission_flag("S1-P4B"), r"^FA\{s1_p4b_[0-9a-f]{12}\}$")

    def test_flags_differ_by_mission_and_key(self):
        with mock.patch.dict(os.environ, {"CTF_KEY": TEST_KEY}):
            a, b = fa.mission_flag("S0-F2"), fa.mission_flag("S0-F3")
        with mock.patch.dict(os.environ, {"CTF_KEY": TEST_KEY + "x"}):
            c = fa.mission_flag("S0-F2")
        self.assertNotEqual(a, b)
        self.assertNotEqual(a, c)

    def test_missing_key_exits(self):
        with mock.patch.dict(os.environ, {}, clear=True), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit):
                fa.mission_flag("S0-F2")


class TestShop(ShopTestCase):
    def test_solved_and_unsolved(self):
        self.assertTrue(fa.juice_shop_solved("scoreBoardChallenge", self.url))
        self.assertFalse(fa.juice_shop_solved("loginAdminChallenge", self.url))

    def test_unknown_key_is_unsolved(self):
        self.assertFalse(fa.juice_shop_solved("noSuchChallenge", self.url))

    def test_shop_url_from_env(self):
        with mock.patch.dict(os.environ, {"SHOP_URL": self.url + "/"}):
            self.assertTrue(fa.juice_shop_solved("scoreBoardChallenge"))

    def test_unreachable_raises(self):
        with self.assertRaises(fa.ShopUnreachable):
            fa.juice_shop_solved("scoreBoardChallenge", "http://127.0.0.1:9")

    def test_check_solved_records_failure_instead_of_exiting(self):
        report = fa.Report("t")
        self.assertFalse(report.check_solved("scoreBoardChallenge", "solved", "hint", url="http://127.0.0.1:9"))
        report.check(True, "another check still runs")
        ok, label, hint = report.results[0]
        self.assertFalse(ok)
        self.assertIn("Can't reach Juice Shop", hint)
        self.assertEqual(len(report.results), 2)


class TestMarkdown(unittest.TestCase):
    def test_sections_basic(self):
        secs = fa.sections("# Title\n\n## Identity\nAgent\n\n## Scope ##\nlocalhost:3000\n")
        self.assertEqual(set(secs), {"identity", "scope"})
        self.assertIn("Agent", secs["identity"])

    def test_sections_ignores_h3_and_fenced_code(self):
        md = "## Real\nbody\n```\n## Fake\n```\n### Sub\nmore\n"
        secs = fa.sections(md)
        self.assertEqual(list(secs), ["real"])
        self.assertIn("### Sub", secs["real"])

    def test_find_section_whole_word(self):
        secs = {"permissions": "x\n", "output format": "y\n"}
        self.assertIsNone(fa.find_section(secs, ("mission",)))
        self.assertEqual(fa.find_section(secs, ("output",)), "y\n")

    def test_find_section_phrase(self):
        secs = {"rules of engagement": "r\n"}
        self.assertEqual(fa.find_section(secs, ("rules of engagement",)), "r\n")
        self.assertEqual(fa.find_section(secs, ("rules",)), "r\n")

    def test_bullets(self):
        text = "- one\n* two\n1. three\n2) four\n  - nested\nnot a bullet\n-nospace\n"
        self.assertEqual(len(fa.bullets(text)), 5)

    def test_find_secrets(self):
        self.assertTrue(fa.find_secrets("key: sk-ant-api03-abcdefghijklmnop"))
        self.assertTrue(fa.find_secrets("CTF_KEY=abc"))
        self.assertTrue(fa.find_secrets("ghp_" + "a" * 36))
        self.assertFalse(fa.find_secrets("Read keys from the ANTHROPIC_API_KEY environment variable."))


class TestReport(unittest.TestCase):
    def run_finish(self, *oks):
        report = fa.Report("Field Agents | test")
        for i, ok in enumerate(oks):
            report.check(ok, f"check {i}", f"hint {i}")
        out = io.StringIO()
        with mock.patch.dict(os.environ, {"CTF_KEY": TEST_KEY}), contextlib.redirect_stdout(out):
            code = report.finish("S0-F2", "Done.")
        return code, out.getvalue()

    def test_pass_prints_flag(self):
        code, out = self.run_finish(True, True)
        self.assertEqual(code, 0)
        self.assertIn("FA{s0_f2_", out)

    def test_fail_hides_flag_and_shows_hints(self):
        code, out = self.run_finish(True, False)
        self.assertEqual(code, 1)
        self.assertNotIn("FA{", out)
        self.assertIn("hint 1", out)
        self.assertNotIn("hint 0", out)

    def test_empty_report_does_not_pass(self):
        code, out = self.run_finish()
        self.assertEqual(code, 1)
        self.assertNotIn("FA{", out)


if __name__ == "__main__":
    unittest.main()
