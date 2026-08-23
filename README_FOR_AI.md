# WorthIR project map for AI tools

This is the complete navigation and tracked-file audit for the repository.
Use it before searching broadly or changing code. The short root `README.md` is
for human users; this document is deliberately detailed.

## Repository architecture

- The reusable framework is at the repository root: `contracts/`, `docs/`,
  `examples/`, `quickstart/`, `scripts/`, `src/`, and `task_template/`.
- `paper_results/` contains all paper-specific actions, evaluator ledgers,
  analyses, replay packages, figure builders, and reproduction commands.
- `python setup_environment.py` creates the dependency-free framework
  environment and validates it. `worthir.cmd` and `./worthir` are the human
  launchers; `worthir.py` is their platform-neutral command implementation.
- `python paper_results/run.py` creates a paper-local environment and validates
  the released paper results.

## Reusable evaluation flow

1. Run `python setup_environment.py` from the repository root.
2. Use `worthir demo` to verify the complete qrels-to-report path.
3. For a generic task, provide `task.json`, `queries.csv`, `routes.csv`, and
   `outcomes.csv`, then run `worthir build-custom SOURCE TASK`.
4. Run `worthir validate-task TASK` before scoring any policy.
5. Export held-out query-route choices as CSV and run
   `worthir evaluate TASK CHOICES --policy-id ID`.
6. `worthir compare TASK` scores every supplied policy and
   every fixed route and writes Markdown, CSV, and JSON reports.
7. `worthir build-trec` is a convenience adapter for qrels and TREC runs.

## Information boundary and scientific invariants

- Policies may use only information available before the selected route executes.
- Relevance judgments, unselected-route outcomes, utilities, oracle actions, and
  regret are evaluator-only.
- The ledger must contain the complete Cartesian product of queries and routes.
- Route costs are cumulative. A route cannot cost less than any prerequisite.
- Cost availability is part of the information boundary. Fixed costs known at
  commitment are stored on public route entries; query-dependent known costs
  are stored in `participant/route_costs.csv`; post-execution measurements stay
  evaluator-only. `validate-task` reconciles public and evaluator costs.
- Generic sources may provide cumulative cost directly or incremental component
  cost; the builder computes the transitive prerequisite closure once.
- Utility is `effectiveness - lambda * cumulative_cost`. Raw utilities are
  task-specific and must not be compared across tasks.
- Oracle and regret are defined only within the registered route set.
- `organizer_private` files are released for reproduction but were evaluator-only
  when the corresponding policies were selected.

## Public interface and limits

- The generic adapter accepts any named higher-is-better scalar effectiveness
  measure with declared bounds. The TREC adapter computes NDCG@K from qrels and
  six-column run files.
- Constant route costs belong in `routes.csv`; a complete `costs.csv` overrides
  them for query-dependent latency or work.
- The contract exposes only choices that the generic scorer uses. Higher
  effectiveness, a complete route set, nonnegative cumulative cost, and the
  oracle tie break are fixed public invariants rather than ignored switches.
- `comparison.md` is descriptive. The generic tool does not invent uncertainty
  intervals or choose lambda; task owners must supply a valid resampling design
  and a declared cost preference when inferential claims are needed.
- `legal_state.csv` is a documented participant input and is not consumed by the
  evaluator. Information-boundary validity still depends on how policy choices
  were produced.
- Historical paper files may retain names such as `raw_quality` or `menu`; do not
  copy those terms into the reusable public interface.

## Change rules for AI tools

- Keep reusable framework code and dependencies outside `paper_results/`.
- Keep paper-only dependencies inside `paper_results/requirements.txt`.
- Use `effectiveness`, `available routes`, and `route set` in the reusable API.
- Never expose evaluator ledgers to routing-policy code.
- Do not add hashes, checksum files, release manifests, or maintenance narration.
- Preserve released scientific values unless a requested correction has evidence.
- Run `python run.py` after framework changes, and test the one-click setup plus
  `worthir demo` when an entry point or adapter changes.
- After paper-result changes, also run
  `python paper_results/run.py --use-current-python` when dependencies are present.

## Complete tracked-file audit

Every tracked path is listed once. Evaluator data must not become policy input
merely because it is publicly released.

### Root files

