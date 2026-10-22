# ReproProof

> 面向 AI 论文 Artifact 提交的自动化可复现性审计工具。

ReproProof 在论文代码提交前检查常见的可复现性风险：

- 随机种子缺失；
- 依赖版本未锁定；
- 数据路径硬编码；
- 常见训练/测试数据泄漏；
- README 运行命令与仓库不一致；
- 论文声明的数据集/指标与代码不一致。

它不是论文写作助手，也不是通用代码审查工具，而是面向 AI/ML 论文 Artifact 提交的自动化质量 Gate。

## 安装

```powershell
cd C:\Users\fengjinfeng\Documents\ChatGPT\ThesisAssistant
python -m pip install -e .[paper]
```

如果只审计代码、不需要读取 PDF 论文，可以只安装核心包：

```powershell
python -m pip install -e .
```

## 使用

审计本地仓库：

```powershell
reproof audit . --out reproof-report
```

同时比对论文：

```powershell
reproof audit examples/demo-paper --paper examples/demo-paper/paper.pdf --out reproof-report
```

指定失败阈值：

```powershell
reproof audit . --fail-on high
```

当存在高优先级问题时，命令返回非零退出码，可用于 CI。

## 生成文件

默认生成：

```text
reproof-report/
  report.html
  report.md
  report.json
  pr-comment.md
```

## 演示仓库

```text
examples/
  demo-basic/    # 种子、依赖和路径问题
  demo-leak/     # 预处理发生在数据划分之前
  demo-readme/   # README 命令不存在
  demo-paper/    # 论文与代码数据集/指标不一致
  demo-mixed/    # 综合缺陷
```

运行演示：

```powershell
python -m reproof audit examples/demo-mixed --out tmp/reproof-mixed --fail-on none
```

## 测试

```powershell
python -m unittest discover -s tests -v
```

## GitHub Action

仓库根目录包含 `action.yml`。调用示例：

```yaml
name: ReproProof

on:
  pull_request:

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./
        with:
          path: .
          fail-on: high
```

## 能力边界

- 只支持 Python ML 仓库；
- 数据泄漏检测只覆盖常见调用顺序模式；
- 论文-代码一致性只检查数据集和指标等有限字段；
- 报告是辅助审计结果，不等同于会议或期刊的正式 Artifact Evaluation；
- 默认只做静态分析，不执行用户代码。
