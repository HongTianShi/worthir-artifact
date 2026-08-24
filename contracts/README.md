# 示例契约

这些文件定义包含六个查询的冒烟测试。新任务请使用 `worthir build-custom`；若
输入是 qrels 和 TREC run，则使用 `worthir build-trec`。两者都会创建相互绑定的
任务契约和路线注册表。

公共接口规定五项不变量：有效性越高越好；ledger 包含每个“查询--路线”组合；
成本非负且为累计成本；成本在决策时是否可见必须明确；Oracle 并列时先选择成本
较低者，再按注册顺序选择。决策时已知的固定成本写在路线注册表中；决策时已知的
逐查询成本写在 `participant/route_costs.csv` 中。