| Path | What it is | What it is for |
| --- | --- | --- |
| `LICENSE` | License | MIT license for WorthIR-authored code. |
| `NOTICE` | Third-party notice | Points to the data, model, and software terms that remain outside the MIT license. |
| `pyproject.toml` | Editable install metadata | Provides the `worthir` console command for a checked-out repository. |
| `CITATION.cff` | Citation metadata | Supplies the software release and preferred paper citation to GitHub and citation tools. |
| `README_FOR_AI.md` | AI project map | Explains architecture, invariants, current limits, and the purpose of every tracked file. |
| `README.md` | Human entry point | Gives the one-command setup, complete demo, own-data route, and paper-results boundary. |
| `run.py` | Framework validator | Runs the dependency-free framework validation suite. |
| `setup_environment.py` | Environment setup | Creates `.venv`, exposes `src/` inside it, and runs the framework doctor without downloading packages. |
| `worthir` | POSIX launcher | Bootstraps the local environment when needed and forwards commands to the unified CLI. |
| `worthir.cmd` | Windows launcher | Bootstraps the local environment when needed and forwards commands to the unified CLI. |
| `worthir.py` | Unified CLI | Provides doctor, demo, init, TREC build, action conversion, scoring, and comparison subcommands. |

### Repository configuration

| Path | What it is | What it is for |
| --- | --- | --- |
| `.gitattributes` | Repository configuration | Normalizes text line endings and marks binary research artifacts so Git does not rewrite them. |
| `.github/workflows/validate.yml` | Continuous integration | Validates the framework on Windows, Linux, and macOS and separately reproduces the paper results. |
| `.gitignore` | Repository configuration | Excludes generated outputs, environments, caches, editor state, and build products. |

### Reusable contracts

| Path | What it is | What it is for |
| --- | --- | --- |
| `contracts/quickstart_contract.json` | Task contract | Defines the synthetic task, action schema, metric range, cost preference, and identifiers. |
| `contracts/README.md` | Contract guide | Explains the shared quickstart task contract and route registry. |
| `contracts/route_registry.json` | Route registry | Registers quickstart routes, prerequisites, and fixed commitment-time costs. |

### Reusable documentation

| Path | What it is | What it is for |
| --- | --- | --- |
| `docs/ADAPT_TO_NEW_TASK.md` | Adaptation guide | Defines the generic task tables, route dependencies, cost modes, TREC shortcut, and router workflow. |
| `docs/COST_AND_LAMBDA.md` | Cost guide | Explains cumulative cost choices, normalization, lambda selection, and sensitivity. |
| `docs/OUTPUTS.md` | Output guide | Defines comparison fields, fixed references, Pareto membership, and descriptive scope. |

### End-to-end TREC example

| Path | What it is | What it is for |
| --- | --- | --- |
| `examples/trec_walkthrough/README.md` | Walkthrough guide | Shows the complete qrels-to-report demo and how to add another policy. |
| `examples/trec_walkthrough/source/alternative_choices.csv` | Policy choices | Supplies a second query-route policy for the action-conversion example. |
| `examples/trec_walkthrough/source/policy_choices.csv` | Policy choices | Supplies the default adaptive choices consumed during task construction. |
| `examples/trec_walkthrough/source/qrels.tsv` | TREC qrels | Defines graded relevance for the small walkthrough task. |
| `examples/trec_walkthrough/source/queries.csv` | Participant state | Provides human-readable query text and one legal pre-route feature. |
| `examples/trec_walkthrough/source/routes.csv` | Route definition | Maps route IDs to TREC runs, prerequisites, costs, and the development-selected fixed route. |
| `examples/trec_walkthrough/source/runs/base.trec` | TREC run | Supplies base-route rankings for the walkthrough. |
| `examples/trec_walkthrough/source/runs/prf.trec` | TREC run | Supplies query-expansion rankings for the walkthrough. |
| `examples/trec_walkthrough/source/runs/rerank.trec` | TREC run | Supplies cross-encoder rankings for the walkthrough. |

### Generic non-TREC example

| Path | What it is | What it is for |
| --- | --- | --- |
| `examples/custom_task/README.md` | Generic task guide | Explains the four source files and the cumulative/incremental cost modes. |
| `examples/custom_task/source/task.json` | Task definition | Declares the non-TREC effectiveness measure, cost profile, and fixed reference. |
| `examples/custom_task/source/queries.csv` | Participant state | Supplies only the fields available to the example router. |
| `examples/custom_task/source/routes.csv` | Route definition | Demonstrates a multi-prerequisite route and incremental component costs. |
| `examples/custom_task/source/outcomes.csv` | Evaluator outcomes | Supplies complete answer-coverage and query-dependent cost outcomes. |
| `examples/custom_router/README.md` | Router guide | Shows how to execute and replace the external example router. |
| `examples/custom_router/router.py` | Example router | Reads legal state, routes, lambda, and public query-dependent costs, then writes choices without opening evaluator data. |
| `examples/custom_router/run.py` | Router walkthrough | Builds the generic task, runs the router, binds its choices, and writes the comparison. |

