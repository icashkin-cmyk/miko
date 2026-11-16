未驗收提案

# Stage 5｜External Skill Intake 外部方案研究與吸收

- 目的：研究外部 Skill、工具、API、MCP 或原始碼，萃取可重用方法並安全轉化為 MIKO 資產。
- 輸入：Gap Matrix、候選來源、repository、commit/tag、License、原始文件與測試。
- 輸出：Source Review、License/Security Review、Knowledge Extraction、採用／不採用決策、候選差異。
- 前置條件：G4 PASS。
- 操作要求：完整讀取目的、觸發、不適用、步驟、I/O、依賴、錯誤處理、測試、授權與限制。
- 禁止事項：不得只看名稱或摘要；不得抹除來源；不得複製未授權程式；不得執行不可信腳本；不得把研究成果標成已安裝。
- 檢查點：是否檢查網路、憑證、檔案操作、提示注入、未公開 API 與供應鏈風險。
- Acceptance Criteria：每項吸收內容有來源、版本、授權、差異、理由與測試計畫。
- Failure Handling：License UNKNOWN、來源無法讀取或安全未完成時 BLOCKED／NOT_READ，不進入採用。
- Recovery：改用權威替代來源或等待授權；保留失敗紀錄。
- Regression Test：移除 License、改變 commit、注入外部命令或提示注入，均應被拒絕或降級。
- 閉環條件：候選資產可追溯且不冒充來源原作，G5 PASS。
- 負責角色：IMPLEMENTER／TESTER／INDEPENDENT_AUDITOR／GOVERNANCE_OWNER。
- 證據與保存：Source Review、License、SHA-256、diff、拒絕清單與執行日誌。
