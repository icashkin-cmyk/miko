# 批次 4 移出本輪的轉交項目

## 狀態

- `PROPOSED`
- `NOT_ADOPTED`
- `HISTORICAL_NOT_RUNTIME`
- `OUT_OF_BATCH4_CANDIDATE_SCOPE`

本目錄保留原候選文件作為責任轉交與歷史審查材料，不代表它們仍是批次 4 可進入工程驗證的候選 Skill。不得直接搬入正式 `skills/`、Runtime 或帳號卡。

## 轉交項目

### 07 `photo-inspection-log`

責任應轉回照片／文件專案的 writer 與治理者。原因是其 xlsx／PDF 交付、照片與列對應、工作檔 round-trip、公司交付與外部寫入邊界，不屬本批次共用契約的直接放行範圍。

本輪只保留原文件，不執行真實照片、Excel、PDF、公司交付或外部寫入驗證。

### 09 `tw-backtest-workflow`

維持 `PAUSED_BY_USER`。C6／C9 例外僅指固定唯讀引擎回歸，不授權本批次規劃或修改回測引擎。

`backtest_contract.py`、`preflight_fixed_regression.py`、PIT／look-ahead、事件旗標、成本、基準與 28 欄適用性等工程內容，應轉回 DGHP 臺股專案 writer 與專責治理流程；本 PR 不採用、不接線、不執行。

## 後續條件

任何重新納入都必須由對應 writer、總召或 MIKO 另行指定範圍、責任方、版本基線、測題與獨立稽核，不因本轉交檔存在而自動恢復路由或解除停止。
