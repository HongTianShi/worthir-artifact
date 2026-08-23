# 面向 AI 工具的 WorthIR 项目地图

这是本仓库完整的导航和受跟踪文件审计。进行大范围搜索或修改代码前应先阅读此文件。
根目录下精简的 `README.md` 面向人类用户；本文档有意保留更详细的信息。

## 仓库架构

- 可复用框架位于仓库根目录，包括 `contracts/`、`docs/`、`examples/`、
  `quickstart/`、`scripts/`、`src/` 和 `task_template/`。
- `paper_results/` 包含论文专用动作、评测 ledger、分析、回放包、绘图程序和复现命令。
- `python setup_environment.py` 创建并验证无依赖的框架环境。`worthir.cmd` 和
  `./worthir` 是人类使用的入口；`worthir.py` 是跨平台命令实现。
- `python paper_results/run.py` 创建论文专用环境并验证已发布论文结果。

## 可复用评测流程

1. 从仓库根目录运行 `python setup_environment.py`。
2. 使用 `worthir demo` 验证从 qrels 到报告的完整路径。
3. 对于标准 IR 数据，在 `routes.csv` 中定义路线和成本，然后运行
   `worthir build-trec SOURCE TASK --task-id ID --metric ndcg@K --lambda VALUE`。
4. 将留出查询的路线选择导出为 CSV，并使用
   `worthir actions TASK CHOICES --policy-id ID` 绑定到任务。
5. 运行 `worthir compare TASK`。该命令评估全部策略和全部固定路线，并写出
   Markdown、CSV 和 JSON 报告。
6. 对于非 TREC 指标，使用 `worthir init`，手动替换完整 ledger 后再评分或比较。

## 信息边界与科学不变量

- 策略只能使用所选路线执行前已经可用的信息。
- 相关性标注、未选路线结果、效用、Oracle 动作和遗憾只对评测端可见。
- ledger 必须包含查询与路线的完整笛卡尔积。
- 路线成本为累计成本；子路线成本不得低于父路线。
- 效用为 `effectiveness - lambda * cumulative_cost`。原始效用由任务定义，
  不得跨任务比较。
- Oracle 和遗憾只在已注册路线集合内定义。
- `organizer_private` 文件为支持复现而发布，但在相应策略进行选择时只对评测端可见。

## 公共接口与限制

- 内置适配器读取 qrels 和六列 TREC run 并计算 NDCG@K。其他有效性指标需要预先
  计算 ledger。
- 固定路线成本写入 `routes.csv`；完整的 `costs.csv` 可以用随查询变化的延迟或
  工作量覆盖它们。
- 契约只公开通用评分器实际使用的选项。有效性越高越好、路线集合完整、累计成本非负
  以及 Oracle 并列处理是固定公共不变量，不是被忽略的开关。
- `comparison.md` 是描述性的。通用工具不会虚构不确定性区间或选择 lambda；需要
  推断性结论时，任务所有者必须提供有效重采样设计和预先声明的成本偏好。
- `legal_state.csv` 是有明确说明的参与者输入，评测器不读取它。信息边界是否成立，
  仍取决于策略选择的产生方式。
- 历史论文文件可能保留 `raw_quality`、`menu` 等名称；不要将这些术语复制到可复用
  公共接口中。

## AI 工具修改规则

- 可复用框架代码和依赖必须位于 `paper_results/` 之外。
- 论文专用依赖必须位于 `paper_results/requirements.txt`。
- 可复用 API 使用 `effectiveness`、`available routes` 和 `route set`。
- 绝不能向路由策略代码公开评测 ledger。
- 不要添加哈希、校验和文件、发布清单或维护过程叙述。
- 除非有证据支持用户要求的修正，否则保留已发布科学数值。
- 修改框架后运行 `python run.py`；入口或适配器变化后还要测试一键配置和
  `worthir demo`。
- 修改论文结果后，如果依赖可用，还要运行
  `python paper_results/run.py --use-current-python`。

## 完整受跟踪文件审计（328 个文件）

每个受跟踪路径只列出一次。评测数据不会仅仅因为已经公开，就变成合法的策略输入。

### 根目录文件

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `LICENSE` | 许可证 | WorthIR 自有代码的 MIT 许可证。 |
| `README_FOR_AI.md` | AI 项目地图 | 说明架构、不变量、当前限制以及每个受跟踪文件的用途。 |
| `README.md` | 人类入口 | 提供一键配置、完整演示、自有数据流程和论文结果边界。 |
| `run.py` | 框架验证器 | 运行无依赖的框架验证套件。 |
| `setup_environment.py` | 环境配置 | 创建 `.venv`，在其中公开 `src/`，并在不下载软件包的情况下运行框架检查。 |
| `worthir` | POSIX 启动器 | 必要时初始化本地环境，并将命令转发给统一 CLI。 |
| `worthir.cmd` | Windows 启动器 | 必要时初始化本地环境，并将命令转发给统一 CLI。 |
| `worthir.py` | 统一 CLI | 提供 doctor、demo、init、TREC 构建、动作转换、评分和比较子命令。 |

### 仓库配置

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `.gitattributes` | 仓库配置 | 统一文本换行符，并标记二进制研究资产，避免 Git 改写。 |
| `.github/workflows/validate.yml` | 持续集成 | 在 Windows 和 Linux 上验证框架，并单独复现论文结果。 |
| `.gitignore` | 仓库配置 | 排除生成输出、环境、缓存、编辑器状态和构建产物。 |

### 可复用契约

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `contracts/quickstart_contract.json` | 任务契约 | 定义合成任务、动作模式、指标范围、成本偏好和标识符。 |
| `contracts/README.md` | 契约指南 | 说明共享的快速入门任务契约和路线注册表。 |
| `contracts/route_registry.json` | 路线注册表 | 注册合成快速入门路线及其父子关系。 |

### 可复用说明文档

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `docs/ADAPT_TO_NEW_TASK.md` | 适配指南 | 说明将可运行模板变成新任务的人工步骤。 |
| `docs/COST_AND_LAMBDA.md` | 成本指南 | 说明累计成本选择、归一化、lambda 选择和敏感性。 |
| `docs/OUTPUTS.md` | 输出指南 | 定义比较字段、固定参照、Pareto 归属和描述性范围。 |

