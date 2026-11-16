未驗收提案

# Stage 8｜生命週期與回復

- 目的：保留歷史、管理版本、維護差異、執行退役與可逆回復。
- 輸入：已驗收候選、原始快照、diff、版本 ledger、測試證據與採用裁決。
- 輸出：版本沿革、目前使用版、候選版、歷史版、退役紀錄、回復目標。
- 前置條件：G7 PASS；每個候選都有完整 manifest 與 hash。
- 操作要求：採累積式演進；記錄繼承、強化、新增、修正、重構與廢止；保留原始內容。
- 禁止事項：不得直接覆寫歷史；不得無理由刪除功能、限制、測試或來源；不得把最新候選當正式版。
- 檢查點：回復目標是否可用；版本與 hash 是否一致；退役是否有授權與影響分析。
- Acceptance Criteria：歷史版本可讀、差異可重放、回復可執行、正式採用與 Runtime 讀回分離。
- Failure Handling：hash 不符標 CONFLICT；回復不可用則 BLOCKED，不執行退役。
- Recovery：回復至最後已驗收版本，保存失敗與新差異。
- Regression Test：刪除快照、改 hash、移除 rollback target、把 candidate 改 adopted，均應被拒絕。
- 閉環條件：版本 ledger、archive、rollback 與狀態讀回一致，G8 PASS。
- 負責角色：GOVERNANCE_OWNER／TESTER／INDEPENDENT_AUDITOR。
- 證據與保存：version ledger、MANIFEST、SHA-256、archive metadata、rollback log。
