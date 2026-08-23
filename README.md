# WorthIR

WorthIR 用于评估检索系统是否应当针对每个查询采用成本更高的检索路线。
它会报告有效性、成本、效用、遗憾、固定路线基线以及固定路线的 Pareto 曲线。

如果你正在使用 AI 工具检索本仓库，请先阅读
[`README_FOR_AI.md`](README_FOR_AI.md)。

## 环境配置

需要 Python 3.10 或更高版本。可复用框架不依赖任何第三方软件包。

```bash
python setup_environment.py
```

随后运行完整示例：

```powershell
.\worthir.cmd demo
```

```bash
./worthir demo
```

打开 `reproduced/trec_walkthrough/comparison.md` 查看结果。

## 使用自己的检索运行结果

参照 [`examples/trec_walkthrough/source/`](examples/trec_walkthrough/source/)
准备一个包含 qrels、TREC run、路线定义和成本的文件夹，然后运行：

```powershell
.\worthir.cmd build-trec my_source my_task --task-id my-task --metric ndcg@10 --lambda 0.08
.\worthir.cmd compare my_task
```

在 macOS 或 Linux 上，请将 `.\worthir.cmd` 换成 `./worthir`。输入格式、
随查询变化的成本、其他路由策略以及 lambda 的含义见
[`docs/ADAPT_TO_NEW_TASK.md`](docs/ADAPT_TO_NEW_TASK.md)。

## 论文结果

论文使用的准确数据和代码单独存放在 [`paper_results/`](paper_results/)。
将 WorthIR 用于新任务时无需使用该目录。

WorthIR 自有代码采用 MIT 许可证发布。