### Synthetic quickstart

| Path | What it is | What it is for |
| --- | --- | --- |
| `quickstart/evaluator/hidden_ledger.csv` | Evaluator data | Complete synthetic effectiveness and cumulative-cost outcomes. |
| `quickstart/evaluator/README.md` | Evaluator guide | Explains why complete query-route outcomes are evaluator-only. |
| `quickstart/participant/example_actions.json` | Action file | Example one-route-per-query decisions bound to the quickstart contract. |
| `quickstart/participant/legal_state.csv` | Participant data | Synthetic inference-time query features. |
| `quickstart/participant/README.md` | Participant guide | Defines the quickstart information available to a routing policy. |
| `quickstart/README.md` | Quickstart guide | Explains the dependency-free six-query example. |

### Reusable commands

| Path | What it is | What it is for |
| --- | --- | --- |
| `scripts/actions_from_csv.py` | Action converter | Validates human-readable query-route choices and writes contract-bound action JSON. |
| `scripts/build_custom_task.py` | Generic task adapter | Builds contracts, participant state, and a complete ledger from generic source tables. |
| `scripts/build_trec_task.py` | TREC adapter | Computes NDCG@K from qrels and runs and builds a complete reusable task. |
| `scripts/compare_policies.py` | Comparison reporter | Scores all supplied policies and fixed routes and writes Markdown, CSV, JSON, and Pareto outputs. |
| `scripts/init_task.py` | Task initializer | Copies the runnable template and replaces task, contract, and registry identifiers. |
| `scripts/README.md` | Command guide | Indexes the reusable framework commands. |
| `scripts/run_integrity_tests.py` | Integrity tests | Checks invalid inputs, arithmetic invariants, cumulative costs, ties, and the example information boundary. |
| `scripts/run_smoke_test.py` | Smoke test | Scores the six-query quickstart and writes aggregate results. |
| `scripts/score_actions.py` | Scoring CLI | Resolves task inputs, invokes the core scorer, and writes aggregate JSON. |
| `scripts/validate_task.py` | Task validator | Reports task coverage, dependency edges, cost availability, and public-to-evaluator cost agreement before scoring. |
| `scripts/validate_framework.py` | Framework validator | Runs smoke, integrity, task initialization, TREC construction, action conversion, and comparison checks. |

### Reusable Python source

| Path | What it is | What it is for |
| --- | --- | --- |
| `src/README.md` | Source guide | Explains the dependency-free source layout. |
| `src/worthir_eval/__init__.py` | Python API | Exports task inspection, scoring, and the public error type. |
| `src/worthir_eval/core.py` | Scoring implementation | Validates dependency graphs, actions, ledgers, cumulative costs, and the public cost boundary, then computes effectiveness, cost, utility, oracle agreement, and regret. |
| `src/worthir_eval/README.md` | Package guide | Summarizes the scorer API and participant-evaluator boundary. |

### New-task template

| Path | What it is | What it is for |
| --- | --- | --- |
| `task_template/.gitignore` | Template configuration | Excludes generated task scores and comparison reports. |
| `task_template/contracts/route_registry.json` | Template route registry | Runnable two-route prerequisite example to replace for a new task. |
| `task_template/contracts/task_contract.json` | Template task contract | Runnable one-query task, metric, cost, and schema example. |
| `task_template/evaluator/ledger.csv` | Template evaluator data | Complete one-query, two-route effectiveness and cost ledger. |
| `task_template/participant/actions.json` | Template action file | One-row example selecting a registered route. |
| `task_template/participant/legal_state.csv` | Template participant data | One-row example of inference-time query state. |
| `task_template/README.md` | Template guide | Explains when to use the manual template instead of the TREC adapter. |

### Paper-results root

