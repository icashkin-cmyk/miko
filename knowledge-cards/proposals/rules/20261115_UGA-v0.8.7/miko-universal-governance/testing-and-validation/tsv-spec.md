---
doc_id: tsv-spec
name_zh: 測試與驗證
version: 0.8.7
date: 2026-11-14
status: PROPOSED
---

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
