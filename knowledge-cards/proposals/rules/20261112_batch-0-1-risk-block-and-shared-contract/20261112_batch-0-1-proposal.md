未驗收提案

# 批次 0／批次 1：風險封鎖與共用契約提案

## A. 基線與範圍

- 提案類型：rules
- 提案狀態：`PROPOSED`
- 採用狀態：`NOT_ADOPTED`
- 歷史附件基線：`VERSION 1.2.58`／`ADR-081`／`HEAD 6db897bbf87ffab9ade1ffd8018ece83036041b6`
目前正本基線：`miko-core v1.72`／`VERSION 1.2.71`／`ADR-094`／`main 5663974816c14044cc33fbf3023dc3a8d5d996a2`。
- 目標：為 10 個修復設計提供批次 0 風險封鎖與批次 1 共用狀態／合約 schema。
- 寫入邊界：本提案只放在 `knowledge-cards/proposals/`；不修改 `skills/`、`tests/`、`VERSION`、`sync/`、正式路由或外部平台。

附件內容：

1. `batch-0-risk-blocks.json`：機械可讀的候選封鎖設定。
2. `batch-1-operation-contract.schema.json`：共用 Operation Contract JSON Schema。
3. `batch-1-state-machine.md`：狀態、任務四態、轉移、不變量與失敗出口。

## B. 批次 0：先封鎖風險

批次 0 的原則是 fail closed：未採用、未稽核、未批准時，預設為唯讀降級或使用者既有停止，不讓 schema、模型輸出、CI 或 force 解除封鎖。

### 全域設定

```yaml
mode: fail_closed
default_route: READ_ONLY_DEGRADED
adopted: false
read_only: true
external_write: false
allow_force_override: false
allow_implicit_approval: false
allow_blind_retry: false
unknown_is_success: false
not_run_is_pass: false
partial_is_complete: false
```

### 全域硬封鎖

候選設定拒絕下列行為：

- Broker、LIVE、下單、交易。
- 付款、預訂、刪除、永久刪除。
- 對外發送、回信、公開發布。
- 外部寫入、排程、憑證／帳號設定變更。
- 正式路由恢復與採用狀態變更。

### 領域封鎖摘要

| Skill | 路由模式 | 保留能力 | 封鎖能力 |
|---|---|---|---|
| dghp-travel | `READ_ONLY_DEGRADED` | 離線候選檢查、合成 fixture、來源狀態草稿 | `READY_TO_GO`、真實旅程放行、訂票、付款、導航 |
| gmail-cleanup | `READ_ONLY_DEGRADED` | 唯讀盤點、重要信檢查、mock 測試 | 移動、刪除、改標籤、退訂、寄信、回信、排程 |
| grilling | `READ_ONLY_DEGRADED` | 人工逐輪提問、提案輸出、唯讀來源審查 | 正式交付、自動共識、委派寫入、外部寫入 |
| label-foreign-text | `READ_ONLY_DEGRADED` | 可讀性檢查、來源查核草稿 | 定稿、正式標籤發布、對外交付 |
| make-skill | `READ_ONLY_DEGRADED` | 本機 lint 設計、唯讀審查、提案 | push、Drive DELTA、帳號卡、Runtime 啟用、公開發布 |
| multi-agent-coordination-engine | `READ_ONLY_DEGRADED` | 唯讀設計審查、獨立唯讀子任務設計 | 實際委派、並行 writer、秘密處理、外部寫入 |
| photo-inspection-log | `READ_ONLY_DEGRADED` | preflight 診斷、manifest／hash 盤點、工作檔讀取、fixture 測試 | 正式 xlsx、公司交付、覆寫既有交付 |
| tw-alert-check | `READ_ONLY_DEGRADED` | 來源狀態草稿、唯讀來源檢查、UNKNOWN 回報 | 官方安全結論、停班／交通安全放行、外部寫入 |
| tw-backtest-workflow | `PAUSED_BY_USER` | 固定 C6／C9 引擎回歸、唯讀契約測試 | 一般回測、抓資料、策略研究、參數調整、績效結論、LIVE／Broker |
| visual-content-intelligence | `READ_ONLY_DEGRADED` | `content_only`、使用者提供媒體讀取、`page_text_only` | `content_and_miko`、正式 proposal、工程導入、下載／上傳、外部寫入 |

`tw-backtest-workflow` 的 C6／C9 例外只允許判斷引擎回歸 PASS／FAIL，不得作策略績效解讀，也不得視為解除回測停止。

