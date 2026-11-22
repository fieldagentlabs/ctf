"""Unit tests for the control CLI. Run: python3 -m unittest discover -s platform/control/tests"""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import control  # noqa: E402

GRADER = "import sys\nprint('args', sys.argv[1:])\nsys.exit(7)\n"


class TestControl(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for folder in ("s0-the-farm/missions/f2-wake-up-call", "s1-juice-shop/missions/k4-patch-the-shop"):
            verify_dir = self.root / "seasons" / folder / "verify"
            verify_dir.mkdir(parents=True)
            (verify_dir / "grade.py").write_text(GRADER)
        (self.root / "seasons/s0-the-farm/missions/f1-first-contact").mkdir(parents=True)  # no grader

    def tearDown(self):
        self.tmp.cleanup()

    def test_lists_only_missions_with_graders(self):
        self.assertEqual(sorted(control.missions(self.root)), ["f2", "k4"])

    def test_resolve_accepts_short_and_full_ids(self):
        for name in ("f2", "F2", " f2 ", "S0-F2", "s0-f2"):
            self.assertEqual(control.resolve(name, self.root).parents[1].name, "f2-wake-up-call", name)

    def test_resolve_unknown(self):
        self.assertIsNone(control.resolve("f1", self.root))
        self.assertIsNone(control.resolve("zz", self.root))

    def test_verify_runs_grader_with_args_and_returns_its_code(self):
        self.assertEqual(control.verify("k4", ["--x", "y"], self.root), 7)

    def test_verify_unknown_mission(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(control.verify("f1", [], self.root), 2)
        self.assertIn("f2, k4", err.getvalue())

    def test_real_repo_has_f2(self):
        self.assertIsNotNone(control.resolve("f2"))


if __name__ == "__main__":
    unittest.main()
