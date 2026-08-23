# RQ2：策略比较

该软件包在每个任务的完整路线集合和主要成本设定内比较所有策略，包括开发集选定的
固定路线、均匀随机路由、低容量 QPP 门控、任务现有自适应策略，以及仅使用查询文本的
Adaptive Re-Ranking（ARR）BERT 适配。ARR 记录是遵守协议的适配，并非对上游
检查点的复现。

`actions/non_neural_actions.parquet` 和 `actions/arr_actions.parquet` 为每个查询
记录一个路线 ID。`actions/expected_cost_control_probabilities.csv` 包含与各学习
策略期望平均成本相同、且与路线无关的最大熵分布。评分所用的逐查询路线结果位于
`replays/`。

`actions/fever_same_menu_actions.csv` 增加三路线 ExtraTrees 动作向量；
`actions/fever_arr_3_and_5_route_actions.csv` 包含两种 FEVER 路线集合各 5 次 ARR
运行。它们与跨任务动作文件共同复现 FEVER 三/五路线比较中的全部 6 行。

主要统计区间采用各任务的依赖单位。每个任务的 6 个对比构成一个 Holm family：QPP、
现有自适应策略和主要 ARR 运行分别与固定路线及相应的期望成本匹配随机分配比较。

期望成本对照保持期望平均成本，而不是路线频率。因此策略相对该对照的优势同时包含
其路线组合及查询--路线分配的影响。`results/fever_query_route_matching.csv` 中单独
提供的 FEVER 路线频率匹配置换会固定路线计数，只分离路线与查询匹配带来的增益。

`results/fever_online_latency.csv` 报告 RTX 4070 Laptop GPU 上的预热在线均值。
每个均值包含 BM25、路线选择特征构建、一次单查询路由器调用及所选付费操作，不包含
索引构建、模型加载、离线训练、冷启动或尾部延迟。