| Path | What it is | What it is for |
| --- | --- | --- |
| `paper_results/README.md` | Paper-results entry point | Explains how to reproduce and validate all released paper outputs. |
| `paper_results/PAPER_MAP.md` | Paper result index | Maps each main-paper figure and table to source data, commands, outputs, and reproduction level. |
| `paper_results/requirements.txt` | Dependency specification | Pinned packages used only by paper-result reproduction. |
| `paper_results/run.py` | Paper-results entry point | Creates the paper-local environment and launches released-results validation. |

### Paper documentation

| Path | What it is | What it is for |
| --- | --- | --- |
| `paper_results/docs/DATA_AND_MODEL_TERMS.md` | Data and model terms | Records licenses, access conditions, and use constraints. |
| `paper_results/docs/README.md` | Documentation guide | Indexes paper-result semantics, data terms, and notices. |
| `paper_results/docs/REFERENCE_SEMANTICS.md` | Reference semantics | Defines deployable policies, evaluator-only references, opportunity, and regret. |
| `paper_results/docs/THIRD_PARTY_NOTICES.md` | Third-party notices | Attributes external datasets, models, and software. |

### Full-replay guidance

| Path | What it is | What it is for |
| --- | --- | --- |
| `paper_results/full_replay/CANONICAL_TREC.md` | Full-replay specification | Documents canonical TREC-DL reconstruction. |
| `paper_results/full_replay/FEVER.md` | Full-replay specification | Documents FEVER reconstruction. |
| `paper_results/full_replay/MUSIQUE.md` | Full-replay specification | Documents MuSiQue reconstruction. |
| `paper_results/full_replay/README.md` | Full-replay guide | Explains what is required to rebuild retrieval outputs. |
| `paper_results/full_replay/RESOURCE_REQUIREMENTS.md` | Resource guide | Summarizes software, storage, model, and compute needs. |
| `paper_results/full_replay/STRUCTURED_AND_DIAGNOSTIC.md` | Full-replay specification | Documents structured and diagnostic reconstructions. |

### Paper analyses: overview

| Path | What it is | What it is for |
| --- | --- | --- |
| `paper_results/analyses/README.md` | Analysis guide | Indexes released RQ2-RQ5 analyses and their evidentiary scope. |

### Paper analyses: RQ2

| Path | What it is | What it is for |
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

### Paper analyses: RQ3

| Path | What it is | What it is for |
| --- | --- | --- |
| `paper_results/analyses/rq3_utility_sources/data/query_strata.csv` | Analysis table | query strata: released RQ3 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq3_utility_sources/data/README.md` | Analysis guide | Explains the RQ3 diagnostic data. |
| `paper_results/analyses/rq3_utility_sources/data/top_decile_switching.csv` | Analysis table | top decile switching: released RQ3 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq3_utility_sources/README.md` | Analysis guide | Explains the RQ3 analysis package. |

### Paper analyses: RQ4