### 端到端 TREC 示例

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `examples/trec_walkthrough/README.md` | 操作指南 | 展示从 qrels 到报告的完整演示及添加另一策略的方法。 |
| `examples/trec_walkthrough/source/alternative_choices.csv` | 策略选择 | 为动作转换示例提供第二个查询--路线策略。 |
| `examples/trec_walkthrough/source/policy_choices.csv` | 策略选择 | 提供任务构建时使用的默认自适应选择。 |
| `examples/trec_walkthrough/source/qrels.tsv` | TREC qrels | 定义小型示例任务的分级相关性。 |
| `examples/trec_walkthrough/source/queries.csv` | 参与者状态 | 提供可读查询文本和一个合法的路线选择前特征。 |
| `examples/trec_walkthrough/source/routes.csv` | 路线定义 | 将路线 ID 映射到 TREC run、父依赖、成本和开发集选定固定路线。 |
| `examples/trec_walkthrough/source/runs/base.trec` | TREC run | 提供示例的基础路线排名。 |
| `examples/trec_walkthrough/source/runs/prf.trec` | TREC run | 提供示例的查询扩展排名。 |
| `examples/trec_walkthrough/source/runs/rerank.trec` | TREC run | 提供示例的交叉编码器排名。 |

### 合成快速入门任务

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `quickstart/evaluator/hidden_ledger.csv` | 评测器数据 | 完整的合成有效性和累计成本结果。 |
| `quickstart/evaluator/README.md` | 评测器指南 | 说明为何完整查询--路线结果只对评测端可见。 |
| `quickstart/participant/example_actions.json` | 动作文件 | 与快速入门契约绑定的逐查询单路线决策示例。 |
| `quickstart/participant/legal_state.csv` | 参与者数据 | 合成的推理时查询特征。 |
| `quickstart/participant/README.md` | 参与者指南 | 定义快速入门任务中路由策略可用的信息。 |
| `quickstart/README.md` | 快速入门指南 | 说明无依赖的六查询示例。 |

### 可复用命令

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `scripts/actions_from_csv.py` | 动作转换器 | 验证可读查询--路线选择并写出绑定契约的动作 JSON。 |
| `scripts/build_trec_task.py` | TREC 适配器 | 根据 qrels 和 run 计算 NDCG@K，并构建完整可复用任务。 |
| `scripts/compare_policies.py` | 比较报告器 | 评估全部策略和固定路线，并写出 Markdown、CSV、JSON 和 Pareto 输出。 |
| `scripts/init_task.py` | 任务初始化器 | 复制可运行模板并替换任务、契约和注册表标识符。 |
| `scripts/README.md` | 命令指南 | 索引可复用框架命令。 |
| `scripts/run_integrity_tests.py` | 完整性测试 | 检查无效输入、算术不变量、累计成本、并列情况和示例信息边界。 |
| `scripts/run_smoke_test.py` | 冒烟测试 | 评估六查询快速入门任务并写出汇总结果。 |
| `scripts/score_actions.py` | 评分 CLI | 解析任务输入、调用核心评分器并写出汇总 JSON。 |
| `scripts/validate_framework.py` | 框架验证器 | 运行冒烟测试、完整性测试、任务初始化、TREC 构建、动作转换和比较检查。 |

### 可复用 Python 源码

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `src/README.md` | 源码指南 | 说明无依赖源码布局。 |
| `src/worthir_eval/__init__.py` | Python API | 导出受支持的评分函数和错误类型。 |
| `src/worthir_eval/core.py` | 评分实现 | 验证路线、动作、ledger 和累计成本，再计算有效性、成本、效用、Oracle 一致率和遗憾。 |
| `src/worthir_eval/README.md` | 软件包指南 | 概述评分器 API 及参与者--评测者边界。 |

### 新任务模板

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `task_template/.gitignore` | 模板配置 | 排除生成的任务分数和比较报告。 |
| `task_template/contracts/route_registry.json` | 模板路线注册表 | 可运行的双路线示例，新任务应替换其内容。 |
| `task_template/contracts/task_contract.json` | 模板任务契约 | 可运行的单查询任务、指标、成本和模式示例。 |
| `task_template/evaluator/ledger.csv` | 模板评测器数据 | 完整的单查询、双路线有效性和成本 ledger。 |
| `task_template/participant/actions.json` | 模板动作文件 | 选择一条已注册路线的单行示例。 |
| `task_template/participant/legal_state.csv` | 模板参与者数据 | 单行推理时查询状态示例。 |
| `task_template/README.md` | 模板指南 | 说明何时使用手动模板而不是 TREC 适配器。 |

### 论文结果根目录

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/README.md` | 论文结果入口 | 说明如何复现和验证全部已发布论文输出。 |
| `paper_results/requirements.txt` | 依赖规范 | 仅供论文结果复现使用的固定版本软件包。 |
| `paper_results/run.py` | 论文结果入口 | 创建论文专用环境并启动已发布结果验证。 |

### 论文说明文档

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/docs/DATA_AND_MODEL_TERMS.md` | 数据与模型条款 | 记录许可证、访问条件和使用限制。 |
| `paper_results/docs/README.md` | 文档指南 | 索引论文结果语义、数据条款和声明。 |
| `paper_results/docs/REFERENCE_SEMANTICS.md` | 参照语义 | 定义可部署策略、仅评测端参照、机会和遗憾。 |
| `paper_results/docs/THIRD_PARTY_NOTICES.md` | 第三方声明 | 注明外部数据集、模型和软件的来源。 |

### 完整回放指南

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/full_replay/CANONICAL_TREC.md` | Full-replay specification | Documents canonical TREC-DL reconstruction. |
| `paper_results/full_replay/FEVER.md` | Full-replay specification | Documents FEVER reconstruction. |
| `paper_results/full_replay/MUSIQUE.md` | Full-replay specification | Documents MuSiQue reconstruction. |
| `paper_results/full_replay/README.md` | Full-replay guide | Explains what is required to rebuild retrieval outputs. |
| `paper_results/full_replay/RESOURCE_REQUIREMENTS.md` | Resource guide | Summarizes software, storage, model, and compute needs. |
| `paper_results/full_replay/STRUCTURED_AND_DIAGNOSTIC.md` | Full-replay specification | Documents structured and diagnostic reconstructions. |

### 论文分析：概览

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/analyses/README.md` | Analysis guide | Indexes released RQ2-RQ5 analyses and their evidentiary scope. |

