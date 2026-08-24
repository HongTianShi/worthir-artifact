# 绘图程序

- `make_worthir_contract.py`：协议概览。
- `make_cost_quality_inversion.py`：固定路线成本--有效性曲线。
- `make_recoverability_bridge.py`：任务内可恢复性图。

相邻 CSV/JSON 文件是这些程序使用的精简输入。请通过
`python scripts/reproduce_paper.py --output-dir reproduced/paper` 运行全部
绘图程序，以便首先完成输入和计算检查。
