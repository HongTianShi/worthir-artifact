# TREC-DL 回放

- `public/`：动作时状态、契约、路线注册表和参照动作。
- `organizer_private/`：动作冻结后由评测器使用的精简路线结果。

运行 `score_actions.py` 评估参照动作文件。

策略只能使用公共接口。评测 ledger 随已完成任务一同发布以支持复现，但仍不能作为
策略输入。

软件包不包含 MS MARCO 开发表、原始 TREC qrels、完整路线排名或详细候选审计；
汇总评分不需要这些内容。见 `public/docs/DATA_ACCESS_NOTICE.md` 和
`../../full_replay/CANONICAL_TREC.md`。