### 论文分析：RQ2

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/analyses/rq2_policy_comparison/actions/arr_actions.parquet` | Columnar analysis data | arr actions: released RQ2 policy action or control input used by the paper analysis. |
| `paper_results/analyses/rq2_policy_comparison/actions/expected_cost_control_probabilities.csv` | Analysis table | expected cost control probabilities: released RQ2 policy action or control input used by the paper analysis. |
| `paper_results/analyses/rq2_policy_comparison/actions/fever_arr_3_and_5_route_actions.csv` | Analysis table | fever arr 3 and 5 route actions: released RQ2 policy action or control input used by the paper analysis. |
| `paper_results/analyses/rq2_policy_comparison/actions/fever_same_menu_actions.csv` | Analysis table | fever same menu actions: released RQ2 policy action or control input used by the paper analysis. |
| `paper_results/analyses/rq2_policy_comparison/actions/non_neural_actions.parquet` | Columnar analysis data | non neural actions: released RQ2 policy action or control input used by the paper analysis. |
| `paper_results/analyses/rq2_policy_comparison/actions/README.md` | Analysis guide | Explains the RQ2 action inputs. |
| `paper_results/analyses/rq2_policy_comparison/README.md` | Analysis guide | Explains the RQ2 analysis package. |
| `paper_results/analyses/rq2_policy_comparison/results/expected_cost_controls.csv` | Analysis table | expected cost controls: released RQ2 derived comparison or statistical result used by the paper analysis. |
| `paper_results/analyses/rq2_policy_comparison/results/fever_online_latency.csv` | Analysis table | fever online latency: released RQ2 derived comparison or statistical result used by the paper analysis. |
| `paper_results/analyses/rq2_policy_comparison/results/fever_pairwise_comparison.csv` | Analysis table | fever pairwise comparison: released RQ2 derived comparison or statistical result used by the paper analysis. |
| `paper_results/analyses/rq2_policy_comparison/results/fever_query_route_matching.csv` | Analysis table | fever query route matching: released RQ2 derived comparison or statistical result used by the paper analysis. |
| `paper_results/analyses/rq2_policy_comparison/results/fever_same_menu_policy_comparison.csv` | Analysis table | fever same menu policy comparison: released RQ2 derived comparison or statistical result used by the paper analysis. |
| `paper_results/analyses/rq2_policy_comparison/results/holm_tests.csv` | Analysis table | holm tests: released RQ2 derived comparison or statistical result used by the paper analysis. |
| `paper_results/analyses/rq2_policy_comparison/results/policy_comparison.csv` | Analysis table | policy comparison: released RQ2 derived comparison or statistical result used by the paper analysis. |
| `paper_results/analyses/rq2_policy_comparison/results/README.md` | Analysis guide | Explains the RQ2 derived results. |
| `paper_results/analyses/rq2_policy_comparison/results/uniform_random_seed_results.csv` | Analysis table | uniform random seed results: released RQ2 derived comparison or statistical result used by the paper analysis. |

### 论文分析：RQ3

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/analyses/rq3_utility_sources/data/query_strata.csv` | Analysis table | query strata: released RQ3 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq3_utility_sources/data/README.md` | Analysis guide | Explains the RQ3 diagnostic data. |
| `paper_results/analyses/rq3_utility_sources/data/top_decile_switching.csv` | Analysis table | top decile switching: released RQ3 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq3_utility_sources/README.md` | Analysis guide | Explains the RQ3 analysis package. |

### 论文分析：RQ4

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/analyses/rq4_robustness/data/cost_preference_summary.csv` | Analysis table | cost preference summary: released RQ4 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq4_robustness/data/fever_candidate_dependence.csv` | Analysis table | fever candidate dependence: released RQ4 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq4_robustness/data/model_and_fold_summary.csv` | Analysis table | model and fold summary: released RQ4 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq4_robustness/data/README.md` | Analysis guide | Explains the RQ4 diagnostic data. |
| `paper_results/analyses/rq4_robustness/data/structured_candidate_recurrence.csv` | Analysis table | structured candidate recurrence: released RQ4 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq4_robustness/README.md` | Analysis guide | Explains the RQ4 analysis package. |

### 论文分析：RQ5

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/analyses/rq5_route_value/data/difficulty_opportunity_summary.csv` | Analysis table | difficulty opportunity summary: released RQ5 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq5_route_value/data/README.md` | Analysis guide | Explains the RQ5 diagnostic data. |
| `paper_results/analyses/rq5_route_value/data/rq5_axis_within_difficulty.csv` | Analysis table | rq5 axis within difficulty: released RQ5 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq5_route_value/data/rq5_complementarity_summary.csv` | Analysis table | rq5 complementarity summary: released RQ5 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq5_route_value/data/rq5_difficulty_band_heterogeneity.csv` | Analysis table | rq5 difficulty band heterogeneity: released RQ5 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq5_route_value/data/rq5_fever_gold_rank_band_routes.csv` | Analysis table | rq5 fever gold rank band routes: released RQ5 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq5_route_value/data/rq5_information_block_contrasts.csv` | Analysis table | rq5 information block contrasts: released RQ5 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq5_route_value/data/rq5_operation_control_summary.csv` | Analysis table | rq5 operation control summary: released RQ5 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq5_route_value/data/rq5_route_value_prediction_summary.csv` | Analysis table | rq5 route value prediction summary: released RQ5 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq5_route_value/data/rq5_structured_question_type_profiles.csv` | Analysis table | rq5 structured question type profiles: released RQ5 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq5_route_value/README.md` | Analysis guide | Explains the RQ5 analysis package. |

### 论文图表

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/paper_reproduction/figures/cost_quality_inversion_data.csv` | Paper input | cost quality inversion data: compact values consumed by a figure or table builder. |
| `paper_results/paper_reproduction/figures/hero_example_2019.json` | Paper input | hero example 2019: compact values consumed by a figure or table builder. |
| `paper_results/paper_reproduction/figures/make_cost_quality_inversion.py` | Figure builder | make cost quality inversion: recreates a released WorthIR paper figure. |
| `paper_results/paper_reproduction/figures/make_recoverability_bridge.py` | Figure builder | make recoverability bridge: recreates a released WorthIR paper figure. |
| `paper_results/paper_reproduction/figures/make_worthir_contract.py` | Figure builder | make worthir contract: recreates a released WorthIR paper figure. |
| `paper_results/paper_reproduction/figures/README.md` | Figure-builder guide | Maps figure scripts to compact inputs. |
| `paper_results/paper_reproduction/figures/recoverability_bridge_data.csv` | Paper input | recoverability bridge data: compact values consumed by a figure or table builder. |
| `paper_results/paper_reproduction/inputs/README.md` | Paper-input guide | Explains compact table and query-level inputs. |
| `paper_results/paper_reproduction/inputs/table3_recoverability.csv` | Paper input | table3 recoverability: compact values consumed by a figure or table builder. |
| `paper_results/paper_reproduction/inputs/table4_expected.csv` | Paper input | table4 expected: compact values consumed by a figure or table builder. |
| `paper_results/paper_reproduction/inputs/table4_query_level.parquet` | Paper input | table4 query level: query-level source rows for rebuilding a released table. |
| `paper_results/paper_reproduction/README.md` | Paper-reproduction guide | Explains compact figure and table inputs, builders, and reference outputs. |
| `paper_results/paper_reproduction/reference_outputs/figure1.pdf` | Archived figure | figure1: reference PDF for comparison with regenerated artwork. |
| `paper_results/paper_reproduction/reference_outputs/figure2.pdf` | Archived figure | figure2: reference PDF for comparison with regenerated artwork. |
| `paper_results/paper_reproduction/reference_outputs/figure3.pdf` | Archived figure | figure3: reference PDF for comparison with regenerated artwork. |
| `paper_results/paper_reproduction/reference_outputs/README.md` | Reference-output guide | Explains archived figure PDFs and their comparison role. |

