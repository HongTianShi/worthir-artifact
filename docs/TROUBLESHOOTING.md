# 故障处理

## 确认当前使用的安装

```bash
python --version
python -m worthir doctor
```

WorthIR 需要 Python 3.10 或更高版本。全局 `worthir` 不在 `PATH` 中时，
`python -m worthir` 是最稳妥的入口。

## 源码启动器无法使用 `.venv`

源码启动器在仓库内创建 `.venv`。移动仓库后，该环境可能仍指向旧路径。只删除
当前仓库的 `.venv`，然后重新运行启动器：

```powershell
Remove-Item -LiteralPath .venv -Recurse
.\worthir.cmd doctor
```

```bash
rm -rf .venv
./worthir doctor
```

仅在 Python 可执行文件丢失、仓库已移动，或升级 Python 后包导入立即失败时重建
`.venv`。若报错来自任务契约或缺失的查询—路线组合，应修正任务文件，不要重建环境。

## Windows 启动了错误的 Python

运行 `py -3.13 -m pip install worthir-eval==1.3.0` 和
`py -3.13 -m worthir doctor`，也可将 `3.13` 换成已安装版本。若 Microsoft Store
别名拦截 `python`，可在“管理应用执行别名”中关闭该别名。

## PyPI 安装无法连接包索引

```bash
python -m pip install --index-url https://pypi.org/simple worthir-eval==1.3.0
```

受管理网络应使用本地管理员批准的代理或包索引。源码启动器首次创建 `.venv` 时
同样需要访问 PyPI。

## Hugging Face 或数据下载失败

核心评价器不下载模型。完整路线重建可能访问 Hugging Face 或数据集官网。先重新
运行任务的 `prepare` 阶段。FiQA 示例：

```bash
python paper_results/full_replay/replay.py fiqa260 prepare --workspace fiqa-work
```

若模型站点被阻断，请通过允许的网络下载文档指定的 checkpoint，并让任务适配器
指向本地目录。不要静默替换模型。

## 磁盘空间与缓存位置

`worthir demo-custom` 占用很小；完整重建可能需要数 GB 的模型缓存、语料和索引。
先阅读 `paper_results/full_replay/RESOURCE_REQUIREMENTS.md` 中的任务卡。下载前可将
`HF_HOME` 指向空间充足的磁盘。

## 任务校验失败

运行 `worthir validate-task TASK --output validation.json`。报告会检查查询与路线覆盖、
依赖闭包、累计成本、公开成本一致性和信息边界。缺失查询—路线对或契约格式错误与
Python 环境无关。

## 报告可复现故障

使用仓库的“报告可复现故障”Issue 表单，提供命令、Python 和操作系统版本、完整错误，
以及使用 PyPI 还是源码。不要上传不能再分发的 evaluator ledger。
