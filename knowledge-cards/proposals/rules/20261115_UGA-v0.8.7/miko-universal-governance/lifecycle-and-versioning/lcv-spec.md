---
doc_id: lcv-spec
name_zh: 生命週期與版本
version: 0.8.7
date: 2026-11-14
status: PROPOSED
---

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
