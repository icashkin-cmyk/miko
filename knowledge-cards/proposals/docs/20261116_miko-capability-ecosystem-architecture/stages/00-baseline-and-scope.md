未驗收提案

# Stage 0｜基線與範圍凍結

- 目的：凍結本批次的來源、清單、總數、範圍與不做事項，防止漏項或中途擴張。
- 輸入：MIKO 正本版本、附件 17／18、既有 Skill 清單、既有候選區、使用者目標。
- 輸出：Scope Record、完整清單、總數、來源快照、風險與不做清單。
- 前置條件：已讀取 miko-core 與唯一狀態來源；權威版本可核對。
- 操作要求：記錄 repo、branch、commit、檔案清單、SHA-256、讀取時間與 NOT_READ 項目。
- 禁止事項：不得把可見檔案子集稱為全部；不得中途靜默增加範圍；不得修改正本。
- 檢查點：清單是否可重放；總數是否可計算；每個項目是否有唯一 ID。
- Acceptance Criteria：100% 納入項目有 ID、來源、狀態與責任；未讀來源明確標 NOT_READ。
- Failure Handling：清單不完整則 BLOCKED，停止後續依賴階段。
- Recovery：重新讀取唯一來源，產生新基線，不覆寫舊基線。
- Regression Test：刪除一個清單項目、加入重複 ID、改變基準 commit，檢查是否被拒絕。
- 閉環條件：Scope Record 已保存、讀回一致、G0 PASS。
- 負責角色：IMPLEMENTER 建立；TESTER 重算；INDEPENDENT_AUDITOR 冷讀。
- 證據與保存：`evidence/stage-00/` 保存命令、輸出、manifest、hash 與差異。
