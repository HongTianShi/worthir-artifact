# RQ2--RQ5 分析

从仓库根目录运行：

```bash
python scripts/reproduce_rqs.py --output-dir reproduced/rqs
```

该命令会验证已发布表格，根据逐查询路线结果和动作重新计算 RQ2 策略均值，并写出
精简的 Markdown/CSV 结果。它不会下载语料库、训练路由器或执行神经检索。

| 目录 | 内容 |
| --- | --- |
| `rq2_policy_comparison/` | 匹配的策略结果、成本对照、Holm 检验和 FEVER 延迟 |
| `rq3_utility_sources/` | 查询分层、可预测性和最高十分位切换 |
| `rq4_robustness/` | 成本偏好、重复出现、学习器和折叠检查 |
| `rq5_route_value/` | 相关页面深度、图/分解对照和路线价值预测 |

`structured_v2` 是 2Wiki-Structured 稳定的机器可读标识符。RQ3--RQ5 属于
结果产生后的诊断，不能解释为前瞻性策略评测。