| Path | What it is | What it is for |
| --- | --- | --- |
| `paper_results/analyses/rq4_robustness/data/cost_preference_summary.csv` | Analysis table | cost preference summary: released RQ4 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq4_robustness/data/cost_preference_curves.csv` | Figure source | Dense cost-preference curves and marked intervals used to redraw Figure 5. |
| `paper_results/analyses/rq4_robustness/data/fever_candidate_dependence.csv` | Analysis table | fever candidate dependence: released RQ4 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq4_robustness/data/model_and_fold_summary.csv` | Analysis table | model and fold summary: released RQ4 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq4_robustness/data/README.md` | Analysis guide | Explains the RQ4 diagnostic data. |
| `paper_results/analyses/rq4_robustness/data/structured_candidate_recurrence.csv` | Analysis table | structured candidate recurrence: released RQ4 diagnostic result used by the paper analysis. |
| `paper_results/analyses/rq4_robustness/README.md` | Analysis guide | Explains the RQ4 analysis package. |

### Paper analyses: RQ5

| Path | What it is | What it is for |
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

### Paper figures and tables

| Path | What it is | What it is for |
| --- | --- | --- |
| `paper_results/paper_reproduction/figures/cost_quality_inversion_data.csv` | Paper input | cost quality inversion data: compact values consumed by a figure or table builder. |
| `paper_results/paper_reproduction/figures/hero_example_2019.json` | Paper input | hero example 2019: compact values consumed by a figure or table builder. |
| `paper_results/paper_reproduction/figures/make_cost_quality_inversion.py` | Figure builder | make cost quality inversion: recreates a released WorthIR paper figure. |
| `paper_results/paper_reproduction/figures/make_figures_4_7.py` | Figure builder | Redraws the opportunity, sensitivity, reranking-localization, and latency figures from released tables. |
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

### Task replays: overview

| Path | What it is | What it is for |
| --- | --- | --- |
| `paper_results/replays/README.md` | Replay guide | Indexes every task replay and its evidence type. |

### Task replay: TREC-DL

| Path | What it is | What it is for |
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

### Task replay: Dense-standard and legacy

| Path | What it is | What it is for |
| --- | --- | --- |
| `paper_results/replays/dense_and_legacy_recoverability/analysis_results.json` | Replay data | analysis results: Dense-standard and legacy data or derived results used by task-specific validation. |
| `paper_results/replays/dense_and_legacy_recoverability/baseline_semantics_by_split.csv` | Replay data | baseline semantics by split: Dense-standard and legacy data or derived results used by task-specific validation. |
| `paper_results/replays/dense_and_legacy_recoverability/baseline_semantics_summary.csv` | Replay data | baseline semantics summary: Dense-standard and legacy data or derived results used by task-specific validation. |
| `paper_results/replays/dense_and_legacy_recoverability/deployable_ci_hyperlink.json` | Replay data | deployable ci hyperlink: Dense-standard and legacy data or derived results used by task-specific validation. |
| `paper_results/replays/dense_and_legacy_recoverability/deployable_ci_structured.json` | Replay data | deployable ci structured: Dense-standard and legacy data or derived results used by task-specific validation. |
| `paper_results/replays/dense_and_legacy_recoverability/README.md` | Replay guide | Explains the Dense-standard and legacy replay directory, evidence status, entry points, and interpretation. |
| `paper_results/replays/dense_and_legacy_recoverability/recoverability_core.csv` | Replay data | recoverability core: Dense-standard and legacy data or derived results used by task-specific validation. |

### Task replay: FEVER

| Path | What it is | What it is for |
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

### Task replay: FiQA260

| Path | What it is | What it is for |
| --- | --- | --- |
| `paper_results/replays/fiqa260/candidate_pool_fingerprints.parquet` | Replay data | candidate pool fingerprints: FiQA260 data or derived results used by task-specific validation. |
| `paper_results/replays/fiqa260/execution_fingerprints.parquet` | Replay data | execution fingerprints: FiQA260 data or derived results used by task-specific validation. |
| `paper_results/replays/fiqa260/legal_state.parquet` | Replay data | legal state: FiQA260 data or derived results used by task-specific validation. |
| `paper_results/replays/fiqa260/manifest.json` | Replay inventory | Lists released FiQA260 components and provenance metadata. |
| `paper_results/replays/fiqa260/query_membership.parquet` | Replay data | query membership: FiQA260 data or derived results used by task-specific validation. |
| `paper_results/replays/fiqa260/raw_quality_labels.parquet` | Replay data | raw quality labels: FiQA260 data or derived results used by task-specific validation. |
| `paper_results/replays/fiqa260/README.md` | Replay guide | Explains the FiQA260 replay directory, evidence status, entry points, and interpretation. |
| `paper_results/replays/fiqa260/schema.json` | Replay schema | Defines FiQA260 tables, fields, data types, and meanings. |

### Task replay: Hyperlink10k

| Path | What it is | What it is for |
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

### Task replay: MuSiQue

| Path | What it is | What it is for |
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

### Task replay: 2Wiki-Structured

| Path | What it is | What it is for |
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

### Paper reproduction commands

| Path | What it is | What it is for |
| --- | --- | --- |
| `paper_results/scripts/README.md` | Command guide | Indexes paper reproduction and replay validation commands. |
| `paper_results/scripts/reproduce_paper.py` | Reproduction script | Rebuilds released figures and tables. |
| `paper_results/scripts/reproduce_rqs.py` | Reproduction script | Recomputes RQ2-RQ5 numerical summaries. |
| `paper_results/scripts/validate_results.py` | Validation orchestrator | Runs all released paper-result checks. |
| `paper_results/scripts/verify_released_canonical.py` | Replay validator | Checks the compact canonical TREC-DL replay. |

### Third-party terms

| Path | What it is | What it is for |
| --- | --- | --- |
| `paper_results/third_party/2WikiMultiHopQA-LICENSE.txt` | Third-party license | License text for 2WikiMultiHopQA-derived material. |
| `paper_results/third_party/README.md` | Third-party guide | Explains external license material. |