## C. 批次 1：共用 Operation Contract

每一個候選操作都使用同一份結構：

```text
schema_version
proposal_status
task_id
operation_id
skill
route
baseline
steps
task_state
evidence_summary
difficulty_cards
approvals
artifacts
notes
```

每個 `step` 必須有：

```text
step_id
kind: P | C | J
trigger
depends_on
input_refs
output_refs
status
forbidden
acceptance
failure_exit
evidence_refs
```

這樣可以把文件文字轉成可逐步驗收的契約，而不是只依靠模型記憶或段落理解。

## D. 共用狀態與任務四態

### 證據狀態

- `NOT_READ`：來源存在或應存在，但本輪讀不到。
- `NOT_RUN`：應執行但尚未執行。
- `UNKNOWN`：已嘗試但證據不足。
- `CONFLICT`：來源、版本、輸入或讀回結果互斥。
- `BLOCKED`：缺資料、決策、授權、付費或不可逆閘門。
- `PARTIAL`：只完成部分子步驟。
- `PASS`：單一檢查或單一步驟通過，不等於任務完成或正式採用。

### 任務四態

- `完成`：所有適用 AC 與相依證據通過，且已獲必要採用授權。
- `完成但有疑慮`：技術檢查可判定，但仍有非關鍵未知、殘留風險或等待稽核／治理。
- `需要資料`：缺來源、讀回、授權、決策或其他可明確補足的資料。
- `卡住`：連續兩輪無改善、無替代來源、不可逆閘門未解除或無法安全繼續。

`PARTIAL` 是證據狀態，不是任務四態；不可直接把 `PARTIAL` 當作「完成」。

## E. 困難卡與失敗出口

每次外部來源或工具失敗，都必須有：

```text
現象
證據
類別
影響哪個 AC
解除條件
負責方
首次發現時間
```

出口固定為：

- 缺資料：替代來源只試一次；仍取不到標 `NOT_READ`；只停相依步驟。
- 缺決定／授權／付費：`BLOCKED`；寫明 MIKO 要完成的精確動作；不得繞過授權。
- 技術失敗：回到失敗步驟；下一輪只修一個目標；連續兩輪無改善則卡住。
- 外部依賴：列負責方與解除條件；未回覆不算批准。

## F. 最小驗收清單

### 批次 0

- [ ] 未採用 Skill 預設不是 `ADOPTED`／`EFFECTIVE`。
- [ ] 正式副作用路由均為 `READ_ONLY_DEGRADED`、`PAUSED_BY_USER` 或 `BLOCKED`。
- [ ] 不存在 force、隱含批准或盲目重試解鎖。
- [ ] `UNKNOWN`、`NOT_RUN`、`PARTIAL` 不得被當成功。
- [ ] 固定回測例外僅限 C6／C9，且不作策略解讀。

### 批次 1

- [ ] JSON Schema 可解析。
- [ ] 每個 step 有唯一 ID、P／C／J、依賴、輸入、輸出、禁止、驗收與失敗出口。
- [ ] route 強制 `adopted=false`、`read_only=true`、`external_write=false`。
- [ ] baseline 固定為目前正本基線；歷史附件基線另列。
- [ ] 任何受阻狀態不會聚合成 `完成`。
- [ ] 外部操作具有 operation ID 與批准欄位。
- [ ] artifact 未讀回時不可標 `committed=true`。

## G. 責任與後續流轉

- Manus：建立本提案包，不審查、不放行、不修改正式路徑。
- Claude 治理總召：審查批次 0／1 是否可納入正式規則或 scripts。
- independent-audit：對正式採用前的候選規則、schema、狀態轉移與高風險封鎖做冷啟動稽核。
- MIKO：決定是否採用、是否恢復路由，以及是否允許任何外部寫入。

若正式採用，必須由 Claude 治理總召將候選內容搬入正式路徑，並依正本流程完成 independent audit、check_repo、測試、版本／ADR、推送後讀回與 MIKO 逐件批准。

## H. 本輪未完成事項

- 未修改 `skills/`、`tests/`、`VERSION`、`sync/` 或正式路由。
- 未修改 miko-core 正本。
- 未將 JSON Schema 接入正式 Runtime。
- 未執行 CI 或正式測試。
- 未完成 independent audit。
- 未取得正式採用或恢復路由批准。
- 未推送 GitHub。
