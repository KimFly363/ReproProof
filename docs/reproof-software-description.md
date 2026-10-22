# ReproProof 软件说明书

## 1. 软件名称

**ReproProof：论文复现审计**

## 2. 作品简介

ReproProof 是面向 AI 论文 Artifact 提交的自动化可复现性审计工具。它嵌入代码提交与投稿前检查流程，用静态分析识别随机种子缺失、依赖未锁定、硬编码数据路径、训练/测试数据泄漏、README 入口不一致，以及论文与代码在数据集和指标上的不一致。每次审计生成可追溯的 HTML、Markdown、JSON 和 PR 评论报告，并提供可量化的风险评分，帮助科研实验室减少复现失败和 Artifact 评审问题。

## 3. 产品定位

- 产品类型：AI 科研质量工具 / 开发者基础设施；
- 第一用户：准备向 AI 会议提交代码 Artifact 的科研实验室；
- 第二用户：会议 Artifact Evaluation 委员会、期刊可复现性编辑；
- 付费方：课题组、学院、会议和期刊；
- 核心场景：论文投稿、代码开源、实验交接和 Artifact 评审前。

## 4. 运行环境

- 操作系统：Windows、Linux、macOS；
- Python：3.9+；
- CLI：标准库 argparse；
- 静态分析：Python AST；
- 论文解析：内置 pypdf 6.10 / 可选 pip 安装；
- 报告：自包含 HTML + Markdown + JSON；
- CI：GitHub Actions composite action。

## 5. 安装与运行

源代码目录直接运行：

```powershell
python reproof.py audit . --out reproof-report
```

可编辑安装：

```powershell
python -m pip install -e .[paper]
reproof audit . --out reproof-report
```

Windows 一键入口：

```text
run_reproof.bat audit . --out reproof-report
```

## 6. 功能模块

### 6.1 CLI

```text
reproof audit <repo> [--paper paper.pdf] [--out report-dir] [--fail-on high]
```

支持返回非零退出码，可用于 CI Gate。

### 6.2 六条审计规则

| 编号 | 规则 | 技术方法 |
|---|---|---|
| R1 | 随机种子缺失 | AST 调用检测，多框架种子识别 |
| R2 | 依赖版本未锁定 | 多格式依赖清单解析 |
| R3 | 数据路径硬编码 | AST 字符串字面量 + 路径模式识别 |
| R4 | 训练/测试数据泄漏 | AST 调用顺序与变量关系分析 |
| R5 | README 入口不一致 | README 命令提取 + 文件存在性检查 |
| R6 | 论文-代码不一致 | 论文文本抽取 + 数据集/指标目录匹配 |

### 6.3 报告

- `report.html`：自包含可视化报告，可脱离网络打开；
- `report.md`：便于提交和版本管理；
- `report.json`：结构化结果，可供二次开发；
- `pr-comment.md`：可直接用于 GitHub PR 评论。

### 6.4 GitHub Action

`action.yml` 支持：

- 设置审计路径；
- 可选论文路径；
- 设置失败阈值；
- 输出报告目录。

## 7. 技术架构

```text
CLI
  -> 文件扫描器
  -> Python AST / 论文文本分析
  -> 6 条规则
  -> 问题模型
  -> 风险评分
  -> HTML / Markdown / JSON / PR 报告
```

核心输出对象：

```json
{
  "rule_id": "R4",
  "severity": "high",
  "file": "train.py",
  "line": 15,
  "message": "预处理在 train_test_split 之前对完整数据执行",
  "evidence": "scaler.fit_transform(X)",
  "suggestion": "先划分数据，再只在训练集上 fit"
}
```

## 8. 数据与安全

- 默认只做静态分析；
- 不执行用户代码；
- 论文 PDF 本地解析；
- 报告保存在本地目录；
- 不依赖云数据库；
- 内置 pypdf 以便离线解析 PDF。

## 9. 测试与效果

受控测试集包含 6 个仓库：

- demo-basic；
- demo-leak；
- demo-readme；
- demo-paper；
- demo-mixed；
- demo-clean。

结果：

- 11 个规则/仓库期望组合全部命中；
- 共识别 12 条问题；
- 干净仓库 0 误报；
- 11 个自动化测试通过；
- CLI 高优先级问题返回非零退出码；
- 打包后可在独立目录运行。

## 10. 已知边界

- 只支持 Python 仓库；
- 数据泄漏检测只覆盖常见调用顺序模式；
- 论文-代码一致性只检查有限的数据集和指标字段；
- 不执行完整训练；
- 报告结果需要人工确认；
- 评分是仓库风险指标，不代表会议或期刊的正式评审结果。
