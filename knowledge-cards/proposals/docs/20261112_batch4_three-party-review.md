未驗收提案

# 批次 4 三方審查與共識狀態（W2 退回修訂版）

## 1. 基線與範圍

- 目前正本：`miko-core v1.71`／`VERSION 1.2.70`。
- 歷史設計基線：`VERSION 1.2.58`／`ADR-081`／`HEAD 6db897bbf87ffab9ade1ffd8018ece83036041b6`；只作 `HISTORICAL_NOT_RUNTIME` 證據。
- 本輪候選：01～06、08、10，共 8 份。
- 責任轉交：07 `photo-inspection-log`、09 `tw-backtest-workflow`，位於 `handoff/20261112_batch4-out-of-scope/`，不再列入本輪候選。
- PR #44 只供治理審閱；不合併、不修改正式 Skill、不接 Runtime。

## 2. W2 審查後狀態

| 角色／項目 | 最新結果 | 限制 |
|---|---|---|
| 總召 PR #44 審查 | `REJECTED_AS_CURRENT_CANDIDATE／NEEDS_REVISION` | 已發現 C3 FAIL、Schema 重複、狀態混軸與 07／09 越界；本檔不替 MIKO 完成正式放行。 |
| Gemini 3.5 Flash-Lite | `ADVICE_ONLY／UNVERIFIED` | 建議內容合理但原始輸出未入庫；不得視為正式審查或共識。 |
| Claude Sonnet 4.6 | `PRE_W2_SUMMARY_ONLY／UNVERIFIED` | 只看修改前摘要，未涵蓋 W2 修訂；不得宣稱最新稿 PASS。 |
| Manus | `REVISION_IN_PROGRESS` | 只修改 PR 候選層；不改正式路徑。 |
| independent-audit | `NOT_RUN` | 須待總召複審後另行排程，不能由模型或自我檢查取代。 |

## 3. W2 已要求並正在套用的修訂

1. 將索引中的本機絕對路徑改為 repo 相對路徑，修復 C3。
2. 補 `20261112_batch4-contract-comparison.md`，對照 miko-core 既有任務四態、困難卡、`OPERATION_ID`、證據標籤與 FINAL_HANDOFF 19 欄。
3. 將證據軸、任務軸、路由／停止軸、授權軸與採用／產物軸分開；不再把 `PAUSED_BY_USER` 與 `PASS` 放在同一狀態軸。
4. validator 加入移除 `NOT_ADOPTED`、`allow_blind_retry=true` 與第五任務態的負向測試。
5. 07 移至照片／文件專案責任轉交；09 移至 DGHP 臺股專案責任轉交並維持 `PAUSED_BY_USER`。
6. 重新執行 `check_repo.py --skip-backtest` 與候選 validator；CI 綠燈仍待本輪提交後確認。

## 4. 不能在本輪宣稱的內容

- Schema 不是 miko-core 新正式契約；目前是 `PROPOSED_ONLY`。
- `idempotency_key` 只是候選擴充，必須與既有 `OPERATION_ID` 映射，不能成為第二個操作身份。
- `retry_policy` 仍需遵循 `STOP`／`READBACK_ONLY` 的候選語意；不能用 `max_attempts` 包裝 blind retry。
- validator PASS 只證明檔案／候選層規則，不能證明 Runtime 行為、外部服務、真實資料或 independent audit。
- Gemini、Claude 自述與 Manus 摘要沒有原始輸出、模型輸出編號與輸入摘要 SHA，因此目前均是未驗證材料。

## 5. `tw-backtest-workflow` 特別處理

- 維持 `PAUSED_BY_USER`。
- C6／C9 例外僅表示固定唯讀引擎回歸，不表示策略有效、投資建議、績效結果或交易授權。
- `backtest_contract.py`、`preflight_fixed_regression.py`、事件旗標、PIT／look-ahead、成本、基準與 28 欄適用性移出本輪，由 DGHP 臺股專案 writer 另行處理。
- 本 PR 不接線、不執行、不恢復一般回測。

## 6. 下一個允許出口

只有以下順序完成後，才可重新談 Claude 最新稿重審：

1. 提交 W2 修訂到 PR #44。
2. `check_repo.py --skip-backtest` C3 PASS，且候選 validator 負向測試 PASS。
3. 總召複審 8 份候選與契約對照表。
4. 總召明確同意後，才排 Claude 對最新稿的邊界重審。
5. 總召複審通過後，才排 independent audit。
6. 在此之前不合併、不修改正式 Skill、不啟動下一批次。

## 任務四態

**需要資料。** W2 修訂可在候選分支完成；目前仍需要重跑結果、CI 新 run 與總召複審，才能解除 PR #44 的 C3 阻塞。
