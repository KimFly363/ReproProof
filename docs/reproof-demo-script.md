# ReproProof 3-5 分钟演示脚本

> 目标时长：4 分钟 20 秒  
> 画面：终端 + HTML 报告 + GitHub Action 示例  
> 注意：不出现学校名称、Logo、指导教师信息。

## 0:00-0:30 问题引入

画面：一个“看起来正常”的 ML 仓库，有 README、train.py、requirements.txt。

旁白：

> 这是一个准备投稿的机器学习项目，有训练脚本、有依赖文件，看起来一切正常。但它可能仍然无法复现：预处理可能泄漏了测试集，依赖没有锁定，论文里写的指标代码里根本没有计算。等问题在 Artifact Evaluation 被发现，就已经太晚。

## 0:30-1:10 运行 ReproProof

终端：

```bash
reproof audit examples/demo-paper --paper examples/demo-paper/paper.pdf --out reproof-report
```

展示扫描过程、输出问题和评分。

旁白：

> ReproProof 以 CLI 或 GitHub Action 的形式嵌入提交流程。用户只需要指定代码仓库，论文是可选项。系统会运行六条规则，并把每个问题定位到文件和行号。

## 1:10-2:20 展示 HTML 报告

打开 `report.html`，展示：

- 总评分与风险等级；
- 六维评分；
- 问题列表；
- 论文与代码数据集中不一致；
- 论文指标 F1 与代码 accuracy 不一致。

旁白：

> 这里不是简单的关键词提示。报告会显示论文证据和代码证据，说明为什么判定为不一致，并给出修复建议。

## 2:20-3:05 展示数据泄漏

运行 `demo-leak`：

```bash
reproof audit examples/demo-leak --out reproof-report-leak
```

打开报告中的 R4 问题。

旁白：

> 这个仓库在 train_test_split 之前执行了 StandardScaler.fit_transform，测试集信息已经进入训练流程。ReproProof 通过 AST 调用顺序和变量关系发现了这个问题。

## 3:05-3:40 GitHub Action

展示 `action.yml` 和示例工作流。

旁白：

> 它不是需要主动打开的网站。接入 GitHub Action 后，每次 PR 都会自动运行，并可通过 fail-on high 阻断高风险合并。

## 3:40-4:20 测试与收尾

展示测试汇总：

- 6 个受控仓库；
- 11 个规则组合全部命中；
- 12 条问题；
- 干净仓库 0 误报；
- 11 个自动化测试通过。

旁白：

> ReproProof 让可复现性检查从一次人工审计，变成每次代码提交都会运行的质量 Gate，帮助 AI 论文代码在提交前发现那些作者自己很难看见的问题。
