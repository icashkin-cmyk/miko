未驗收提案

# MIKO Capability Ecosystem Architecture

- 中文名稱：MIKO 概念導向能力生態系架構
- stable_id：miko-capability-ecosystem-architecture
- 狀態：CANDIDATE_PROPOSAL
- 正本：MIKO v1.2.72；本資料夾不修改正本
- 目的：把使用者的概念、素材或目標，轉換為可研究、可驗證、可維護、可執行的 MIKO 能力與工作流。
- 審核者：Manus 直接審核；Claude 審核：NOT_RUN（依本輪指示）
- Runtime：UNKNOWN；尚未宣稱已載入、熱插拔或生效

## 1. 核心原則

1. 概念優先：使用者不必先知道 Skill 名稱。
2. 能力先盤點：先確認已擁有、可呼叫、能執行、已驗收的差異。
3. 累積式演進：保留原始版本、來源、授權、diff、測試與回復方式。
4. 吸收不等於複製：外部 Skill 只在授權、來源與安全條件允許時轉化。
5. 資產分類：不是每個概念都升格為 Skill；可形成知識卡、Adapter、Workflow、Reference、Template、Script 或一次性成果。
6. 規劃不等於執行：Orchestrator 不得把計畫、候選或工具成功回應冒充成成品完成。
7. 未驗證不升格：UNKNOWN、NOT_RUN、NOT_READ、BLOCKED 不得轉成 PASS。
8. 正本不覆蓋：本提案只位於候選區，不直接寫入 `skills/`、`VERSION` 或 Runtime 設定。

## 2. 八階段總流程

| 階段 | stable_id | 名稱 | 核心問題 | Gate |
|---|---|---|---|---|
| 0 | baseline-and-scope | 基線與範圍凍結 | 本次到底盤點什麼？ | G0 |
| 1 | capability-inventory | 全域能力目錄 | 現在到底擁有什麼？ | G1 |
| 2 | asset-classification | 資產分類 | 應成為 Skill、知識卡、Adapter 或 Workflow？ | G2 |
| 3 | concept-to-capability | 概念萃取與能力轉化 | 如何把想法變成可設計需求？ | G3 |
| 4 | skill-gap-analysis | 能力缺口分析 | 缺什麼、重複什麼、哪些未驗證？ | G4 |
| 5 | external-skill-intake | 外部方案研究與吸收 | 哪些外部方法可安全吸收？ | G5 |
| 6 | intent-to-execution | 概念到執行編排 | 如何組成可執行工作流？ | G6 |
| 7 | quality-and-e2e-acceptance | 品質與端到端驗收 | 成品是否真的有效？ | G7 |
| 8 | lifecycle-and-recovery | 生命週期與回復 | 如何維護、退役與回復？ | G8 |

階段必須依序通過 Gate；前一階段未 PASS，不得把下一階段標為完成。可建立下一階段的草稿，但狀態只能是 `NOT_READY`。

## 3. 分層責任

- `miko-core`：治理、權限、版本、證據、停止與正式放行。
- `Capability Inventory`：描述能力現況，不負責自行安裝。
- `Concept-to-Capability`：將概念轉成能力需求與資產候選。
- `Skill Gap Analysis`：分析缺口與重複，不負責採用決策。
- `External Skill Intake`：來源、授權、安全與可吸收性審查。
- `Intent-to-Execution`：排序與串接工作流，不提高權限。
- `Router`：依子任務選擇 Skill、工具、來源與格式。
- `Runtime/Adapter`：實際執行與回傳結果。
- `Quality/E2E Acceptance`：測試成品與獨立驗收。
- `Lifecycle`：版本、diff、退役、回復與歷史保存。

## 4. 角色

- `IMPLEMENTER`：建立候選文件、Skill、Adapter 或 Workflow。
- `TESTER`：自行執行正向、負向、邊界、異常、回歸與 Mutation 測試。
- `INDEPENDENT_AUDITOR`：不接受前兩者的 PASS 宣稱，重新讀取與驗證。
- `GOVERNANCE_OWNER`：判斷權限、正式採用、版本與不可逆動作。

## 5. 絕對狀態邊界

`installed`、`callable`、`executable`、`verified`、`adopted`、`runtime_read_back` 必須分開記錄。文件完成、候選建立、靜態驗證通過，均不等於 Runtime 生效。

## 6. 目前驗收狀態

- 附件 17／18 盤點：PASS_WITH_REFINEMENT
- 架構責任分層：PASS_WITH_REFINEMENT
- 外部平台能力：UNKNOWN
- Anthropic 官方功能主張：UNKNOWN
- Stage 1 格式／metadata／觸發契約：PASS_WITH_REFINEMENT（20/20）
- Stage 1 Runtime 實測：UNKNOWN／NOT_RUN
- GitHub 正本採用：NOT_RUN
- 正式採用：NOT_RUN

詳見各階段文件與 `governance/acceptance-policy.md`。
