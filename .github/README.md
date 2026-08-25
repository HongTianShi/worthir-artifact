# 自动检查与发布

- `validate.yml` 在 Linux、Windows 和 macOS 上检查框架，测试支持的 Python
  版本，在仓库外安装 wheel，并核对论文结果映射。
- `publish.yml` 构建 wheel 和源码包，通过 Trusted Publishing 将英文版本发布到
  PyPI，并测试公开软件包。
- `fiqa260-smoke.yml` 在 CPU 上重建小规模 FiQA-Compression260 路线并检查 ledger。

简体中文标签用于归档中文源码，不会向 PyPI 重复发布软件包。
