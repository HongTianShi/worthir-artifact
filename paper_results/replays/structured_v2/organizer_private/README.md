# 2Wiki-Structured 评测 ledger

该目录包含与公共任务接口绑定的 2,000 查询、5 路线结果 ledger，以及按支持标题
连通分量隔离的参照。它属于评测器输入，绝不能用于训练或选择策略。

```bash
python score_submission.py \
  --public-root ../public \
  --private-root . \
  --submission my_policy.json \
  --output score.json
```

评分器返回汇总结果。不确定性区间以 1,636 个支持标题连通分量为单位重采样。
