未驗收提案

# 批次 4 三方審查與共識狀態（更新版）

## 1. 基線

- 目前正本：`miko-core v1.71`／`VERSION 1.2.70`。
- 10 份附件歷史基線：`VERSION 1.2.58`／`ADR-081`／`HEAD 6db897bbf87ffab9ade1ffd8018ece83036041b6`。
- 附件基線只作歷史證據，標記為 `HISTORICAL_NOT_RUNTIME`，不覆蓋現行正本。
- 本輪候選內容先前只存在 Manus 本機；本 PR 的目的，是提供 GitHub 可追溯審查材料，不是合併或正式採用。

## 2. 三方角色與最新結果

| 角色 | 工作 | 最新結果 | 證據／限制 |
|---|---|---|---|
| Gemini 3.5 Flash-Lite | 共用性、可執行性與最小欄位建議 | `PASS／ADVICE_ONLY` | 已成功通訊；建議已套入候選 Schema 與 10 份提案層，不代表採用或稽核。 |
| Manus | 建立批次 0／1、10 份 Skill 提案、知識卡索引、validator、PR | `PROPOSED_ONLY` | 只提交 `knowledge-cards/proposals/`；不修改正式 Skill、Runtime、VERSION 或外部服務。 |
| Claude Sonnet 4.6 | 治理邊界、硬封鎖與提案狀態 | `PASS／PRE_GEMINI_EDIT` | 修改前摘要邊界審查通過；Gemini 最新修訂後尚未重審。 |
| independent-audit | fresh context 重讀、逐檔證據與治理採用檢查 | `NOT_RUN` | 不由 Gemini、Claude 或 Manus 自查取代。 |

## 3. Gemini 已套入的候選修訂

1. 共用契約新增候選 `idempotency_key`。
2. 共用契約新增候選 `retry_policy`，只允許 `STOP` 或 `READBACK_ONLY`。
3. 同一冪等鍵重跑只能唯讀查詢既有 manifest，不得重新觸發副作用。
4. 候選產物明確採暫存 → flush → fsync → 原子替換 → 逐項讀回 SHA-256 的生命週期。
5. 讀回未知維持 `UNKNOWN`／`BLOCKED`。
6. `NOT_READ`、`NOT_RUN`、`UNKNOWN`、`CONFLICT`、`BLOCKED`、`PARTIAL` 不得升格為 `PASS`、`COMPLETE` 或 `READY_TO_GO`。

這些內容只作候選規格，尚未接入正式 `miko-core`、safe-implementation 或 Runtime。

## 4. Claude 已完成與待完成範圍

### 已完成：修改前摘要邊界審查

Claude 先前判定 10 份提案的邊界摘要均 PASS，包含：

- `PROPOSED／NOT_ADOPTED／HISTORICAL_NOT_RUNTIME` 三重標記。
- `tw-backtest-workflow` 維持 `PAUSED_BY_USER`。
- Broker／LIVE／ORDER／TRADE／PAYMENT／BOOKING 與外部寫入硬封鎖。
- `UNKNOWN／NOT_RUN／PARTIAL／CONFLICT／BLOCKED／NOT_READ` 不得升格。

### 待完成：Gemini 修訂後重審

Claude 尚未重讀本次新增的 `idempotency_key`、`retry_policy` 與 10 份提案附加段落。此項需在 PR 上由總召或授權審查者確認後再執行。

## 5. 目前共識裁決

**狀態：`CANDIDATE_READY_FOR_GITHUB_REVIEW／NOT_READY_FOR_ADOPTION`。**

目前可以做：

1. 推送候選分支。
2. 建立只供審閱的 GitHub PR。
3. 由總召在 GitHub 上直接查閱檔案、差異與驗證器。
4. 收到總召意見後，再安排 Claude 最新邊界重審與 independent audit。

目前不可以做：

1. 合併 PR。
2. 修改正式 `skills/` 正本。
3. 啟用 Runtime 或恢復正式路由。
4. 執行外部寫入、公開發布、交易、Broker、LIVE、付款、預訂、刪除或寄信。
5. 把本 PR 的檔案存在、validator 通過或模型建議當作正式採用證據。

## 6. `tw-backtest-workflow` 特別處理

- 本輪不把一般回測、引擎旗標、PIT／OOS、成本、基準或策略驗證納入可放行內容。
- 維持 `PAUSED_BY_USER`。
- C6／C9 只有在未來獲准時，才可作具體樣本的固定唯讀引擎回歸。
- C6／C9 不得被解讀為策略有效、投資建議、績效結果或交易授權。

## 7. 待總召裁決

請總召在 PR 上確認：

- 候選層是否接受維持在 `knowledge-cards/proposals/`。
- 是否允許 Claude 對 Gemini 修訂後版本重審。
- 是否允許排程 independent audit。
- 是否維持批次 0 全域封鎖與 `PAUSED_BY_USER`。
- 是否維持「不合併、不修改正式 Skill、不啟動下一批次」。

## 任務四態

**需要資料。** GitHub PR 與總召審查是下一步必要資料；候選文件已在本機完成，但正式採用、Claude 最新重審、independent audit 與治理裁決尚未完成。
