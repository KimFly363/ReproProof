# ReproProof 技术方案（初稿）

## 一、产品概述与定位

### 1.1 背景与目标

AI/ML 论文越来越依赖公开代码和实验 Artifact。随机种子缺失、依赖未锁定、数据路径写死、训练/测试数据泄漏、运行命令失效，以及论文与代码在数据集和指标上的不一致，都会导致 Artifact 评审失败或后续复现困难。

ReproProof 的目标是把可复现性检查从人工、一次性的投稿前检查，变为嵌入代码提交过程的自动质量 Gate。

### 1.2 产品定位

- 产品类型：AI 科研质量工具 / 研发基础设施；
- 第一用户：准备提交 AI 论文代码 Artifact 的科研实验室；
- 第二用户：会议 Artifact Evaluation 委员会、期刊可复现性编辑；
- 产品形态：Python CLI + GitHub Action + HTML/Markdown/JSON 报告；
- 核心动作：`reproof audit . --paper paper.pdf`；
- 核心价值：在提交前自动发现可复现性风险，并给出文件、行号、证据和修复建议。

### 1.3 产品不是什么

- 不是论文写作助手；
- 不是通用代码审查工具；
- 不是实验管理平台；
- 不是查重或 AIGC 检测工具；
- 不替代人工 Artifact Evaluation。

## 二、技术架构与创新

### 2.1 整体架构

```text
CLI / GitHub Action
        |
        v
Repository Scanner
        |
        +--> Python AST Analyzer
        +--> Dependency Parser
        +--> README Parser
        +--> Paper Text Loader
        |
        v
Six Audit Rules
        |
        v
Issue Model + Risk Scoring
        |
        +--> report.html
        +--> report.md
        +--> report.json
        +--> pr-comment.md
```

### 2.2 技术选型

| 模块 | 技术 |
|---|---|
| CLI | Python argparse |
| 静态分析 | Python AST |
| 依赖解析 | requirements.txt / pyproject / lock 文件 |
| 论文解析 | 内置 pypdf + TXT/MD 回退 |
| 报告 | 自包含 HTML、Markdown、JSON |
| CI | GitHub Actions composite action |
| 测试 | unittest |

### 2.3 六条规则

1. 随机种子缺失：AST 检测 random、NumPy、PyTorch、TensorFlow 种子设置；
2. 依赖版本未锁定：解析依赖清单与锁文件，识别未固定版本；
3. 数据路径硬编码：检测 Windows、Unix、网络绝对路径字符串；
4. 训练/测试数据泄漏：追踪 scaler/feature selector 的 fit 与 train_test_split 的调用顺序和变量关系；
5. README 入口不一致：提取运行命令并验证脚本存在；
6. 论文-代码一致性：从论文和代码中提取数据集、指标，生成有证据的对照结果。

### 2.4 核心创新

#### 创新一：跨文档与代码的一致性审计

将论文声明、代码配置和实验结果映射到同一张审计表。首版只检查有明确证据的数据集和指标，不做主观语义推断。

#### 创新二：数据泄漏的调用顺序分析

不是搜索关键词“scaler”，而是判断预处理 fit 是否发生在 train_test_split 之前，以及后续是否对完整数据 fit。

#### 创新三：嵌入提交链路的 CI Gate

CLI 支持 `--fail-on high`，GitHub Action 可直接在 PR 中运行并返回失败状态。与一次性手动审计相比，它覆盖每次修改。

#### 创新四：可解释报告

每条问题包含规则编号、严重程度、文件、行号、证据、置信度和修复建议，避免黑盒结论。

## 三、功能设计与实现

### 3.1 输入

```text
reproof audit <repository> [--paper paper.pdf]
```

### 3.2 输出

```text
reproof-report/
  report.html
  report.md
  report.json
  pr-comment.md
```

### 3.3 评分

评分不是会议录用预测，而是仓库内部风险指标。高优先级问题会显著降低分数，并触发 CLI 非零退出码。

### 3.4 安全设计

- 默认只读文件、不执行用户代码；
- 论文本地解析；
- 不上传代码；
- 对规则异常进行捕获，不中断全部审计；
- 报告中明确说明结果需要人工确认。

## 四、开发测试与部署

### 4.1 开发流程

- 构建文件扫描器和数据模型；
- 实现六条规则；
- 统一 Issue JSON 输出；
- 实现风险评分；
- 实现 HTML/Markdown/JSON/PR 报告；
- 实现 CLI 与 GitHub Action；
- 使用演示仓库和自动化测试验证。

### 4.2 测试集

6 个受控仓库：

- demo-basic；
- demo-leak；
- demo-readme；
- demo-paper；
- demo-mixed；
- demo-clean。

### 4.3 测试结果

- 11 个规则/仓库期望组合全部命中；
- 共识别 12 条问题；
- 干净仓库 0 误报；
- 11 个自动化测试通过；
- 独立 ZIP 包可运行；
- 内置 pypdf 可离线解析 PDF。

### 4.4 部署

- 本地运行：`python reproof.py audit .`
- Python 安装：`pip install -e .[paper]`
- GitHub Actions：使用根目录 `action.yml`
- 离线提交包：`dist/ReproProof-v0.1.0.zip`

## 五、应用价值与展望

### 5.1 应用场景

- 论文投稿前检查代码仓库；
- 开源论文代码前做质量 Gate；
- 会议 Artifact Evaluation 预检；
- 实验室代码交接；
- 课程和研究项目复现检查。

### 5.2 量化价值

- 自动发现缺失的种子、依赖和数据路径；
- 在提交前定位常见数据泄漏；
- 降低 Artifact 评审中的可复现性问题；
- 将一次人工检查转化为每次提交自动运行。

### 5.3 未来规划

- 增加更多泄漏模式和跨文件数据流；
- 支持更多 ML 框架；
- 增加 Docker 沙箱和 smoke test；
- 开发完整 GitHub App；
- 与 MLflow、DVC、W&B 集成；
- 建立公开可复现性测试集和评分标准。

## 六、附录

### 6.1 核心文件

- `reproof/auditor.py`：审计编排；
- `reproof/rules/`：六条规则；
- `reproof/analyzers/`：文件、AST、论文解析；
- `reproof/reporters/`：报告生成；
- `action.yml`：GitHub Action；
- `examples/`：测试和演示仓库；
- `tests/`：自动化测试。

### 6.2 说明

本方案中的测试结果是内部受控测试，不等同于真实论文仓库上的通用准确率。正式参赛材料应补充真实公开仓库测试和人工误报确认。
