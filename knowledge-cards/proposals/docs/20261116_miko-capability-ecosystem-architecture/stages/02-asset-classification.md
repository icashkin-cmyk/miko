未驗收提案

# Stage 2｜資產分類

- 目的：判斷成果應成為 Skill、知識卡、Adapter、Workflow、Reference、Template、Script 或一次性成果。
- 輸入：Capability Inventory、Concept Record、輸入輸出與重複性分析。
- 輸出：Asset Classification Record、分類理由、責任邊界與保存位置。
- 前置條件：G1 PASS。
- 操作要求：以可重複性、觸發穩定性、資料契約、工具依賴、維護成本及權限風險判斷。
- 禁止事項：不得因為概念重要就自動升格 Skill；不得以分類取代驗收。
- 檢查點：分類是否有反例；是否存在更小資產；是否與既有 Skill 重疊。
- Acceptance Criteria：每個候選只有一個主分類，必要時列備選分類與轉換條件。
- Failure Handling：分類衝突標 CONFLICT，交 GOVERNANCE_OWNER，不自行裁決。
- Recovery：補做案例與責任矩陣，產生新分類版本。
- Regression Test：同一能力在短期一次性與長期重複情境下，分類器應產生可解釋差異。
- 閉環條件：分類、理由、保存方式與責任均已記錄，G2 PASS。
- 負責角色：IMPLEMENTER 提案；GOVERNANCE_OWNER 裁決；INDEPENDENT_AUDITOR 驗證。
- 證據與保存：`schemas/asset-record.schema.md`、分類矩陣與 evidence。
