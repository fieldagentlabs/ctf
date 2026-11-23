"""Tests for fa_api's stdlib parts (no network, no SDK needed)."""
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fa_api  # noqa: E402


class FaApiTest(unittest.TestCase):
    def test_model_default_and_override(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(fa_api.model(), "claude-haiku-5-5")
        with mock.patch.dict(os.environ, {"FA_MODEL": "some-other-model"}):
            self.assertEqual(fa_api.model(), "some-other-model")

    def test_missing_key(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(fa_api.ApiKeyMissing):
                fa_api.client()

    def test_usage_cost(self):
        u = fa_api.Usage("claude-haiku-5-5")
        u.add(SimpleNamespace(input_tokens=1_000_000, output_tokens=1_000_000,
                              cache_read_input_tokens=1_000_000, cache_creation_input_tokens=None))
        self.assertAlmostEqual(u.cost(), 0.61)
        self.assertAlmostEqual(u.cost(batch=True), 0.305)
        self.assertIsNone(fa_api.Usage("unknown-model").cost())
        self.assertIsNotNone(fa_api.Usage("claude-haiku-5-5-20261101").cost())
        self.assertIn("1 calls", u.summary())


if __name__ == "__main__":
    unittest.main()