### 任务回放：概览

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/replays/README.md` | Replay guide | Indexes every task replay and its evidence type. |

### 任务回放：TREC-DL

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/replays/canonical_trec/BUILD_REPORT.json` | Build record | Records TREC-DL replay construction counts, checks, and outputs. |
| `paper_results/replays/canonical_trec/organizer_private/data/test/2019/query_membership.parquet` | Evaluator data | query membership: TREC-DL evaluation membership or grouped folds; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/canonical_trec/organizer_private/data/test/2019/route_outcomes.parquet` | Evaluator data | route outcomes: TREC-DL complete per-query route outcomes; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/canonical_trec/organizer_private/data/test/2020/query_membership.parquet` | Evaluator data | query membership: TREC-DL evaluation membership or grouped folds; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/canonical_trec/organizer_private/data/test/2020/route_outcomes.parquet` | Evaluator data | route outcomes: TREC-DL complete per-query route outcomes; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/canonical_trec/organizer_private/manifest.json` | Replay inventory | Lists released TREC-DL components and provenance metadata. |
| `paper_results/replays/canonical_trec/public/contracts/cost_contract.json` | Replay contract | cost contract: defines TREC-DL cost and utility semantics. |
| `paper_results/replays/canonical_trec/public/contracts/evaluator_schema.json` | Replay contract | evaluator schema: defines TREC-DL evaluator-only fields. |
| `paper_results/replays/canonical_trec/public/contracts/legal_state_schema.json` | Replay contract | legal state schema: defines TREC-DL participant-visible fields and exclusions. |
| `paper_results/replays/canonical_trec/public/contracts/PREFREEZE_LOCK.json` | Replay contract | PREFREEZE LOCK: defines TREC-DL frozen pre-evaluation decisions. |
| `paper_results/replays/canonical_trec/public/contracts/REFERENCE_BASELINE_PREFIT_LOCK.json` | Replay contract | REFERENCE BASELINE PREFIT LOCK: defines TREC-DL frozen pre-evaluation decisions. |
| `paper_results/replays/canonical_trec/public/contracts/route_registry.json` | Replay contract | route registry: defines TREC-DL available routes and dependencies. |
| `paper_results/replays/canonical_trec/public/contracts/submission.schema.json` | Replay contract | submission.schema: defines TREC-DL accepted action-file structure. |
| `paper_results/replays/canonical_trec/public/contracts/task_contract.json` | Replay contract | task contract: defines TREC-DL task population, metric, route set, and evaluation rules. |
| `paper_results/replays/canonical_trec/public/data/test/2019/legal_state.parquet` | Participant data | legal state: TREC-DL inference-time state available to the routing policy. |
| `paper_results/replays/canonical_trec/public/data/test/2019/query_membership.parquet` | Participant data | query membership: TREC-DL query or split membership. |
| `paper_results/replays/canonical_trec/public/data/test/2020/legal_state.parquet` | Participant data | legal state: TREC-DL inference-time state available to the routing policy. |
| `paper_results/replays/canonical_trec/public/data/test/2020/query_membership.parquet` | Participant data | query membership: TREC-DL query or split membership. |
| `paper_results/replays/canonical_trec/public/docs/DATA_ACCESS_NOTICE.md` | Scientific specification | DATA ACCESS NOTICE: documents TREC-DL scope, execution, provenance, environment, or frozen analysis decisions. |
| `paper_results/replays/canonical_trec/public/docs/EVALUATION_OUTPUTS.md` | Scientific specification | EVALUATION OUTPUTS: documents TREC-DL scope, execution, provenance, environment, or frozen analysis decisions. |
| `paper_results/replays/canonical_trec/public/docs/REFERENCE_BASELINE_PREFIT_SPEC.md` | Scientific specification | REFERENCE BASELINE PREFIT SPEC: documents TREC-DL scope, execution, provenance, environment, or frozen analysis decisions. |
| `paper_results/replays/canonical_trec/public/docs/REPRODUCIBILITY_ENVIRONMENT.json` | Machine-readable specification | REPRODUCIBILITY ENVIRONMENT: documents TREC-DL scope, execution, provenance, environment, or frozen analysis decisions. |
| `paper_results/replays/canonical_trec/public/docs/SCIENTIFIC_TASK_SPECIFICATION.md` | Scientific specification | SCIENTIFIC TASK SPECIFICATION: documents TREC-DL scope, execution, provenance, environment, or frozen analysis decisions. |
| `paper_results/replays/canonical_trec/public/manifest.json` | Replay inventory | Lists released TREC-DL components and provenance metadata. |
| `paper_results/replays/canonical_trec/public/README.md` | Replay guide | Explains the TREC-DL replay directory, evidence status, entry points, and interpretation. |
| `paper_results/replays/canonical_trec/public/reference_baselines/BASELINE_TRAINING_MANIFEST.json` | Baseline record | BASELINE TRAINING MANIFEST: frozen TREC-DL reference-baseline model, parameters, or training metadata. |
| `paper_results/replays/canonical_trec/public/reference_baselines/bm25_margin_qpp_gate.json` | Baseline record | bm25 margin qpp gate: frozen TREC-DL reference-baseline model, parameters, or training metadata. |
| `paper_results/replays/canonical_trec/public/reference_baselines/extratrees_quality_regression.joblib` | Reference model | extratrees quality regression: frozen TREC-DL reference-baseline model, parameters, or training metadata. |
| `paper_results/replays/canonical_trec/public/reference_baselines/extratrees_quality_regression.json` | Baseline record | extratrees quality regression: frozen TREC-DL reference-baseline model, parameters, or training metadata. |
| `paper_results/replays/canonical_trec/public/reference_submissions/cross_encoder.json` | Reference submission | cross encoder: frozen TREC-DL fixed or development-selected action vector. |
| `paper_results/replays/canonical_trec/public/reference_submissions/dense_fusion.json` | Reference submission | dense fusion: frozen TREC-DL fixed or development-selected action vector. |
| `paper_results/replays/canonical_trec/public/reference_submissions/development_selected.json` | Reference submission | development selected: frozen TREC-DL fixed or development-selected action vector. |
| `paper_results/replays/canonical_trec/public/reference_submissions/late_interaction.json` | Reference submission | late interaction: frozen TREC-DL fixed or development-selected action vector. |
| `paper_results/replays/canonical_trec/public/reference_submissions/stop_bm25.json` | Reference submission | stop bm25: frozen TREC-DL fixed or development-selected action vector. |
| `paper_results/replays/canonical_trec/public/requirements-baselines.txt` | Dependency specification | requirements baselines: packages required by the TREC-DL replay or reference baselines. |
| `paper_results/replays/canonical_trec/public/requirements-lock.txt` | Dependency specification | requirements lock: packages required by the TREC-DL replay or reference baselines. |
| `paper_results/replays/canonical_trec/public/requirements.txt` | Dependency specification | requirements: packages required by the TREC-DL replay or reference baselines. |
| `paper_results/replays/canonical_trec/public/templates/submission_template.json` | Submission template | submission template: example legal TREC-DL route-selection file. |
| `paper_results/replays/canonical_trec/README.md` | Replay guide | Explains the TREC-DL replay directory, evidence status, entry points, and interpretation. |
| `paper_results/replays/canonical_trec/score_actions.py` | Replay script | score actions: scores action or submission files for TREC-DL. |

