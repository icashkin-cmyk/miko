未驗收提案

# Stage 4｜Skill Gap Analysis 能力缺口分析

- 目的：判斷現有能力是否足夠、哪些缺少、哪些重複、哪些只是未驗證。
- 輸入：Concept Record、Capability Inventory、Asset Classification。
- 輸出：Gap Matrix、重複矩陣、候選解法排序與不採用理由。
- 前置條件：G3 PASS。
- 操作要求：先檢查既有能力能否組合，再考慮新增或吸收外部方案。
- 禁止事項：不得把未驗證能力當缺口補裝；不得因名稱不同就判定能力不同。
- 檢查點：是否區分 missing、duplicate、unverified、blocked、out-of-scope。
- Acceptance Criteria：每個需求有現有能力、缺口狀態、候選處理方式與驗收條件。
- Failure Handling：Inventory 不足則 BLOCKED；資料衝突則 CONFLICT，不自行取較新或較完整者。
- Recovery：更新 Inventory 或補做能力測試，保留原分析。
- Regression Test：移除一個既有能力、改變其版本或輸出契約，Gap Matrix 必須變化。
- 閉環條件：所有缺口均有狀態與下一步，G4 PASS。
- 負責角色：IMPLEMENTER／TESTER／INDEPENDENT_AUDITOR。
- 證據與保存：Gap Matrix、dependency graph、反例輸出。
