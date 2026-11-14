# MIKO Universal Governance Architecture — 候選規格執行報告（v0.2.2）

- 日期：2026-11-14（Asia/Taipei）
- 狀態：`PROPOSED`（未採用、未寫入 GitHub、未 Runtime 生效）
- 治理核心：`CORE_NOT_READ`（本環境未載入 miko-core；正本 `NOT_READ`）
- 最終候選：v0.2.2（經 3 輪修正、1 輪修正驗證、1 輪最終驗證）

## 1. 執行結論

已在候選層完成 A：通用製作流程（14 步 × 14 欄）、UAC 十六章、USC 九契約／四節／七欄、三層分層、路由／生命週期／測試模組、GitHub 結構、命名、README 模板、責任矩陣、驗收矩陣與 11 個背景檢查器。Claude API 共 4 輪互動（round1 審查 10 項、round2 審查 7 項、round3 修正驗證 6 FIXED＋1 PARTIAL＋2 新項、round4 最終驗證 PASS）。背景測試 10/10 檢查器 PASS、負向回歸 10/10 PASS、MANIFEST 41/41 OK。

未完成／未驗證：行為層 20 條 AC 未由 L1 以上驗收者實跑；Runtime 熱插拔與 Claude Code／Manus／GitHub 支援皆 `UNKNOWN`；未寫入 GitHub。

## 2. Claude API 衝突檢查結果

| 輪次 | 模型 | 問題數 | 最高嚴重度 | 判定 |
|---|---|---|---|---|
| round1 | claude-opus-4-5-20251101 | 10（F-01～F-10） | P0（UAC→UCP 循環） | PASS_WITH_FIXES |
| round2 | claude-opus-4-5-20251101 | 7（F-01～F-07） | P1（RSL 路由表不可讀未定義） | PASS_WITH_FIXES |
| round3 | claude-opus-4-5-20251101（Sonnet 4.6 端點無回應後改） | 7 驗證＋2 新項 | P2 | PASS_WITH_FIXES |
| round4 | claude-opus-4-5-20251101 | 2 驗證 | — | PASS |

## 3. 修正前後差異

- v0.1 → v0.2：移除 UAC→UCP run-time 邊（F-01）；新增獨立性等級 L0～L3、驗收包、冷啟動（F-02、F-03）；adapter 標 PLACEHOLDER（F-04、F-05）；UAC 第 2、13 章補欄位（F-06、F-07）；預算計數與終止證明（F-08、F-09）；BR-05 欄位名稱以 UAC 為準（F-10）。
- v0.2 → v0.2.1：證據拆 `evidence_text`／`evidence_source_id`（F-01）；流程圖省略條件（F-02）；冷啟動定義（F-03）；RSL 不可讀 → `NOT_READ`（F-04）；`related_docs` 格式（F-05）；USC 失敗欄涵蓋缺資料（F-06）；R-04 改 `CONFLICT`（F-07）。
- v0.2.1 → v0.2.2：contract.yaml 第 1 章欄位補齊（N-01）；裁決理由記錄位置 `route_decision_reason`／`decided_by`（N-02）。
- diff 檔：`evidence/diff/v0.1_to_v0.2.patch`（1267 行）、`v0.2_to_v0.2.1.patch`（843 行）、`v0.2.1_to_v0.2.2.patch`（136 行）、`v0.1_to_v0.2.2.patch`（1937 行）。

## 4. 背景測試結果

| 檢查器 | v0.2 | v0.2.1 | v0.2.2 |
|---|---|---|---|
| TSV-FMT | PASS | PASS | PASS |
| TSV-STRUCT | PASS | PASS | PASS |
| TSV-CONTRACT | PASS | PASS | PASS |
| TSV-SKILL | PASS | PASS | PASS |
| TSV-OVERLAP | PASS | PASS | PASS |
| TSV-ROUTE | PASS | PASS | PASS |
| TSV-DAG | PASS | PASS | PASS |
| TSV-EXIT | PASS | PASS | PASS |
| TSV-REG | PASS | PASS | PASS |
| TSV-RUNTIME | PASS | PASS | PASS |
| TSV-REGRESSION | PASS | PASS | PASS（10/10 負向注入） |

MANIFEST：`sha256sum -c` 41/41 OK。

## 5. 未驗證事項

1. Runtime 熱插拔（無 H-04 三項證據）。
2. Claude Code／Manus／GitHub adapter 實際整合。
3. 20 條行為層 AC（`NOT_RUN`）。
4. miko-core 正本版本與 A0／W1～W7／A3 對齊（`NOT_READ`）。
5. 預算數值 3／2 是否為正式值（`PENDING_DECISION`）。

## 6. 困難卡

| ID | 現象 | 證據 | 類別 | 影響 AC | 解除條件 | 負責方 | 首次發現 |
|---|---|---|---|---|---|---|---|
| K-01 | miko-core 未載入 | 本機 skills 無 miko-core | 缺資料 | AC-A00-03、AC-A12-01 | 提供 miko-core 或 GitHub 連接器 | MIKO | 2026-11-14 15:52 |
| K-02 | Sonnet 4.6 審查端點無回應 | round3.log 連線中斷 | 缺資料 | 跨模型交叉驗證 | 換模型或稍後重試 | Manus／API | 2026-11-14 16:05 |
| K-03 | 20 條行為層 AC 未實跑 | acceptance-matrix NOT_RUN | 缺授權 | AC-A08、A11、A12 | 指派 L1 以上驗收者 | MIKO／R-CONV | 2026-11-14 16:00 |
| K-04 | Runtime 能力未知 | adapters PLACEHOLDER | 缺資料 | LCV H-04 | 三項實測證據 | 執行環境 | 2026-11-14 15:57 |
| K-05 | 正本 VERSION 未讀 | 無 miko-core/VERSION | 缺資料 | 版本對齊 | 讀取正本 | MIKO | 2026-11-14 15:52 |

