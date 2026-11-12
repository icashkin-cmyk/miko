# 批次 4 知識卡與候選提案
## 給總召審閱的簡報腳本

> 文件性質：未驗收、候選層、供治理總召審閱。
>
> 本文件不代表正式採用、Runtime 生效、independent audit 通過、外部服務驗證或 GitHub 推送完成。

---

## 一、簡報基本資料

**簡報對象：** MIKO 治理總召

**簡報目的：** 請總召審閱目前已完成的批次 4 知識卡、8 份本輪候選修復提案與 2 份責任轉交文件，確認是否可以進入下一階段的工程驗證；本次不是請總召直接放行正式 Skill。

**目前正本基線：** `miko-core v1.73`；對應正本 `VERSION 1.2.72`／`ADR-095`／`main 3d53f026d348e80b072fc9c21801a05dec0309aa`。

**附件歷史基線：** `VERSION 1.2.58`／`ADR-081`／`HEAD 6db897bbf87ffab9ade1ffd8018ece83036041b6`。此基線只作歷史設計的來源證據，全部標記為 `HISTORICAL_NOT_RUNTIME`，不得覆蓋目前正本。

**目前工作副本狀態：** 所有本輪新增內容均位於 `knowledge-cards/proposals/`；候選修訂只允許寫入 PR 分支，沒有修改正式 `skills/`、`VERSION`、Runtime、外部服務、Drive 或帳號卡。

**建議簡報時間：** 10～15 分鐘，最後保留 5 分鐘給總召裁決。

---

## 二、開場稿：先講清楚這不是正式放行

> 「總召，這次報告的是批次 4 的候選層成果，不是正式 Skill 版本，也不是 Runtime 變更。8 份本輪候選維持 `PROPOSED`、`NOT_ADOPTED`、`HISTORICAL_NOT_RUNTIME`；07 與 09 已移至責任轉交區，不再列入本輪候選。請總召審閱的是：問題是否抓對、共用契約是否足夠、邊界是否清楚，以及是否同意進入下一個驗證階段。」

---

## 三、第一張：為什麼要做批次 4

### 講稿

> 「原 10 份修復設計共同暴露出同一組治理與工程問題：各 Skill 有自己的流程，但缺少一致的狀態、證據、失敗出口、操作 ID、來源固定、原子寫入與讀回驗證。總召審查後，07 與 09 移出本輪，其餘 8 份先不碰正本，先補既有契約對照與候選層驗證。」

### 主要共通技術債

1. 歷史版本、目前 checkout 與 Runtime 狀態容易混淆。
2. `NOT_READ`、`NOT_RUN`、`UNKNOWN`、`CONFLICT`、`BLOCKED`、`PARTIAL` 缺乏一致的聚合規則。
3. 缺少唯一 `task_id`、`operation_id`、`step_id` 與 P/C/J 步驟證據。
4. 外部來源、工具版本、命令、exit code、查閱時間與 SHA 未形成完整證據鏈。
5. 本地輸出缺少暫存、flush、fsync、原子替換、`COMMITTED` 與寫入後讀回 SHA 的完整生命週期。
6. 授權不足、限流、逾時、部分成功、來源衝突與相依停止尚未全部可測化。
7. 高風險路由可能被自然語言的「繼續」「先做再補批准」繞過。

---

## 四、第二張：批次 0——先封鎖風險

### 講稿

> 「批次 0 的原則是先降低副作用，不先追求功能完整。各 Skill 依自身領域採 `READ_ONLY_DEGRADED` 或 `PAUSED_BY_USER`。所有外部寫入、不可逆操作、正式交付與高風險路由先 fail closed。」

### 全批次硬封鎖

- Broker、LIVE、ORDER、TRADE、下單與交易。
- PAYMENT、BOOKING、真實付款與預訂。
- `send`、`reply`、`delete`、`permanent_delete`、`schedule`、`public_publish`。
- `external_write`、`route_enable`、`adoption_state_change`。
- force override、implicit approval、blind retry。
- 以替代命令、自然語言暗示或「先做再補批准」繞過封鎖。

### 回測特殊封鎖

> 「`tw-backtest-workflow` 必須維持 `PAUSED_BY_USER`。唯一保留的是 C6／C9 固定唯讀引擎回歸；即使 C6／C9 通過，也不能解讀為策略有效、投資訊號、績效結果或交易授權。」

### 請總召確認

- 是否同意批次 0 的全域封鎖優先於任何 Skill 自有流程？
- 是否同意所有未完成的外部寫入先停在 `BLOCKED`，而不是交由各 Skill 自行判斷？

---

## 五、第三張：批次 1——共用 Operation Contract

### 講稿

