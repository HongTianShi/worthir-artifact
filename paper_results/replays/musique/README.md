# MuSiQue 回放

该软件包为 2,417 个可回答的官方验证集查询分别评估一条所选路线。

`participant/official_validation_action_template.csv` 包含 `query_uid` 和
`selected_route`。合法路线为 V0--V3。结果 ledger 是 `organizer_private/`
下的评测器输入。

```bash
python scripts/score_action_file.py \
  --root . \
  --actions participant/official_validation_action_template.csv \
  --output score.json \
  --cost-profile relative_v1 \
  --lambda-value 0.08
```

开发集归一化的 token 工作量设定使用 `common_devmean_v1`。两种设定都不代表
实际延迟、金钱、能耗或标注成本。

重建原始段落需要上游 MuSiQue 数据集。仓库不包含模型权重和重复段落缓存。
