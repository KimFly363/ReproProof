# ReproProof

> 面向 AI 论文 Artifact 提交的自动化可复现性审计工具。

ReproProof 检查 AI/ML 代码仓库中常见的可复现性问题，并生成 HTML、Markdown、JSON 和 PR 评论报告。

## 快速开始

```powershell
cd C:\Users\fengjinfeng\Documents\ChatGPT\ThesisAssistant
python -m pip install -e .[paper]
reproof audit examples/demo-paper --paper examples/demo-paper/paper.pdf --out reproof-report
```

启动后查看：

```text
reproof-report/report.html
```

## 核心能力

- R1 随机种子缺失；
- R2 依赖版本未锁定；
- R3 数据路径硬编码；
- R4 常见训练/测试数据泄漏；
- R5 README 入口与仓库不一致；
- R6 论文-代码数据集/指标有限一致性检查。

## 产品形态

- Python CLI；
- GitHub Action；
- 自包含 HTML/Markdown 报告；
- PR 评论文本。

## 目录

```text
reproof/         核心审计引擎与规则
examples/        5 个带缺陷的演示仓库
tests/           规则和集成测试
action.yml       GitHub Action
REPROPROOF_README.md  详细使用说明
docs/            产品、评审和参赛材料
```

## 与旧 PaperProof 原型的关系

`prototype/`、`software/` 和 `desktop/` 是上一阶段的论文引证工具原型，保留作为历史材料。当前比赛方向以 ReproProof 为准。

详细说明见 `REPROPROOF_README.md`。

## 测试

```powershell
python -m unittest discover -s tests -v
```
