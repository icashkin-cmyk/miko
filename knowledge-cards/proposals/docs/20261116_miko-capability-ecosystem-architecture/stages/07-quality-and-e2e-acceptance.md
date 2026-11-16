未驗收提案

# Stage 7｜品質與端到端驗收

- 目的：證明實際成品符合需求，而不是只證明文件、Skill 或工具存在。
- 輸入：Workflow Plan、實際輸出、測試案例、Acceptance Criteria、來源與版本證據。
- 輸出：正向、負向、邊界、異常、回歸、Mutation、E2E 與獨立驗收報告。
- 前置條件：G6 PASS；所有執行命令與目標檔案可重放。
- 操作要求：保存完整命令、stdout、stderr、Exit Code、環境、時間、Commit、SHA-256 與差異。
- 禁止事項：不得以預期輸出冒充實際輸出；不得把 SKIP 當 PASS；不得把自驗冒充獨立驗收。
- 檢查點：測試是否能抓到預期錯誤；Mutation 是否被測試拒絕；遠端讀回是否一致。
- Acceptance Criteria：所有必要 AC PASS；無 UNKNOWN／NOT_RUN／BLOCKED 被升格；獨立驗收完成。
- Failure Handling：FAIL 回到一個修正目標；證據不足標 UNKNOWN 或 NOT_RUN；不交付。
- Recovery：修正候選、保存 diff、重跑受影響測試與完整回歸。
- Regression Test：既有功能、舊輸出格式、舊限制、失敗出口與版本回復均需重測。
- 閉環條件：自驗後獨立驗收 PASS，G7 PASS 才可交付候選。
- 負責角色：TESTER；INDEPENDENT_AUDITOR 判定；IMPLEMENTER 修正。
- 證據與保存：`evidence/stage-07/` 三角色分離證據。