## 7. 任務四態

完成但有疑慮。

## 8. 聲明

尚未寫入 GitHub、尚未正式採用、尚未 Runtime 生效。本報告與候選文件皆為 `PROPOSED`。

## 9. A12 獨立驗收複核與修正（v0.2.4）

檢視對象：L0～L3 獨立性等級與驗收包封裝。發現 9 項缺口（G1～G9），已全部補強；Claude 複核再提 4 項（A-01 P1、A-02～A-04 P2），亦已修正。

| 缺口 | 嚴重度 | 修正 |
|---|---|---|
| G1 等級只有一句定義，無可驗證條件 | P1 | 新增 §2.1 判定表（條件、必要證據、最高結果、`adoption_support`） |
| G2 等級與採用權限未對應 | P1 | L1 `adoption_support=NO`；L2／L3 為 YES（仍需 R-CONV） |
| G3 驗收包只有負面清單 | P1 | 附錄 A：正面清單、封裝、`sha256sum -c` 驗證、排除清單 |
| G4 接觸作者只要求記錄 | P2 | L-02：接觸即降 L0、換人、計入 `audit_round` |
| G5 報告無固定欄位 | P2 | 附錄 A.4：11 欄（含 `manifest_check`、`audit_round`、`reviewer_split`） |
| G6 包被竄改無處理 | P2 | 附錄 A.5：報告作廢、重新封裝、`audit_round+1` |
| G7 無多驗收者與利益衝突規則 | P2 | L-03、L-04：取最低等級與最嚴格判定，不得多數決 |
| G8 RT-A12 只有 2 題 | P3 | 擴為 5 題（缺欄位、L0、竄改、接觸作者、PASS 誤標 ADOPTED） |
| G9 PASS 與 ADOPTED 銜接不清 | P3 | AC-A12-06：未經 R-CONV 不得標 `ADOPTED`／`EFFECTIVE` |

測試：TSV-AUDIT 新增並通過；負向回歸 R-11～R-14 全數抓到注入錯誤（14/14 PASS）；MANIFEST 41/41 OK。diff：`v0.2.2_to_v0.2.4.patch`（298 行）、`v0.2.3_to_v0.2.4.patch`（157 行）。

仍未驗證：驗收包工具尚未實作（目前只有規格與規格檢查器，未產生真實包）；L3 是否為正本採用必要條件仍為 `PENDING_DECISION`。

## 10. 修正帳本（v0.3.0）

依使用者要求新增常駐記憶模組：開工依序載入治理、錯誤帳、否決帳；三類事件（錯誤、否決、修改）就地寫入、以去重鍵合併、不刪只標取代；變更帳對應 diff 與證據；正文採文本純度規則，測試輸出只放證據目錄。

整合點：UCP A00 載入、A10 寫入、A13 封裝；新增 AC-A00-04、AC-A10-04、AC-A13-04（總 AC 48）；UAC §1 增文本純度；RSL-R10 路由；TSV-LEDGER 檢查器。

測試：12 個檢查器全 PASS；負向回歸 16/16 PASS（R-15 帳本檔名、R-16 載入 AC）；MANIFEST 44/44 OK；diff 358 行。

未驗證：載入器與寫入器尚未實作，熱插拔介面未實測（UNKNOWN）。

## 11. 審查意見處理（v0.4.0）

| 意見 | 處理 | 狀態 |
|---|---|---|
| P0 版本不一致 | 建置腳本改為讀取候選版本；新增 TSV-VERSION 檢查器；全倉庫 VERSION 與 front matter 對齊 0.4.0 | 完成，PASS |
| P0 驗收包工具 | 實作 build_packet.py（建包、去識別 diff、MANIFEST、驗證），已產生 audit-packet 並通過 sha256sum -c | 完成 |
| P1 行為層 AC | 實作 behavior_checks.py 半自動檢查，12 項中 7 項 PASS、5 項 NOT_RUN（需 L1 以上驗收者） | 部分完成 |
| P1 核心對齊 | 讀取 miko-core v1.73（正本 1.2.72），產出 alignment-report；USC 四節與正本不一致列為 P1 | 完成報告，未修正 |
| P1 Adapter | 維持 UNKNOWN，未實作 H-04 三項證據 | 未做 |
| P2 預算與 L3 | 需 R-CONV 裁決，未代決 | 待決 |
| 中長期 輕量路徑 | 新增附錄 C LITE 與 AC-A00-05 | 完成設計 |
| 載入與寫入 | 實作 ledger.py（init/load/write/snapshot/verify），去重合併已驗證 | 完成 |

測試：12 個檢查器 PASS、18 題回歸 PASS、版本檢查 PASS、驗收包 18 檔 PASS。
