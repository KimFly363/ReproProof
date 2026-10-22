"""Rule 1: detect missing random seed setup."""
from __future__ import annotations

from reproof.analyzers.ast_analyzer import iter_calls, parse_python
from reproof.analyzers.file_scanner import Repository
from reproof.models import Issue
from reproof.rules.base import Rule


SEED_CALLS = {
    "random.seed",
    "np.random.seed",
    "numpy.random.seed",
    "torch.manual_seed",
    "torch.cuda.manual_seed",
    "torch.cuda.manual_seed_all",
    "tf.random.set_seed",
    "tensorflow.random.set_seed",
}
TRAINING_HINTS = (
    "optimizer.step", "loss.backward", "model.train", ".fit(", "dataloader",
    "cross_entropy", "train_loader", "training_step", "num_epochs", "epochs",
)


class SeedCheckRule(Rule):
    rule_id = "R1"
    title = "随机种子缺失"
    category = "environment"
    severity = "high"

    def run(self, repo: Repository, paper_text: str = "") -> list[Issue]:
        parsed = [(file, parse_python(file.text, file.relative_path)) for file in repo.python_files]
        seed_found = False
        for _, tree in parsed:
            if tree is None:
                continue
            for call in iter_calls(tree):
                if call.name in SEED_CALLS:
                    seed_found = True
                    break
            if seed_found:
                break
        if seed_found:
            return []

        training_files = []
        for file, tree in parsed:
            if tree is None:
                continue
            call_names = {call.name.lower() for call in iter_calls(tree)}
            haystack = file.text.lower()
            if call_names & {"model.fit", "optimizer.step", "loss.backward"} or any(hint in haystack for hint in TRAINING_HINTS):
                training_files.append(file)
        if not training_files:
            return []

        file = training_files[0]
        lines = file.text.splitlines()
        evidence_hints = ('optimizer.step', 'loss.backward', 'model.train', 'model.fit', 'for epoch', 'num_epochs')
        line_no = next(
            (index for index, line in enumerate(lines, start=1) if any(hint in line.lower() for hint in evidence_hints)),
            None,
        )
        evidence = lines[line_no - 1].strip() if line_no else ""
        return [
            Issue(
                rule_id=self.rule_id,
                title=self.title,
                severity=self.severity,
                category=self.category,
                file=file.relative_path,
                line=line_no,
                message="训练代码中未检测到 random / NumPy / PyTorch / TensorFlow 的随机种子设置，实验结果可能无法复现。",
                evidence=evidence,
                suggestion="在训练入口设置 random.seed(42)、np.random.seed(42)、torch.manual_seed(42)，并按需启用 CUDA 确定性模式。",
                confidence=0.92,
            )
        ]
