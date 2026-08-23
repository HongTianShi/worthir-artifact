# WorthIR Structured-v2 公共评分接口

任务：`worthir-2wiki-structured-v2.0`

该软件包公开 2,000 个合法的购买时查询状态和 5 种预先声明的证据视图。它不包含
任何“查询--视图”结果、qrels、支持标题、Oracle 动作、效用、遗憾、付费视图分数
或已训练策略输出。

使用 `templates/submission_template.json` 为每个 `query_uid` 创建且只创建一个
动作，然后运行：

```text
python validate_submission.py --public-root . --submission my_policy.json
```

组织者端评分器将动作与私有的完整结果 ledger 关联，并返回汇总有效性、成本、效用、
已注册路线集合内的精确遗憾、动作比例及与冻结参照的比较。提供的自适应参照明确标记为
`A_OOF`：每个查询都由未使用其支持标题连通分量拟合的策略评分。动作向量本身不能证明
其训练来源；监督学习的折叠合规性需要由评测端隔离保证。

由于源任务公开，查询标识符可以在软件包外重新关联到 2Wiki。合法状态边界是时间顺序
上的评测契约，而不是密码学保密声明。托管评测器应限制评分频率并分批发布结果，以减少
近似相同提交之间的差分攻击。