> 「批次 1 目前退回修訂。先用既有契約對照表拆開證據、任務、路由、授權與採用狀態；在總召接受對照表前，Schema 只是候選草稿，不是新的正式共用契約。」

### 核心欄位

- `schema_version`
- `proposal_status=PROPOSED`
- `task_id`
- `operation_id`
- `idempotency_key`
- `skill`
- `route.mode`
- `route.adopted=false`
- `route.read_only=true`
- `route.external_write=false`
- `baseline.version／adr／head`
- `steps[].step_id／kind(P|C|J)／depends_on`
- `steps[].status／forbidden／acceptance／failure_exit`
- `task_state`：完成／完成但有疑慮／需要資料／卡住
- 七欄困難卡
- `artifacts[].sha256／readback_sha256／committed=false`
- `retry_policy.max_attempts／on_unknown／same_operation_readback_only`

### 新增的候選安全約束

Gemini 3.5 Flash-Lite 建議並已寫入候選層：

1. 同一 `idempotency_key` 重跑只能唯讀查詢既有 manifest，不得重新觸發副作用。
2. 重試只能採 `STOP` 或 `READBACK_ONLY`，禁止 blind retry。
3. 候選產物生命週期為：暫存 → flush → fsync → 原子替換 → 逐項讀回 SHA-256。
4. 讀回未知時一律維持 `UNKNOWN`／`BLOCKED`。
5. 未知、未跑、衝突、阻擋或部分成功不得升格為 `PASS`、`COMPLETE` 或 `READY_TO_GO`。

### 請總召確認

- `idempotency_key` 與 `retry_policy` 是否可以作為共用契約的必要欄位？
- `committed=false` 是否維持候選層預設，直到正式治理裁決與安全接線完成？
- 是否同意只允許唯讀讀回，不允許同 ID 重新觸發副作用？

---

## 六、第四張：8 份候選與 2 份責任轉交總覽

### 講稿

> 「目前保留 8 份本輪候選文件；07 與 09 只保留責任轉交材料。候選文件仍需補既有契約對照、負向測試與總召複審，不能把文件存在或結構 validator PASS 當成採用。」

| # | Skill | 候選層重點 | 目前路由 |
|---:|---|---|---|
| 01 | `dghp-travel` | 行程草稿與真實預訂分離；餐飲／住宿／交通／返程證據傳播 | `READ_ONLY_DEGRADED` |
| 02 | `gmail-cleanup` | thread、附件、分頁、label 快照、逐封讀回與恢復邊界 | `READ_ONLY_DEGRADED` |
| 03 | `grilling` | 每輪最多五題；使用者單題同意不等於整包授權；不得冒充 independent audit | `READ_ONLY_DEGRADED` |
| 04 | `label-foreign-text` | 法域、產品類別、版本、可讀性與官方法規來源先決；模糊輸入停止 | `READ_ONLY_DEGRADED` |
| 05 | `make-skill` | 禁止把歷史討論、lint、CI 或檔案存在當成採用授權 | `READ_ONLY_DEGRADED` |
| 06 | `multi-agent-coordination-engine` | fresh context、互不寫入、writer 互斥、授權邊界與 CONFLICT | `READ_ONLY_DEGRADED` |
| 07 | `photo-inspection-log` | **已移出本輪**；轉交照片／文件專案 writer | `OUT_OF_SCOPE` |
| 08 | `tw-alert-check` | 逐來源／逐日／逐地點／逐時區；凌晨「明天」拆分；官方來源失敗停止 | `READ_ONLY_DEGRADED` |
| 09 | `tw-backtest-workflow` | **已移出本輪**；維持 `PAUSED_BY_USER`，不接回測工程 | `OUT_OF_SCOPE` |
| 10 | `visual-content-intelligence` | `observed`／`author_claim`／`inference` 分離；URL 不等於已讀取內容 | `READ_ONLY_DEGRADED` |

---

## 七、第五張：三方協同目前狀態

### 講稿

> 「Gemini 原先 Pro 模型因新使用者限制與配額問題不可用；依 MIKO 指示改用低階 `gemini-3.5-flash-lite`，目前已成功取得共用契約審查建議。Gemini 的建議已套入候選層，但總召判定原始輸出未入庫，不能當正式審查證據。Claude 先前只審查修改前的摘要，且未涵蓋本次 W2 修訂；目前不能宣稱最新稿通過。」

### 三方狀態表

