from __future__ import annotations

import json
import unittest
from pathlib import Path

from reproof.analyzers.file_scanner import Repository
from reproof.analyzers.paper_parser import load_paper_text
from reproof.auditor import AuditOptions, audit_repository
from reproof.rules.data_leak_check import DataLeakageRule
from reproof.rules.dependency_check import DependencyCheckRule
from reproof.rules.hardcode_path_check import HardcodedPathRule
from reproof.rules.paper_consistency import PaperConsistencyRule
from reproof.rules.readme_entry_check import ReadmeEntryRule
from reproof.rules.seed_check import SeedCheckRule


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


class RuleTests(unittest.TestCase):
    def test_seed_rule(self):
        repo = Repository(EXAMPLES / "demo-basic")
        issues = SeedCheckRule().run(repo)
        self.assertEqual([issue.rule_id for issue in issues], ["R1"])

    def test_dependency_rule(self):
        repo = Repository(EXAMPLES / "demo-basic")
        issues = DependencyCheckRule().run(repo)
        self.assertEqual([issue.rule_id for issue in issues], ["R2"])

    def test_hardcoded_path_rule(self):
        repo = Repository(EXAMPLES / "demo-basic")
        issues = HardcodedPathRule().run(repo)
        self.assertEqual([issue.rule_id for issue in issues], ["R3"])

    def test_data_leak_rule(self):
        repo = Repository(EXAMPLES / "demo-leak")
        issues = DataLeakageRule().run(repo)
        self.assertEqual([issue.rule_id for issue in issues], ["R4"])

    def test_readme_entry_rule(self):
        repo = Repository(EXAMPLES / "demo-readme")
        issues = ReadmeEntryRule().run(repo)
        self.assertGreaterEqual(len(issues), 1)
        self.assertTrue(all(issue.rule_id == "R5" for issue in issues))

    def test_paper_consistency_rule(self):
        repo = Repository(EXAMPLES / "demo-paper")
        paper = load_paper_text(EXAMPLES / "demo-paper" / "paper.txt")
        issues = PaperConsistencyRule().run(repo, paper)
        self.assertGreaterEqual(len(issues), 2)
        messages = " ".join(issue.message for issue in issues)
        self.assertIn("CIFAR", messages)
        self.assertIn("F1", messages)

    def test_clean_repository_has_no_issues(self):
        result = audit_repository(EXAMPLES / "demo-clean", AuditOptions(fail_on="none"))
        self.assertEqual(result.issues, [])
        self.assertEqual(result.score, 100.0)

    def test_mixed_repository_has_multiple_rules(self):
        result = audit_repository(EXAMPLES / "demo-mixed", AuditOptions(fail_on="none"))
        rule_ids = {issue.rule_id for issue in result.issues}
        self.assertTrue({"R1", "R2", "R3", "R4", "R5"}.issubset(rule_ids))
        self.assertLess(result.score, 50)

    def test_integration_result_is_serializable(self):
        result = audit_repository(
            EXAMPLES / "demo-paper",
            AuditOptions(paper_path=str(EXAMPLES / "demo-paper" / "paper.txt")),
        )
        payload = json.dumps(result.to_dict(), ensure_ascii=False)
        self.assertIn("R6", payload)
        self.assertIn("summary", payload)


if __name__ == "__main__":
    unittest.main()