### 任务回放：Dense-standard 与历史任务

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/replays/dense_and_legacy_recoverability/analysis_results.json` | Replay data | analysis results: Dense-standard and legacy data or derived results used by task-specific validation. |
| `paper_results/replays/dense_and_legacy_recoverability/baseline_semantics_by_split.csv` | Replay data | baseline semantics by split: Dense-standard and legacy data or derived results used by task-specific validation. |
| `paper_results/replays/dense_and_legacy_recoverability/baseline_semantics_summary.csv` | Replay data | baseline semantics summary: Dense-standard and legacy data or derived results used by task-specific validation. |
| `paper_results/replays/dense_and_legacy_recoverability/deployable_ci_hyperlink.json` | Replay data | deployable ci hyperlink: Dense-standard and legacy data or derived results used by task-specific validation. |
| `paper_results/replays/dense_and_legacy_recoverability/deployable_ci_structured.json` | Replay data | deployable ci structured: Dense-standard and legacy data or derived results used by task-specific validation. |
| `paper_results/replays/dense_and_legacy_recoverability/README.md` | Replay guide | Explains the Dense-standard and legacy replay directory, evidence status, entry points, and interpretation. |
| `paper_results/replays/dense_and_legacy_recoverability/recoverability_core.csv` | Replay data | recoverability core: Dense-standard and legacy data or derived results used by task-specific validation. |

### 任务回放：FEVER

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/replays/fever/audits/fever_target_dependence/analyze_fever_target_dependence.py` | Replay script | analyze fever target dependence: runs the named audit or sensitivity analysis for FEVER. |
| `paper_results/replays/fever/audits/fever_target_dependence/fever_dependency_components.csv` | Audit table | fever dependency components: human- or machine-readable FEVER validation, robustness, latency, or scientific findings. |
| `paper_results/replays/fever/audits/fever_target_dependence/FEVER_TARGET_DEPENDENCE_SENSITIVITY.json` | Audit results | FEVER TARGET DEPENDENCE SENSITIVITY: human- or machine-readable FEVER validation, robustness, latency, or scientific findings. |
| `paper_results/replays/fever/audits/fever_target_dependence/FEVER_TARGET_DEPENDENCE_SENSITIVITY.md` | Audit report | FEVER TARGET DEPENDENCE SENSITIVITY: human- or machine-readable FEVER validation, robustness, latency, or scientific findings. |
| `paper_results/replays/fever/audits/fever_target_dependence/fever_target_sensitivity.csv` | Audit table | fever target sensitivity: human- or machine-readable FEVER validation, robustness, latency, or scientific findings. |
| `paper_results/replays/fever/frozen_results/frozen_policy_registry.json` | Evaluator record | frozen policy registry: FEVER frozen policy registry; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/fever/frozen_results/frozen_test_actions.jsonl` | Evaluator data | frozen test actions: FEVER frozen policy actions; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/fever/frozen_results/full_central_table.csv` | Evaluator table | full central table: FEVER released evaluator result or replay support data; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/fever/frozen_results/FULL_EVALUATION.json` | Evaluator record | FULL EVALUATION: FEVER released evaluator result or replay support data; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/fever/frozen_results/LATENCY_FRONTIER.json` | Evaluator record | LATENCY FRONTIER: FEVER released evaluator result or replay support data; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/fever/frozen_results/registered_actions_lambda08.csv` | Evaluator table | registered actions lambda08: FEVER frozen policy actions; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/fever/frozen_results/replayed_score_lambda08.json` | Evaluator record | replayed score lambda08: FEVER released evaluator result or replay support data; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/fever/organizer_private/official_dev_test_membership.parquet` | Evaluator data | official dev test membership: FEVER evaluation membership or grouped folds; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/fever/organizer_private/route_costs.parquet` | Evaluator data | route costs: FEVER cumulative route costs; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/fever/organizer_private/test_outcomes.parquet` | Evaluator data | test outcomes: FEVER complete per-query route outcomes; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/fever/participant/action_template.csv` | Action template | action template: FEVER action rows or action descriptors. |
| `paper_results/replays/fever/participant/legal_state.parquet` | Participant data | legal state: FEVER inference-time state available to the routing policy. |
| `paper_results/replays/fever/README.md` | Replay guide | Explains the FEVER replay directory, evidence status, entry points, and interpretation. |
| `paper_results/replays/fever/reports/FEVER_FULL_VALIDATION_REPORT.md` | Audit report | FEVER FULL VALIDATION REPORT: human- or machine-readable FEVER validation, robustness, latency, or scientific findings. |
| `paper_results/replays/fever/reports/FEVER_SCIENTIFIC_DECISION.md` | Audit report | FEVER SCIENTIFIC DECISION: human- or machine-readable FEVER validation, robustness, latency, or scientific findings. |
| `paper_results/replays/fever/reports/FULL_EVALUATION_REPORT.md` | Audit report | FULL EVALUATION REPORT: human- or machine-readable FEVER validation, robustness, latency, or scientific findings. |
| `paper_results/replays/fever/reports/full_validation_results.json` | Audit results | full validation results: human- or machine-readable FEVER validation, robustness, latency, or scientific findings. |
| `paper_results/replays/fever/reports/WARM_LATENCY_REPORT.json` | Audit results | WARM LATENCY REPORT: human- or machine-readable FEVER validation, robustness, latency, or scientific findings. |
| `paper_results/replays/fever/scripts/make_action_template.py` | Replay script | make action template: creates an action template for FEVER. |
| `paper_results/replays/fever/scripts/score_actions.py` | Replay script | score actions: scores action or submission files for FEVER. |
| `paper_results/replays/fever/scripts/verify_bundle.py` | Replay script | verify bundle: validates released files for FEVER. |
| `paper_results/replays/fever/spec/AMENDMENT_05_LATENCY_PROTOCOL.md` | Scientific specification | AMENDMENT 05 LATENCY PROTOCOL: documents FEVER scope, execution, provenance, environment, or frozen analysis decisions. |
| `paper_results/replays/fever/spec/FULL_RUN_AUTHORIZATION.md` | Scientific specification | FULL RUN AUTHORIZATION: documents FEVER scope, execution, provenance, environment, or frozen analysis decisions. |
| `paper_results/replays/fever/spec/WORTHIR_FEVER_PREREGISTRATION.md` | Scientific specification | WORTHIR FEVER PREREGISTRATION: documents FEVER scope, execution, provenance, environment, or frozen analysis decisions. |

