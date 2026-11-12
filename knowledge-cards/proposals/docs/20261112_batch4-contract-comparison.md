# 批次 1 共用契約對照表與狀態拆軸

> 文件狀態：`PROPOSED`／`NOT_ADOPTED`／`HISTORICAL_NOT_RUNTIME`。
>
> 本表是 PR #44 的補件，不是對 miko-core 正本的修改，也不是新的正式契約。

## 1. 目的

PR #44 原批次 1 Schema 把既有 miko-core 契約、候選工程欄位與路由／證據狀態混在一起。這份對照表先界定「已存在」「候選新增」「不應重複」與「仍需治理裁決」；在本表未經總召接受前，`batch-1-operation-contract.schema.json` 只能當候選草稿。

## 2. 既有契約與候選欄位對照

| 概念 | 既有權威來源 | PR #44 原候選處理 | 修訂後判定 | 責任邊界 |
|---|---|---|---|---|
| 任務四態 | `skills/miko-core/SKILL.md` §1／§2.7；`references/term-definitions.md` | 在 Schema 重新列為必要欄位與狀態聚合 | **既有契約，不重定義**；候選只引用既有 enum 與輸出格式 | miko-core 負責全域任務四態；Skill 只提供領域證據 |
| 困難卡七欄 | `skills/miko-core/references/term-definitions.md`「困難卡」 | 在 Schema 重新建立欄位 | **既有契約，不重定義**；候選只能補領域 AC 對應 | miko-core 定義欄位與出口；領域 Skill 提供現象／證據 |
| `operation_id` | miko-core 四視角／交接規則；`multi-agent-coordination-engine` FINAL_HANDOFF 19 欄中的 `OPERATION_ID` | 重新設計格式並列為 Schema 必填 | **既有識別概念**；候選須說明格式映射，不得替換既有 `OPERATION_ID` | miko-core／協調器維持跨 Skill 追蹤 |
| `task_id` | 既有任務與交接語境 | 直接列入候選 Schema | **可作候選輸入欄位**，但不得改變既有交接契約 | 任務建立方負責穩定性 |
| `idempotency_key` | miko-core 正本未另立同名正式欄位 | Gemini 建議新增為必要欄位 | **候選擴充，非正式欄位**；需明確映射到 `OPERATION_ID`，不得另造第二個操作身份 | safe-implementation／操作實作提出，治理裁決後才可接線 |
| `retry_policy` | safe-implementation 的候選工程責任；miko-core 負責失敗出口 | Gemini 建議新增 `STOP`／`READBACK_ONLY` 與 `max_attempts` | **候選擴充，需修語意**：`STOP` 不應要求重試次數；`READBACK_ONLY` 只讀回同一 operation，不重觸發副作用 | safe-implementation 實作；miko-core 決定未知／阻塞出口 |
| `NOT_READ`／`NOT_RUN`／`UNKNOWN` | miko-core 缺證據三分與 evidence-states | 在 Schema 與狀態機再次列為同一狀態群 | **既有證據軸，不與路由軸混合** | miko-core 定義區分；各步驟提供證據 |
| `CONFLICT`／`BLOCKED`／`PARTIAL`／`PASS` | 既有 evidence-states 與各 Skill 的領域判定 | 與缺證據狀態放在同一聚合軸 | **證據／結果軸**；不得和 `PAUSED_BY_USER` 或授權狀態同軸 | miko-core 聚合規則；領域 Skill 提供局部結果 |
| `PAUSED_BY_USER` | miko-core 停止領域規則；ADR-074／回測正本 | 放入共用狀態圖 | **路由／停止軸**，不是證據狀態 | MIKO 的停止決定優先；不得由候選 Schema 解除 |
| `READ_ONLY_DEGRADED` | 各領域 Skill 的候選／正式路由語意 | 與 evidence 狀態共用一張狀態機 | **路由模式軸**，不是任務結果 | 治理／路由責任方裁決 |
| `adopted`／`committed` | 治理採用與產物生命週期 | 作為候選布林欄位 | **採用／產物軸**；`false` 可作候選預設，不能被 validator 解讀為正式否決或批准 | 治理裁決與 safe-implementation 分工 |
| `baseline` | 正本版本、ADR、immutable commit 來源規則 | 以附件 `1.2.58`／`ADR-081`／舊 HEAD 作唯一 Schema baseline | **歷史來源欄位**；必須另列目前正本 `1.2.71`，不得混稱 | 來源核對與治理版本責任 |
| `steps[].kind=P/C/J` | miko-core 四視角與各領域候選流程 | 直接作共用步驟欄位 | **候選流程標籤**；不代表已接入 Runtime 或取代既有四視角 | 各 Skill 定義領域步驟，miko-core 負責總體閘門 |

