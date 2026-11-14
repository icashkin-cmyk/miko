---
doc_id: modules-spec
name_en: Cross-cutting Modules (Routing, Lifecycle, Testing)
name_zh: 橫向模組規格（路由、生命週期、測試）
module: routing-and-selection|lifecycle-and-versioning|testing-and-validation
version: 0.8.7
date: 2026-11-14
status: PROPOSED
supersedes: 0.1.0
amends: 0.8.7
---

# 橫向模組規格 v0.8.7

## RSL：路由與選擇（routing-and-selection）

### 1 目的與範圍

把「產物類型」映射到「契約＋流程＋驗收器」。範圍：路由表、判定規則、衝突裁決。非範圍：流程步驟內容（UCP）、欄位（UAC／USC）。

### 2 路由表

| route_id | 產物類型 | 契約 | 主要驗收器 | 備註 |
|---|---|---|---|---|
| RSL-R01 | Skill | USC | TSV-SKILL + TSV-CONTRACT | 九契約、四節、七欄 |
| RSL-R02 | Skill 規格書 | UAC | TSV-CONTRACT | 十六章 |
| RSL-R03 | 架構書 | UAC | TSV-CONTRACT + TSV-DAG | 需依賴圖 |
| RSL-R04 | 流程設計書 | UAC | TSV-CONTRACT + TSV-DAG | 流程須可追溯 |
| RSL-R05 | 治理規則 | UAC | TSV-CONTRACT + TSV-OVERLAP | 不得與 A0／W1～W7 重複擁有 |
| RSL-R06 | 路由器文件 | UAC | TSV-CONTRACT + TSV-ROUTE | 每條路由可判定 |
| RSL-R07 | 測試規格 | UAC | TSV-CONTRACT + TSV-EXIT | 每條 AC 有測題 |
| RSL-R08 | 文件整合與升級 | UAC | TSV-CONTRACT + TSV-REG + TSV-REGRESSION | 需 diff 與版本對照 |
| RSL-R09 | Adapter 介面文件 | UAC | TSV-CONTRACT + TSV-RUNTIME | Runtime 狀態須為 `UNKNOWN` 或附證據 |
| RSL-R10 | 修正帳本文件 | UAC | TSV-CONTRACT + TSV-LEDGER | 三帳、載入順序、去重與熱插拔介面齊全 |

### 3 判定規則

R-01 一個產物只命中一條 `route_id`；R-02 多產物逐個判定；R-03 無法判定標 `UNKNOWN` 交 R-CONV；R-04 命中兩條即判 `CONFLICT`，不得自行擇一，交 R-CONV 裁決；裁決理由固定寫入 `evidence/<task_id>/routing.json` 的 `route_decision_reason` 與 `decided_by` 兩欄，未填即視為未裁決（修正 F-07、N-02）；R-05 同一任務內所有路由必須存在於本表。

### 4 失敗處理

路由表無此類型 → `UNKNOWN`；兩條互斥 → `CONFLICT`。

### 5 驗收條件

`AC-RSL-01` 八種以上產物類型皆有路由；`AC-RSL-02` 每條路由有契約與驗收器；`AC-RSL-03` 無循環路由；`AC-RSL-04` 路由 ID 唯一。

## LCV：生命週期與版本（lifecycle-and-versioning）

### 1 目的與範圍

規定版本號、日期時間、commit、SHA-256、快照、退役與熱插拔宣告。非範圍：流程步驟、欄位內容。

### 2 版本規則

V-01 採 SemVer 2.0.0；V-02 MAJOR＝欄位或契約不相容；V-03 MINOR＝新增欄位／步驟且向後相容；V-04 PATCH＝文字修正；V-05 每版本必須有 `version`、`date`、`commit`、`sha256`；V-06 未提交時 `commit: NOT_COMMITTED`。

### 3 狀態與升格

| 狀態 | 意義 | 可升格至 | 升格條件 |
|---|---|---|---|
| `PROPOSED` | 候選 | `ADOPTED` | `AUDIT_PASS`＋R-CONV 裁決 |
| `ADOPTED` | 已採用 | `EFFECTIVE` | Runtime 實測證據 |
| `EFFECTIVE` | 已生效 | `DEPRECATED` | 新版取代且遷移完成 |
| `DEPRECATED` | 停用中 | `RETIRED` | ADR＋快照＋redirect |
| `RETIRED` | 退役 | 不可逆 | — |

### 4 退役規則

RT-01 退役需 ADR；RT-02 退役前必須保存快照；RT-03 退役後保留 redirect 表；RT-04 不得刪除歷史快照；RT-05 退役文件不得再被路由為現行正本。

### 5 熱插拔宣告（定義與邊界）

H-00 熱插拔定義：在不改變契約版本的前提下，於執行期替換實作（adapter／skill 實作），且具備介面相容檢查、狀態交接與回滾。

H-01 文件可宣告 adapter 介面；H-02 未經 Runtime 實測一律 `UNKNOWN`；H-03 文件不得寫成「已支援熱插拔」；H-04 熱插拔需三項證據：介面版本相容測試、替換後行為測試、回滾測試；H-05 缺任一證據即維持 `UNKNOWN`。

## TSV：測試與驗證（testing-and-validation）

### 1 目的與範圍

定義十三個檢查器與測試集：格式、結構、契約、責任重疊、路由完整性、依賴循環、失敗出口、回復與版本、Runtime 聲明、回歸。

### 2 檢查器清單

| checker_id | 檢查 | 失敗狀態 |
|---|---|---|
| TSV-FMT | 格式（日期、時間、標題層級、禁用詞） | `SELF_FAIL` |
| TSV-STRUCT | 結構（十六章／四節／十三欄，回歸為例外） | `SELF_FAIL` |
| TSV-CONTRACT | 契約欄位齊全 | `SELF_FAIL` |
| TSV-SKILL | 九契約、四節、七欄 | `SELF_FAIL` |
| TSV-OVERLAP | 責任重疊（單一擁有者） | `CONFLICT` |
| TSV-ROUTE | 路由完整性 | `SELF_FAIL` |
| TSV-DAG | 依賴循環（build-time 與 run-time 兩張圖） | `CONFLICT` |
| TSV-EXIT | 失敗出口與重試上限 | `SELF_FAIL` |
| TSV-REG | 回復與版本 | `SELF_FAIL` |
| TSV-RUNTIME | Runtime 聲明（不得無證據宣稱已支援） | `SELF_FAIL` |
| TSV-AUDIT | 驗收包與獨立性（附錄 A、§2.1） | `SELF_FAIL` |
| TSV-LEDGER | 修正帳本（三帳、載入順序、去重、文本純度） | `SELF_FAIL` |
| TSV-REGRESSION | 回歸集 | `SELF_FAIL` |

### 3 門檻

T-01 全部檢查 `PASS` 才可交付；T-02 `NOT_RUN` 視為未通過；T-03 重測上限 3 輪、重驗上限 2 輪；T-04 任一檢查 `FAIL` 即不得進 A12。

### 4 驗收條件

`AC-TSV-01` 十三個檢查器皆可執行；`AC-TSV-02` 結果可重現；`AC-TSV-03` 失敗有出口；`AC-TSV-04` 結果輸出機器可讀。