### 任务回放：FiQA260

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/replays/fiqa260/candidate_pool_fingerprints.parquet` | Replay data | candidate pool fingerprints: FiQA260 data or derived results used by task-specific validation. |
| `paper_results/replays/fiqa260/execution_fingerprints.parquet` | Replay data | execution fingerprints: FiQA260 data or derived results used by task-specific validation. |
| `paper_results/replays/fiqa260/legal_state.parquet` | Replay data | legal state: FiQA260 data or derived results used by task-specific validation. |
| `paper_results/replays/fiqa260/manifest.json` | Replay inventory | Lists released FiQA260 components and provenance metadata. |
| `paper_results/replays/fiqa260/query_membership.parquet` | Replay data | query membership: FiQA260 data or derived results used by task-specific validation. |
| `paper_results/replays/fiqa260/raw_quality_labels.parquet` | Replay data | raw quality labels: FiQA260 data or derived results used by task-specific validation. |
| `paper_results/replays/fiqa260/README.md` | Replay guide | Explains the FiQA260 replay directory, evidence status, entry points, and interpretation. |
| `paper_results/replays/fiqa260/schema.json` | Replay schema | Defines FiQA260 tables, fields, data types, and meanings. |

### 任务回放：Hyperlink10k

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/replays/hyperlink10k/build_summary.json` | Build record | Records Hyperlink10k replay construction counts, checks, and outputs. |
| `paper_results/replays/hyperlink10k/organizer_private/data/candidate_pool_fingerprints.parquet` | Evaluator data | candidate pool fingerprints: Hyperlink10k released evaluator result or replay support data; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/hyperlink10k/organizer_private/data/execution_fingerprints.parquet` | Evaluator data | execution fingerprints: Hyperlink10k released evaluator result or replay support data; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/hyperlink10k/organizer_private/data/raw_outcomes.parquet` | Evaluator data | raw outcomes: Hyperlink10k complete per-query route outcomes; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/hyperlink10k/organizer_private/data/references.parquet` | Evaluator data | references: Hyperlink10k relevance references; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/hyperlink10k/organizer_private/execution_specs.json` | Evaluator record | execution specs: Hyperlink10k released evaluator result or replay support data; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/hyperlink10k/organizer_private/fixed_baseline_replay.json` | Evaluator record | fixed baseline replay: Hyperlink10k released evaluator result or replay support data; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed17/fixed_full_local_pool.json` | Golden submission | fixed full local pool: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed17/fixed_hyperlink_1hop.json` | Golden submission | fixed hyperlink 1hop: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed17/fixed_hyperlink_2hop.json` | Golden submission | fixed hyperlink 2hop: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed17/fixed_provided_context.json` | Golden submission | fixed provided context: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed17/fixed_summary.json` | Golden submission | fixed summary: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed17/oracle_canary.json` | Evaluator canary | oracle canary: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed23/fixed_full_local_pool.json` | Golden submission | fixed full local pool: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed23/fixed_hyperlink_1hop.json` | Golden submission | fixed hyperlink 1hop: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed23/fixed_hyperlink_2hop.json` | Golden submission | fixed hyperlink 2hop: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed23/fixed_provided_context.json` | Golden submission | fixed provided context: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed23/fixed_summary.json` | Golden submission | fixed summary: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed23/oracle_canary.json` | Evaluator canary | oracle canary: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed31/fixed_full_local_pool.json` | Golden submission | fixed full local pool: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed31/fixed_hyperlink_1hop.json` | Golden submission | fixed hyperlink 1hop: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed31/fixed_hyperlink_2hop.json` | Golden submission | fixed hyperlink 2hop: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed31/fixed_provided_context.json` | Golden submission | fixed provided context: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed31/fixed_summary.json` | Golden submission | fixed summary: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed31/oracle_canary.json` | Evaluator canary | oracle canary: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed43/fixed_full_local_pool.json` | Golden submission | fixed full local pool: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed43/fixed_hyperlink_1hop.json` | Golden submission | fixed hyperlink 1hop: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed43/fixed_hyperlink_2hop.json` | Golden submission | fixed hyperlink 2hop: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed43/fixed_provided_context.json` | Golden submission | fixed provided context: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed43/fixed_summary.json` | Golden submission | fixed summary: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed43/oracle_canary.json` | Evaluator canary | oracle canary: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed59/fixed_full_local_pool.json` | Golden submission | fixed full local pool: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed59/fixed_hyperlink_1hop.json` | Golden submission | fixed hyperlink 1hop: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed59/fixed_hyperlink_2hop.json` | Golden submission | fixed hyperlink 2hop: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed59/fixed_provided_context.json` | Golden submission | fixed provided context: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed59/fixed_summary.json` | Golden submission | fixed summary: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/golden_submissions/seed59/oracle_canary.json` | Evaluator canary | oracle canary: known Hyperlink10k actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/hyperlink10k/organizer_private/manifest.json` | Replay inventory | Lists released Hyperlink10k components and provenance metadata. |
| `paper_results/replays/hyperlink10k/organizer_private/README.md` | Replay guide | Explains the Hyperlink10k replay directory, evidence status, entry points, and interpretation. |
| `paper_results/replays/hyperlink10k/organizer_private/score_submission.py` | Replay script | score submission: scores action or submission files for Hyperlink10k. |
| `paper_results/replays/hyperlink10k/organizer_private/source_provenance.json` | Evaluator record | source provenance: Hyperlink10k source lineage; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/hyperlink10k/public/contracts/cost_contract.json` | Replay contract | cost contract: defines Hyperlink10k cost and utility semantics. |
| `paper_results/replays/hyperlink10k/public/contracts/legal_state_schema.json` | Replay contract | legal state schema: defines Hyperlink10k participant-visible fields and exclusions. |
| `paper_results/replays/hyperlink10k/public/contracts/legal_submenus.json` | Replay contract | legal submenus: defines Hyperlink10k legal route subsets. |
| `paper_results/replays/hyperlink10k/public/contracts/route_registry.json` | Replay contract | route registry: defines Hyperlink10k available routes and dependencies. |
| `paper_results/replays/hyperlink10k/public/contracts/submission.schema.json` | Replay contract | submission.schema: defines Hyperlink10k accepted action-file structure. |
| `paper_results/replays/hyperlink10k/public/contracts/task_contract.json` | Replay contract | task contract: defines Hyperlink10k task population, metric, route set, and evaluation rules. |
| `paper_results/replays/hyperlink10k/public/data/legal_action_descriptors.parquet` | Participant data | legal action descriptors: Hyperlink10k action rows or action descriptors. |
| `paper_results/replays/hyperlink10k/public/data/legal_query_state.parquet` | Participant data | legal query state: Hyperlink10k inference-time state available to the routing policy. |
| `paper_results/replays/hyperlink10k/public/data/query_membership.parquet` | Participant data | query membership: Hyperlink10k query or split membership. |
| `paper_results/replays/hyperlink10k/public/data/split_assignments.parquet` | Participant data | split assignments: Hyperlink10k inference-time state available to the routing policy. |
| `paper_results/replays/hyperlink10k/public/manifest.json` | Replay inventory | Lists released Hyperlink10k components and provenance metadata. |
| `paper_results/replays/hyperlink10k/public/README.md` | Replay guide | Explains the Hyperlink10k replay directory, evidence status, entry points, and interpretation. |
| `paper_results/replays/hyperlink10k/public/templates/submission_template.json` | Submission template | submission template: example legal Hyperlink10k route-selection file. |
| `paper_results/replays/hyperlink10k/public/validate_submission.py` | Replay script | validate submission: validates released files for Hyperlink10k. |
| `paper_results/replays/hyperlink10k/README.md` | Replay guide | Explains the Hyperlink10k replay directory, evidence status, entry points, and interpretation. |

### 任务回放：MuSiQue

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/replays/musique/examples/common_denominator_actions.parquet` | Replay data | common denominator actions: MuSiQue data or derived results used by task-specific validation. |
| `paper_results/replays/musique/examples/official_validation_actions.parquet` | Replay data | official validation actions: MuSiQue data or derived results used by task-specific validation. |
| `paper_results/replays/musique/manifest.json` | Replay inventory | Lists released MuSiQue components and provenance metadata. |
| `paper_results/replays/musique/organizer_private/controls_private.parquet` | Evaluator data | controls private: MuSiQue evaluator-only control data; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/musique/organizer_private/official_validation_components.parquet` | Evaluator data | official validation components: MuSiQue released evaluator result or replay support data; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/musique/organizer_private/qrels_private.parquet` | Evaluator data | qrels private: MuSiQue relevance references; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/musique/organizer_private/rankings_private.npz` | Evaluator data | rankings private: MuSiQue stored route rankings; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/musique/organizer_private/route_outcomes_private.parquet` | Evaluator data | route outcomes private: MuSiQue complete per-query route outcomes; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/musique/organizer_private/route_runtime.parquet` | Evaluator data | route runtime: MuSiQue runtime or latency measurements; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/musique/participant/candidate_pool_fingerprints.parquet` | Participant data | candidate pool fingerprints: MuSiQue candidate-pool identity and recurrence descriptors. |
| `paper_results/replays/musique/participant/legal_state.parquet` | Participant data | legal state: MuSiQue inference-time state available to the routing policy. |
| `paper_results/replays/musique/participant/official_validation_action_template.csv` | Action template | official validation action template: MuSiQue action rows or action descriptors. |
| `paper_results/replays/musique/participant/policy_state.parquet` | Participant data | policy state: MuSiQue inference-time state available to the routing policy. |
| `paper_results/replays/musique/participant/query_membership.parquet` | Participant data | query membership: MuSiQue query or split membership. |
| `paper_results/replays/musique/README.md` | Replay guide | Explains the MuSiQue replay directory, evidence status, entry points, and interpretation. |
| `paper_results/replays/musique/reports/ADMISSION_GATE_REPORT.md` | Audit report | ADMISSION GATE REPORT: human- or machine-readable MuSiQue validation, robustness, latency, or scientific findings. |
| `paper_results/replays/musique/reports/admission_gate_results.json` | Audit results | admission gate results: human- or machine-readable MuSiQue validation, robustness, latency, or scientific findings. |
| `paper_results/replays/musique/reports/COMMON_COST_DEPENDENCE_AUDIT.md` | Audit report | COMMON COST DEPENDENCE AUDIT: human- or machine-readable MuSiQue validation, robustness, latency, or scientific findings. |
| `paper_results/replays/musique/reports/common_cost_dependence_results.json` | Audit results | common cost dependence results: human- or machine-readable MuSiQue validation, robustness, latency, or scientific findings. |
| `paper_results/replays/musique/reports/COMMON_DENOMINATOR_COST_AUDIT.md` | Audit report | COMMON DENOMINATOR COST AUDIT: human- or machine-readable MuSiQue validation, robustness, latency, or scientific findings. |
| `paper_results/replays/musique/reports/common_denominator_cost_results.json` | Audit results | common denominator cost results: human- or machine-readable MuSiQue validation, robustness, latency, or scientific findings. |
| `paper_results/replays/musique/reports/DECISION_SUMMARY.md` | Audit report | DECISION SUMMARY: human- or machine-readable MuSiQue validation, robustness, latency, or scientific findings. |
| `paper_results/replays/musique/reports/dependence_audit_results.json` | Audit results | dependence audit results: human- or machine-readable MuSiQue validation, robustness, latency, or scientific findings. |
| `paper_results/replays/musique/reports/DEPENDENCE_UNIT_AUDIT.md` | Audit report | DEPENDENCE UNIT AUDIT: human- or machine-readable MuSiQue validation, robustness, latency, or scientific findings. |
| `paper_results/replays/musique/reports/MUSIQUE_WORTHIR_FINAL_REPORT.md` | Audit report | MUSIQUE WORTHIR FINAL REPORT: human- or machine-readable MuSiQue validation, robustness, latency, or scientific findings. |
| `paper_results/replays/musique/reports/postgate_cost_sensitivity.json` | Audit results | postgate cost sensitivity: human- or machine-readable MuSiQue validation, robustness, latency, or scientific findings. |
| `paper_results/replays/musique/reports/POSTGATE_COST_SENSITIVITY.md` | Audit report | POSTGATE COST SENSITIVITY: human- or machine-readable MuSiQue validation, robustness, latency, or scientific findings. |
| `paper_results/replays/musique/reports/REPRODUCIBILITY_REPORT.md` | Audit report | REPRODUCIBILITY REPORT: human- or machine-readable MuSiQue validation, robustness, latency, or scientific findings. |
| `paper_results/replays/musique/reports/reproducibility_results.json` | Audit results | reproducibility results: human- or machine-readable MuSiQue validation, robustness, latency, or scientific findings. |
| `paper_results/replays/musique/scripts/postgate_common_cost_dependence.py` | Replay script | postgate common cost dependence: runs the named audit or sensitivity analysis for MuSiQue. |
| `paper_results/replays/musique/scripts/postgate_cost_sensitivity.py` | Replay script | postgate cost sensitivity: runs the named audit or sensitivity analysis for MuSiQue. |
| `paper_results/replays/musique/scripts/score_action_file.py` | Replay script | score action file: scores action or submission files for MuSiQue. |
| `paper_results/replays/musique/scripts/worthir_policy.py` | Replay script | worthir policy: implements the released routing policy for MuSiQue. |
| `paper_results/replays/musique/spec/ADMISSION_GATE_PREREGISTRATION.md` | Scientific specification | ADMISSION GATE PREREGISTRATION: documents MuSiQue scope, execution, provenance, environment, or frozen analysis decisions. |
| `paper_results/replays/musique/spec/FROZEN_SPEC.json` | Machine-readable specification | FROZEN SPEC: documents MuSiQue scope, execution, provenance, environment, or frozen analysis decisions. |
| `paper_results/replays/musique/spec/LINEAGE_DISCOVERY_REPORT.md` | Scientific specification | LINEAGE DISCOVERY REPORT: documents MuSiQue scope, execution, provenance, environment, or frozen analysis decisions. |
| `paper_results/replays/musique/spec/POSTGATE_COST_DEPENDENCE_AMENDMENT.md` | Scientific specification | POSTGATE COST DEPENDENCE AMENDMENT: documents MuSiQue scope, execution, provenance, environment, or frozen analysis decisions. |

