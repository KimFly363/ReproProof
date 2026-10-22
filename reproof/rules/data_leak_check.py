"""Rule 4: detect common train/test leakage patterns."""
from __future__ import annotations

import re

from reproof.analyzers.ast_analyzer import expr_names, iter_calls, parse_python
from reproof.analyzers.file_scanner import Repository
from reproof.models import Issue
from reproof.rules.base import Rule


PREPROCESSOR_RE = re.compile(
    r"(scaler|normalizer|minmax|standard|robust|pca|selectk|selectpercentile|imputer|vectorizer|tfidf)",
    re.IGNORECASE,
)
SPLIT_NAME = "train_test_split"


class DataLeakageRule(Rule):
    rule_id = "R4"
    title = "训练/测试数据泄漏"
    category = "leakage"
    severity = "high"

    def run(self, repo: Repository, paper_text: str = "") -> list[Issue]:
        issues: list[Issue] = []
        for file in repo.python_files:
            tree = parse_python(file.text, file.relative_path)
            if tree is None:
                continue
            calls = list(iter_calls(tree))
            splits = [call for call in calls if call.name.endswith(SPLIT_NAME)]
            if not splits:
                continue
            for split in splits:
                split_inputs = set()
                for arg in split.node.args:
                    split_inputs |= expr_names(arg)
                if not split_inputs:
                    continue
                pattern = self._find_pattern(calls, split, split_inputs)
                if pattern is None:
                    continue
                message, preprocess_call, reason = pattern
                lines = file.text.splitlines()
                evidence = lines[preprocess_call.line - 1].strip() if preprocess_call.line <= len(lines) else ""
                split_evidence = lines[split.line - 1].strip() if split.line <= len(lines) else ""
                issues.append(
                    Issue(
                        rule_id=self.rule_id,
                        title=self.title,
                        severity=self.severity,
                        category=self.category,
                        file=file.relative_path,
                        line=preprocess_call.line,
                        message=message,
                        evidence=f"{evidence}  |  {split_evidence}",
                        suggestion="先执行 train_test_split，再仅在训练集上 fit 预处理/特征选择器，测试集只调用 transform。",
                        confidence=0.88,
                        metadata={"reason": reason, "split_line": split.line},
                    )
                )
                break
            if issues:
                break
        return issues

    def _find_pattern(self, calls, split, split_inputs):
        preprocess_calls = []
        for call in calls:
            short = call.name.split(".")[-1]
            if short not in {"fit", "fit_transform"}:
                continue
            base = call.name.rsplit(".", 1)[0]
            if not PREPROCESSOR_RE.search(base):
                continue
            inputs = set()
            if call.node.args:
                inputs |= expr_names(call.node.args[0])
            preprocess_calls.append((call, inputs))

        for preprocess, inputs in preprocess_calls:
            used = set(inputs)
            if preprocess.assigned_to:
                used |= {name.strip() for name in preprocess.assigned_to.split(",") if name.strip()}
            if preprocess.line < split.line and used & split_inputs:
                return (
                    "预处理或特征选择在 train_test_split 之前对完整数据执行，测试集信息可能泄漏到训练过程。",
                    preprocess,
                    "preprocess_before_split",
                )

        if split.node.args:
            whole_data_names = expr_names(split.node.args[0])
            for preprocess, inputs in preprocess_calls:
                if preprocess.line > split.line and inputs & whole_data_names:
                    if not any(name.endswith("_train") or name == "train" for name in inputs):
                        return (
                            "train_test_split 之后仍对完整数据执行预处理 fit，测试集信息可能参与训练。",
                            preprocess,
                            "fit_on_full_data_after_split",
                        )
        return None
