# ReproProof 真实公开仓库测试记录

> 测试日期：2026-10-22  
> 测试对象：3 个公开 GitHub 机器学习仓库  
> 方式：浅克隆到本地，使用 ReproProof 默认静态规则审计，不执行仓库代码

## 1. 测试仓库

1. https://github.com/kuangliu/pytorch-cifar
2. https://github.com/lucidrains/vit-pytorch
3. https://github.com/hunkim/DeepLearningZeroToAll

## 2. 测试结果

| 仓库 | 评分 | 等级 | 问题数 | 检出规则 |
|---|---:|---|---:|---|
| kuangliu/pytorch-cifar | 64 | C · 高风险 | 2 | R1 随机种子缺失、R2 无依赖清单 |
| lucidrains/vit-pytorch | 82 | B · 需关注 | 1 | R1 训练脚本未设置随机种子 |
| hunkim/DeepLearningZeroToAll | 82 | B · 需关注 | 1 | R2 依赖未锁定 |

## 3. 人工复核

### pytorch-cifar

- `main.py` 包含训练循环、反向传播和优化器更新；
- 未发现 `random.seed`、`np.random.seed` 或 `torch.manual_seed`；
- 仓库未提供 requirements.txt、pyproject.toml 或锁文件。

判断：两项均为真实可复现性风险。

### vit-pytorch

- 初版规则曾误报 `tests/test_dino_loss.py`；
- 已修正为跳过 `test/tests` 目录；
- 复核后命中根目录 `train_vit_decorr.py`；
- 该训练脚本包含 DataLoader、优化器和训练循环，但未设置随机种子。

判断：规则命中真实训练入口，不是测试文件误报。

### DeepLearningZeroToAll

- `requirements.txt` 中依赖未锁定；
- 仓库是教程集合，不存在单一根入口，因此 README 入口规则被限定为“仅对存在明确根入口的仓库生效”；
- 修正后不再对该仓库报 R5。

判断：R2 命中真实风险；R5 已消除不适用误报。

## 4. 规则修正

本轮真实仓库测试后完成两项修正：

1. R1 跳过 `test/tests` 目录，避免把测试文件中的 `loss.backward()` 当作训练入口；
2. R5 仅在仓库存在明确根入口（`train.py/main.py/run.py/fit.py/experiment.py`）时启用，避免对库项目和教程集合产生不适用报错。

## 5. 结论

- 3 个真实仓库均可完成审计；
- 共检出 4 条问题；
- 人工复核后未发现明显误报；
- 规则在没有训练入口或测试文件的仓库上已减少误报；
- 仍然需要更大规模人工标注，不能把本轮结果当作通用准确率。

## 6. 产物

每个仓库均生成：

- HTML 报告；
- Markdown 报告；
- JSON 报告；
- PR 评论文本。