| 角色 | 最新狀態 | 可宣稱範圍 |
|---|---|---|
| Gemini 3.5 Flash-Lite | 已完成共用契約與原 10 份設計的建議 | 只有未驗證的第二意見，不是採用或稽核 |
| Manus | 已套入候選 Schema 與 8 份候選層；07／09 已轉交 | 只代表提案檔已更新 |
| Claude Sonnet 4.6 | 修改前摘要邊界審查 PASS | 不涵蓋 Gemini 修訂後的最終候選稿 |
| independent-audit | `NOT_RUN` | 不得以 Gemini／Claude 代替 |

### 必須明確說明

- Gemini 建議已套入候選層，不代表正本已改。
- Claude 最新一輪邊界重審尚未完成。
- 三方最終共識尚未形成。
- 本輪沒有正式 Skill 接線、Runtime 啟用或 GitHub 推送。

---

## 八、第六張：驗證證據

### 講稿

> 「目前已完成的是檔案層與候選契約層驗證，不是 Runtime 功能驗證。」

已完成：

- 10 個候選 `SKILL.md` 均存在。
- 每份第一行均為「未驗收提案」。
- 每份均含 `PROPOSED`、`NOT_ADOPTED`、`HISTORICAL_NOT_RUNTIME`。
- Schema 可由 JSON parser 讀取。
- 提案層 validator 通過 `proposal_count=10`。
- `route_boundary=knowledge-cards/proposals-only`。
- `git diff --check` 通過。
- 非提案區變更為 0。

尚未完成：

- Claude 對 Gemini 修訂後版本的重審。
- independent audit。
- 專用 fixture 與正常／失敗／部分成功測試。
- CI、冷啟動、新對話回歸。
- 正式 Skill 接線與 Runtime 行為驗證。
- 固定 commit／raw／逐檔 SHA 的正式交接。

---

## 九、第七張：請總召裁決的 6 個問題

### 請逐項回答

1. **候選層是否可接受？** 是否同意 8 份文件維持在 `knowledge-cards/proposals/`，07／09 維持責任轉交，不直接修改正式 Skill？
2. **共用 Schema 是否可進入工程驗證？** 是否接受 `idempotency_key` 與 `retry_policy` 作為候選契約必要欄位？
3. **封鎖是否維持？** 是否確認全部外部寫入、Broker、LIVE、交易、付款、預訂與正式發布繼續 fail closed？
4. **回測是否維持停止？** 是否確認 `tw-backtest-workflow` 繼續 `PAUSED_BY_USER`，C6／C9 只作固定唯讀回歸？
5. **是否允許 Claude 重審？** 若允許，範圍只限 Gemini 修訂後的候選提案與批次 0／1 Schema，不進入正式 Skill。
6. **下一批次是否啟動？** 只有在 Claude 重審 PASS、機械驗證通過、independent-audit 排程與治理裁決完成後，才進入下一個工程批次。

---

## 十、建議總召裁決格式

建議總召用以下格式回覆，避免「同意」範圍不清：

```text
批次 4 候選層：同意／不同意／需修訂
批次 0 封鎖：維持／修改（若修改請列精確項目）
批次 1 Schema：同意進工程驗證／退回修訂
8 份候選提案：全數／指定編號進 Claude 重審；07／09：維持轉交
Claude 重審：允許／不允許
推送候選分支開 PR 供審查：允許／不允許（只推分支與 PR，不合併）
independent-audit：允許排程／暫不排程
正式 Skill 修改：禁止／另行明確授權
Runtime／GitHub／外部寫入：禁止／另行明確授權
下一批次：啟動／不啟動
```

---

## 十一、收尾稿

> 「總結：批次 4 目前保留 8 份候選、07／09 轉交，並補上契約對照、狀態拆軸與負向驗證。成果仍不等於正式採用。外部寫入與不可逆操作 fail closed，`tw-backtest-workflow` 維持 `PAUSED_BY_USER`，未知與部分成功不得升格。下一步是重跑 C3／check_repo，等待總召複審；在此之前不合併、不修改正式 Skill、不啟用 Runtime。」

---

## 十二、交接欄位

- **任務四態：** 完成但有疑慮。
- **已完成：** 批次 0／1 候選契約、8 份本輪候選提案、07／09 責任轉交、契約對照表、Gemini 建議候選層套入、負向 validator、索引與本簡報腳本。
- **未完成：** Claude 最新邊界重審、independent audit、正式接線、專用測試、Runtime、GitHub 推送。
- **目前風險：** 最新候選稿尚未經 Claude 重審；`label-foreign-text` 的狀態計數語意仍需在重審時確認。
- **阻塞條件：** 需要總召明確裁決是否允許 Claude 重審與是否進入工程驗證。
- **負責方：** 總召裁決；Manus 依裁決執行候選層驗證；正式採用前由 independent-audit 重新讀取與判定。
- **外部寫入：** NONE；本輪未執行 GitHub、Drive、Runtime 或任何外部服務寫入。
