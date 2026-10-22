from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from reproof.cli import main


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_cli_fails_on_high_issue(self):
        with tempfile.TemporaryDirectory() as temp:
            code = main([
                "audit", str(ROOT / "examples" / "demo-leak"),
                "--out", temp, "--fail-on", "high", "--quiet"
            ])
            self.assertEqual(code, 1)
            report = Path(temp) / "report.html"
            self.assertTrue(report.exists())
            self.assertIn("ReproProof", report.read_text(encoding="utf-8"))

    def test_cli_passes_clean_repository(self):
        with tempfile.TemporaryDirectory() as temp:
            code = main([
                "audit", str(ROOT / "examples" / "demo-clean"),
                "--out", temp, "--fail-on", "high", "--quiet"
            ])
            self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
