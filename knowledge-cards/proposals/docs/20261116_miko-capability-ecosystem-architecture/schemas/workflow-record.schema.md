未驗收提案

# Workflow Record Schema

每個工作流至少包含：

| 欄位 | 要求 |
|---|---|
| workflow_id | 穩定英文識別名 |
| objective | 可驗收的工作目標 |
| source_concept_id | 來源 Concept ID |
| nodes | 子任務、輸入、輸出與責任角色 |
| edges | 資料交接與依賴關係 |
| routing | Skill、工具、來源與格式選擇 |
| authorization | 每個外部寫入或高風險操作的授權狀態 |
| checkpoints | 可逆保存點與回復目標 |
| termination | 成功、失敗、BLOCKED、停滯與最大迭代條件 |
| acceptance_criteria | 成品與測試驗收條件 |
| execution_state | PLANNED／CANDIDATE／AUTHORIZED／EXECUTED／VERIFIED／DELIVERED |
| evidence | 命令、輸出、時間、Commit、SHA-256 |