## 3. 狀態拆軸

### 3.1 證據軸

```text
NOT_READ → 已要求但尚未讀到來源或證據
NOT_RUN  → 應執行但本輪尚未執行
UNKNOWN   → 已讀／已跑但仍無法判定
CONFLICT  → 多個可信來源或條件互相衝突
BLOCKED   → 硬封鎖、授權或安全門檻阻止執行
PARTIAL   → 局部結果已存在，整體仍未完成
PASS      → 本步驟的具體驗收條件通過，不等於採用或可執行
```

### 3.2 任務軸

只使用 miko-core 既有四態：

```text
完成／完成但有疑慮／需要資料／卡住
```

不得新增第五種任務態；局部 `PASS` 也不得自動變成「完成」。

### 3.3 路由／停止軸

```text
READ_ONLY_DEGRADED
PAUSED_BY_USER
BLOCKED
```

`PAUSED_BY_USER` 是 MIKO 的停止決定，不由 Schema、Skill、模型或 validator 解除。

### 3.4 採用／產物軸

```text
PROPOSED → NOT_ADOPTED →（需治理裁決後才可能）ADOPTED
COMMITTED=false →（需安全寫入與讀回證據後才可能）COMMITTED=true
```

候選 validator 不得把「檔案存在」解讀成 `ADOPTED`，也不得把本機 hash 解讀成遠端或 Runtime 生效。

### 3.5 授權軸

```text
NOT_REQUESTED／UNKNOWN／APPROVED／REJECTED／EXPIRED
```

授權狀態不能用 `PASS`、`BLOCKED` 或 `PAUSED_BY_USER` 代替；缺少 MIKO 決定時，依困難卡歸類為缺決定授權。

## 4. `operation_id` 與 `idempotency_key` 暫定映射

在總召裁決前只採以下候選語意：

1. `OPERATION_ID` 是既有跨步驟、跨交接的操作識別；不得移除或改名。
2. `idempotency_key` 是同一操作重入時的去重鍵，不是第二個獨立操作身份。
3. 同一 `OPERATION_ID`／`idempotency_key` 重跑只能讀取既有 manifest、狀態與讀回證據。
4. 任何可能觸發副作用的重跑，都必須建立新的明確批准與新的 operation，不得由自然語言「再試一次」隱含授權。
5. 若兩者無法在實作中維持一對一或明確父子關係，應退回移除 `idempotency_key`，而不是讓兩套身份並存。

## 5. `retry_policy` 暫定語意

| 模式 | 允許動作 | 不允許動作 |
|---|---|---|
| `STOP` | 保留失敗／未知證據，輸出困難卡 | 任何重試與副作用重觸發 |
| `READBACK_ONLY` | 只讀取同一 operation 的 manifest、產物與 hash | 重新呼叫副作用工具、建立新寫入、跨 operation 重試 |

`max_attempts` 只適用於經治理批准的唯讀／可逆讀取重試；不能與 `STOP` 的零重試語意衝突。候選 Schema 目前仍需依本表修訂，尚未成為正式契約。

## 6. 驗收出口

本表完成前：

- 批次 1 Schema：`REJECTED_AS_CURRENT_CONTRACT／PROPOSED_ONLY`。
- 正式 Skill：不得修改。
- Runtime：不得接線。
- `tw-backtest-workflow`：維持 `PAUSED_BY_USER`。
- independent-audit：暫不排程。
- 下一批次：不啟動。

## 7. 來源與限制

- 目前正本：`miko-core v1.73`／`VERSION 1.2.72`／`ADR-095`／`main 3d53f026d348e80b072fc9c21801a05dec0309aa`。
- 既有交接欄位：`multi-agent-coordination-engine` FINAL_HANDOFF 19 欄。
- PR #44 原候選 Schema 與 validator：只作比較對象，不能取代正本。
- 本表尚未代表 MIKO 的正式治理裁決。