### 任务回放：2Wiki-Structured

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/replays/structured_v2/build_summary.json` | Build record | Records 2Wiki-Structured replay construction counts, checks, and outputs. |
| `paper_results/replays/structured_v2/organizer_private/audit_sources/frozen_fold_assignments.parquet` | Evaluator data | frozen fold assignments: 2Wiki-Structured evaluation membership or grouped folds; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/structured_v2/organizer_private/audit_sources/frozen_oof_query_actions.parquet` | Evaluator data | frozen oof query actions: 2Wiki-Structured frozen policy actions; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/structured_v2/organizer_private/data/outcomes.parquet` | Evaluator data | outcomes: 2Wiki-Structured complete per-query route outcomes; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/structured_v2/organizer_private/data/references.parquet` | Evaluator data | references: 2Wiki-Structured relevance references; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/structured_v2/organizer_private/golden_submissions/frozen_a_oof.json` | Golden submission | frozen a oof: known 2Wiki-Structured actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/structured_v2/organizer_private/golden_submissions/oracle_canary.json` | Evaluator canary | oracle canary: known 2Wiki-Structured actions used to verify scorer behavior; oracle canaries are never deployable policies. |
| `paper_results/replays/structured_v2/organizer_private/manifest.json` | Replay inventory | Lists released 2Wiki-Structured components and provenance metadata. |
| `paper_results/replays/structured_v2/organizer_private/README.md` | Replay guide | Explains the 2Wiki-Structured replay directory, evidence status, entry points, and interpretation. |
| `paper_results/replays/structured_v2/organizer_private/score_submission.py` | Replay script | score submission: scores action or submission files for 2Wiki-Structured. |
| `paper_results/replays/structured_v2/organizer_private/source_provenance.json` | Evaluator record | source provenance: 2Wiki-Structured source lineage; it was unavailable to routing policies when actions were selected. |
| `paper_results/replays/structured_v2/public/contracts/cost_contract.json` | Replay contract | cost contract: defines 2Wiki-Structured cost and utility semantics. |
| `paper_results/replays/structured_v2/public/contracts/legal_state_schema.json` | Replay contract | legal state schema: defines 2Wiki-Structured participant-visible fields and exclusions. |
| `paper_results/replays/structured_v2/public/contracts/route_registry.json` | Replay contract | route registry: defines 2Wiki-Structured available routes and dependencies. |
| `paper_results/replays/structured_v2/public/contracts/submission.schema.json` | Replay contract | submission.schema: defines 2Wiki-Structured accepted action-file structure. |
| `paper_results/replays/structured_v2/public/contracts/task_contract.json` | Replay contract | task contract: defines 2Wiki-Structured task population, metric, route set, and evaluation rules. |
| `paper_results/replays/structured_v2/public/data/legal_action_descriptors.parquet` | Participant data | legal action descriptors: 2Wiki-Structured action rows or action descriptors. |
| `paper_results/replays/structured_v2/public/data/legal_query_state.parquet` | Participant data | legal query state: 2Wiki-Structured inference-time state available to the routing policy. |
| `paper_results/replays/structured_v2/public/data/query_membership.parquet` | Participant data | query membership: 2Wiki-Structured query or split membership. |
| `paper_results/replays/structured_v2/public/manifest.json` | Replay inventory | Lists released 2Wiki-Structured components and provenance metadata. |
| `paper_results/replays/structured_v2/public/README.md` | Replay guide | Explains the 2Wiki-Structured replay directory, evidence status, entry points, and interpretation. |
| `paper_results/replays/structured_v2/public/templates/submission_template.json` | Submission template | submission template: example legal 2Wiki-Structured route-selection file. |
| `paper_results/replays/structured_v2/public/validate_submission.py` | Replay script | validate submission: validates released files for 2Wiki-Structured. |
| `paper_results/replays/structured_v2/README.md` | Replay guide | Explains the 2Wiki-Structured replay directory, evidence status, entry points, and interpretation. |

### 论文复现命令

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/scripts/README.md` | Command guide | Indexes paper reproduction and replay validation commands. |
| `paper_results/scripts/reproduce_paper.py` | Reproduction script | Rebuilds released figures and tables. |
| `paper_results/scripts/reproduce_rqs.py` | Reproduction script | Recomputes RQ2-RQ5 numerical summaries. |
| `paper_results/scripts/validate_results.py` | Validation orchestrator | Runs all released paper-result checks. |
| `paper_results/scripts/verify_released_canonical.py` | Replay validator | Checks the compact canonical TREC-DL replay. |

### 第三方条款

| 路径 | 文件类型 | 用途 |
| --- | --- | --- |
| `paper_results/third_party/2WikiMultiHopQA-LICENSE.txt` | Third-party license | License text for 2WikiMultiHopQA-derived material. |
| `paper_results/third_party/README.md` | Third-party guide | Explains external license material. |
