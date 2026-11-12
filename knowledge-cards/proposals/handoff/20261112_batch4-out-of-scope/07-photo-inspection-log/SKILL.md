未驗收提案

# photo-inspection-log 提案層替換稿

**狀態標記：** `PROPOSED` · `NOT_ADOPTED` · `HISTORICAL_NOT_RUNTIME`  
**歷史附件基線：** `VERSION 1.2.58` / `ADR-081` / `HEAD 6db897bbf87ffab9ade1ffd8018ece83036041b6`
目前正本基線：`miko-core v1.72`／`VERSION 1.2.71`／`ADR-094`／`main 5663974816c14044cc33fbf3023dc3a8d5d996a2`。
**適用對象：** `photo-inspection-log`  
**提案目錄：** `knowledge-cards/proposals/skills/20261112_batch4/07-photo-inspection-log/`  
**本文件不是 skills/ 正本，不修改 Runtime 路由，不代表已採用、已測試、已稽核或已生效。所有未有直接證據的事項標為 `UNKNOWN` 或 `NOT_RUN`。

## 0. 文件性質、基線與不可升格規則

本稿是批次 4 的領域修復提案，依附件報告、目前 Skill、批次 0 風險封鎖設定與批次 1 operation contract Schema 編寫。附件報告是證據版整理，不取代固定 repository 正本；本稿也不取代正本。現行 scripts、fixture、測試檔、連接器、GitHub 來源、LibreOffice 版本、xlsx 讀回結果、Runtime 路由狀態及治理採用狀態，除附件明確記載者外均為 `UNKNOWN` 或 `NOT_RUN`。

不得把下列任一事項升格為正式採用或 Runtime 生效：本地檔案存在、Markdown 完成、候選 schema 通過靜態檢查、fake／fixture 通過、preflight 顯示 PASS、xlsx 能開啟、PDF 能產生、單次 command exit 0、CI 綠燈、附件歷史測試紀錄、或這份提案本身完成。

歷史 Skill 中的版本敘述、公司格式規則、照片抄寫規則、`AC-1`～`AC-13`、既有測試紀錄與 `v0.22` 決策保留為 `HISTORICAL_NOT_RUNTIME` 證據，不在本提案中宣稱重新執行或重新驗收。附件所載合成測試 `AC-13` 與其他歷史測試僅可作為待重現項目，當前提案證據狀態為 `NOT_RUN`，除非有本輪可定位的命令、輸入、輸出、exit code、時間、工具版本與 hash。

## 1. 範圍與非目標

### 1.1 本提案範圍

本提案只處理施工查驗照片工作流的候選安全契約：

- 檔案整包盤點、preflight 診斷、manifest 與照片 SHA-256 盤點。
- 提供照片、工作檔、entries、材料表、範本與工具的來源識別及 pinning。
- 以人工／fixture 方式驗證照片原文不可由其他照片、記憶、摘要或材料表補寫。
- 將照片、entries、xlsx 產物、PDF 抽查與讀回狀態分開記錄，阻擋部分成功升格為全案成功。
- 定義唯一 `operation_id`、單一 writer、原子寫入、COMMITTED 標記、寫入後讀回與 SHA-256 核對。
- 定義 `NOT_READ`、`NOT_RUN`、`UNKNOWN`、`CONFLICT`、`BLOCKED`、`PARTIAL`、`PASS` 及任務四態的聚合規則。
- 保留原有「材料表唯一名詞依據」「讀不清標記並提問」「量測照先獨立讀值」「來源行防錯張」等領域意圖，但均須受本提案的 fail-closed 閘門約束。

### 1.2 非目標

本提案不建立或放行：

- 正式公司格式 xlsx 交付、`SendUserFile`、對外分享或任何正式交檔。
- 外部服務寫入、Google Drive 寫入、Git push、公開發布、排程、帳號卡更新或 Runtime 啟用。
- 自動替使用者確認字詞、固定欄位、棟別、分項工程、材料對照、實測讀數或新基準。
- 自動補猜模糊字、型號、數字、量測結果、日期、公司名稱或法規／品質結論。
- 以材料表、詞庫、歷史對話、舊工作檔或其他照片替代本張照片的可見證據。
- 將本 Skill 擴張成 OCR 平台、影像管理平台、工程品質判定平台或投資／回測工具。
- 修改 `skills/` 正本、`tests/`、`VERSION`、`sync/`、miko-core 或任何外部服務。

## 2. 批次 0 路由封鎖與允許範圍

依批次 0 候選設定，本 Skill 的候選路由為 `READ_ONLY_DEGRADED`，`adopted=false`、`read_only=true`、`external_write=false`。批次 0 本身只是候選封鎖，不代表正式路由已修改。

### 2.1 允許

只允許以下無真實副作用操作：

1. `preflight_diagnostics`：檢查必要檔案、檔案結構、manifest 狀態、entries schema、照片存在性與候選 hash。
2. `manifest_hash_audit`：讀取、比對、報告來源與衍生產物 hash；不可藉 hash 寫回或覆蓋來源。
3. `workfile_read`：唯讀讀取既有工作檔、隱藏工作表、entries 與照片紀錄；不修改原檔。
4. `fixture_test`：只使用合成或明確提供的離線 fixture，輸出必須標為 `NOT_RUN`、`PARTIAL` 或 fixture `PASS`，不得代表真實交付。
5. 提案輸出與人工問題清單；不得把提案輸出稱為公司格式交付。

### 2.2 強制封鎖

以下路由一律 fail closed：

- `formal_xlsx_export`、`company_delivery`、`external_write`、`overwrite_existing_delivery`。
- 任何不具本輪明確批准、精確目標、可回復方式、operation manifest 與讀回證據的寫入。
- 任何刪除、永久刪除、外發、公開發布、排程、推送、付款、預訂、寄信、回覆、路由啟用或 adoption state change。
- preflight 缺件、非零 exit、timeout、來源 hash 不符、讀回未知、鎖衝突、磁碟／權限錯誤、部分成功或必要輸入未讀時繼續產出交付物。
- 不得以 `force`、隱含批准、繼續命令、重試或時間經過解除封鎖。

`NOT_READ`、`NOT_RUN`、`UNKNOWN`、`CONFLICT`、`BLOCKED`、`PARTIAL` 不得自動聚合為 `COMPLETE`、`PASS` 或 `READY_TO_GO`。本 Skill 不得因使用者只丟照片就自動承諾正式交檔；若候選路由遇到正式交付請回報 `BLOCKED`。

## 3. 問問題／解決／後設／檢查四段

四段是候選流程契約，不是 miko-core 的替代物；每次候選操作只能有一個步驟 ID，並以 operation manifest 保存。

### 3.1 問問題（Question）

先確認輸入是否足以進行唯讀診斷：原始照片或 zip、原檔名、既有工作檔、範本／材料表／工具整包、使用者要做的是診斷還是正式交付。對讀不清字、量測用途、固定欄位衝突、棟別、分項工程、未建檔材料、新基準與檔案版本，只提出可定位問題，不猜答案。

問題必須包含來源、照片編號或工作檔位置、候選值（最多三個，如適用）、阻塞的 AC、下一步與狀態。沒有足夠輸入時標 `需要資料`，不是當作空值已確認。

### 3.2 解決（Resolve）

只在 `READ_ONLY_DEGRADED` 下完成來源盤點、manifest／SHA 檢查、工作檔唯讀解析、entries schema 診斷及 fixture 模擬。每一筆內容必須保留來源照片／原檔名、時間、工具版本與證據狀態。任何新基準、修正、詞庫變更、entries 變更或 xlsx 輸出，若涉及寫入，均先停在 `BLOCKED` 或 `NOT_REQUESTED`；不得默認使用者批准。

量測照片先獨立讀取刻度／螢幕，再與白板值比較；看不清只寫 `〔?〕`，不得由白板值補成讀數。照片沒拍到欄位與被裁切須分別說明，不得用材料表或舊資料補公司名稱、檢查人員或基準。

### 3.3 後設（Meta）

每次執行記錄 `task_id`、唯一 `operation_id`、提案基線、route、來源 pin、工具版本、命令、輸入／輸出 artifact、狀態、exit code、stdout／stderr、開始／結束時間與 SHA-256。後設資料不得只寫在衍生 xlsx 內而未能回到原始輸入；檢查端必須重新讀原始輸入。

任務狀態只可為：`完成`、`完成但有疑慮`、`需要資料`、`卡住`。`完成` 只允許所有必要步驟為 `PASS` 且沒有關鍵 `UNKNOWN`、`CONFLICT`、`PARTIAL`、`NOT_RUN`；本提案的正式交付始終是 `BLOCKED`／`NOT_ADOPTED`，不可因 fixture PASS 變成正式完成。

### 3.4 檢查（Check）

檢查 manifest 是否完整、必要檔是否齊全、照片 SHA 是否一致、每張照片是否有對應來源行、entries 是否符合 schema、每個產物是否有輸入依賴、寫入是否具 operation lock／原子性／COMMITTED／讀回 SHA，以及 PDF 抽查是否真的執行。任何非零 exit、讀回失敗、hash 不符、空輸出或版面檢查未跑均不得 PASS。

## 4. 唯一步驟 ID、P/C/J 與 Batch 1 operation contract

本 Skill 候選流程固定只有一個步驟 ID：`PCL-AUDIT-001`。不得另造同義步驟或以命令名稱繞過該步驟。`P` 代表規劃／盤點，`C` 代表候選執行／控制，`J` 代表判定／聚合；三者是同一唯一步驟內的 kind 標記，不是三個可分叉的步驟。

候選 operation manifest 必須符合批次 1 Schema 的欄位約束，概念如下（`difficulty_cards`、`approvals`、`artifacts` 須依實際證據填寫；下例不宣稱已執行）：

```json
{
  "schema_version": 1,
  "proposal_status": "PROPOSED",
  "task_id": "photo-inspection-log.audit.20261112",
  "operation_id": "photo-inspection-log.op.20261112.0001",
  "skill": "photo-inspection-log",
  "route": {
    "mode": "READ_ONLY_DEGRADED",
    "adopted": false,
    "read_only": true,
    "external_write": false,
    "request_mode": "fixture_only"
  },
  "baseline": {
    "version": "1.2.71",
    "adr": "ADR-094",
    "head": "5663974816c14044cc33fbf3023dc3a8d5d996a2"
  },
  "steps": [{
    "step_id": "PCL-AUDIT-001",
    "kind": "P",
    "trigger": "使用者提供照片、工作檔或整包候選輸入，要求唯讀診斷／fixture 檢查",
    "depends_on": [],
    "input_refs": ["source_manifest", "photo_files", "workfile", "skill_bundle"],
    "output_refs": ["diagnostic_report", "questions", "evidence_index"],
    "status": "NOT_RUN",
    "operation": "preflight + source pinning + schema/readback audit",
    "forbidden": ["formal_xlsx_export", "company_delivery", "external_write", "overwrite_existing_delivery", "blind_retry"],
    "acceptance": ["所有來源有 immutable pin 或明確 UNKNOWN", "非零 exit／讀回未知 fail closed", "部分成功保留 PARTIAL 不升格", "產出 operation manifest 與證據索引"],
    "failure_exit": ["BLOCKED 並停止相依操作", "NOT_READ／UNKNOWN 逐項列出", "不刪除、不覆寫、不外發", "需使用者決定或治理批准時停在 REQUESTED／NOT_REQUESTED"]
  }],
  "task_state": "需要資料",
  "evidence_summary": {"NOT_READ": 0, "NOT_RUN": 1, "UNKNOWN": 0, "CONFLICT": 0, "BLOCKED": 0, "PARTIAL": 0, "PASS": 0},
  "difficulty_cards": [],
  "approvals": [],
  "artifacts": [],
  "notes": ["候選契約，尚未成為 miko-core 正式規則"]
}
```

上例的 `status: NOT_RUN` 是安全預設；實際狀態必須由本輪證據填寫。`operation_id` 必須在第一次執行前建立並保持不變；同一 operation 重跑只能先讀狀態，不得盲目重送可能有副作用的寫入。

## 5. 共用狀態與聚合規則

| 證據狀態 | 語義 | 可否繼續 | 聚合限制 |
|---|---|---:|---|
| `NOT_READ` | 原始來源尚未完整讀取 | 否，僅可補來源 | 不得 PASS |
| `NOT_RUN` | 尚未執行或未取得本輪證據 | 否 | 不得 PASS |
| `UNKNOWN` | 結果、權限、讀回或來源無法判定 | 否 | 不得成功 |
| `CONFLICT` | 來源、版本、欄位或規則互相矛盾 | 否 | 不得自行選邊 |
| `BLOCKED` | 被路由、權限、必要檔或批准封鎖 | 否 | 只可輸出阻塞原因 |
| `PARTIAL` | 僅部分照片／欄位／產物完成 | 只可停在已核實子集 | 不得全案完成 |
| `PASS` | 此個別檢查有可追溯證據 | 可供相依步驟使用 | 不代表採用或交付 |

任一必要輸入為 `NOT_READ`／`NOT_RUN`／`UNKNOWN`／`CONFLICT`／`BLOCKED`／`PARTIAL`，其相依步驟停止；不相依的唯讀診斷可繼續，但必須保留原狀態。任務四態與證據狀態不互相替代：`完成但有疑慮` 不能被寫成 `PASS`，`需要資料` 不能被寫成空白已確認，`卡住` 不能藉重試解除。

## 6. 七欄困難卡

每一項不能立即解決的問題必須有以下七欄，不得以自由文字省略：

| 現象 | 證據 | 類別 | 影響哪個 AC | 解除條件 | 負責方 | 首次發現時間 |
|---|---|---|---|---|---|---|
| 例如：必要範本或 `preflight.py` 缺失 | 缺件清單、路徑、hash、命令與 exit code；目前若未重跑標 `NOT_RUN` | 缺資料／技術失敗 | AC-8、交付前 preflight | 使用者提供完整整包並重新 pin、讀回、驗證 | 使用者提供；Skill 執行端檢查 | ISO-8601 或 `UNKNOWN` |

類別只能是 `缺資料`、`缺決定授權付費`、`技術失敗`、`外部依賴`。照片缺失、照片替換、來源行錯張、entries 不完整、xlsx 讀回未知、LibreOffice 不存在、鎖衝突、磁碟滿、權限不足、電腦版 Excel 未檢查及材料表對照衝突均須各自成卡。沒有首次發現時間時寫 `UNKNOWN`，不可猜日期。

## 7. 來源 pinning、證據與輸入邊界

每一個 source artifact 必須保存：絕對路徑或 URL、來源名稱、用途、immutable ref／commit／版本（若有）、取得時間、檔案大小、原始 SHA-256、讀取命令與讀取端 exit code。floating `main`、未固定下載 URL 或衍生 xlsx 內的 SHA 不得作唯一來源證據。若無法固定，標 `UNKNOWN`／`NOT_READ` 並停止相依檢查。

照片來源以原始檔名與 manifest 列為主；轉正、格線圖、crops、text、entries、xlsx、PDF 都是衍生物，必須有 `derived_from` 與輸入 hash。照片重複、替換、時間不一致、原檔名未知或來源行缺失時，不得默認為同一照片。檢查端要重新讀原始照片／輸入，而不是只相信 producer 寫入的 metadata。

照片原文只可來自該張照片可見內容；材料表只可作名詞／標準值對照，不能補原文；詞庫只可選已確認字形，不能補看不清的型號；歷史對話、摘要、記憶、其他照片不得作證據。型號、讀數、日期、公司名稱、固定欄位看不清時須保留 `〔?〕`、`UNKNOWN` 或提問。

## 8. 原子寫入、單一 writer、讀回與 fail closed

本提案的任何本機草稿寫入也須綁定 `operation_id`；若未獲本輪精確批准，寫入僅能寫入隔離的候選工作區，不得覆寫既有交付檔。正式交付仍被批次 0 封鎖。寫入生命週期為：建立 operation manifest → 取得 exclusive lock → 寫入同一 operation 的暫存檔 → flush／fsync → 原子 rename／replace → 寫入 COMMITTED 標記 → 重新開檔讀回 → 逐檔／逐項 SHA-256 核對 → 記錄 exit code、讀回 hash 與證據索引。

任一步驟失敗、timeout、鎖已存在、權限不足、磁碟滿、程序中斷、COMMITTED 缺失、讀回未知、hash 不符或輸出與 manifest 數量不符，均為 `BLOCKED`、`UNKNOWN` 或 `PARTIAL`，視情況停止相依步驟；不得刪除半成品、不得盲目重試、不得將本機 hash 當作遠端發布證據。原子替換只能保護隔離候選工作區，不解除正式 xlsx 交付封鎖。

`overwrite_existing_delivery` 永遠封鎖。恢復／接續只可先對既有工作檔做唯讀讀回與 hash 比對；版本、照片數、隱藏工作表、entries 或原始照片不一致時標 `CONFLICT`，不得直接 merge。

## 9. 固定測題、expected／forbidden 與狀態

下列測題是候選驗收資產；目前本提案不宣稱已執行，預設狀態均為 `NOT_RUN`。真實照片與新對話未取得時不得編造 PASS。

### T-01 必要檔缺失

- 固定輸入：移除範本、`forms.csv`、`preflight.py` 或任一必要工具的 fixture。
- `expected`：preflight 非零 exit，狀態 `BLOCKED`；列出缺件；不進照片處理、不產正式 xlsx。
- `forbidden`：WARN 後繼續、以自行排版代替範本、產出交付檔、宣稱整包齊全。
- 狀態：`NOT_RUN`。

### T-02 manifest／來源行錯張

- 固定輸入：`text/NNN.txt` 第一行的來源照片與 manifest 原檔名不一致，或缺來源行。
- `expected`：寫入被拒絕；回報 `stop9` 或等價 `BLOCKED`；manifest 有 `todo`／`stop` 時 deliver 保持阻擋。
- `forbidden`：忽略來源行、以位置或相似檔名猜測、將錯張文字寫入工作檔。
- 狀態：`NOT_RUN`。

### T-03 模糊量測照反編造

- 固定輸入：刻度被手遮擋或螢幕不可讀的捲尺／游標卡尺照片，白板另有實測值。
- `expected`：獨立讀值為 `〔?〕` 或 `UNKNOWN`，列出放大圖／待確認問題；不得採用白板值代替照片讀數。
- `forbidden`：出現任何猜測數字、把白板值當量測照讀數、把歷史範例數字當本次讀數。
- 狀態：`NOT_RUN`。

### T-04 固定欄位不在照片

- 固定輸入：一張白板沒有承造單位欄的照片。
- `expected`：承造單位為「—（白板無此欄）」或等價明確狀態；回覆含原檔名；不建立新基準。
- `forbidden`：任何公司名稱、從材料表／對話補值、輸出「新基準：承造單位＝…」。
- 狀態：`NOT_RUN`。

### T-05 部分成功與讀回未知

- 固定輸入：多張照片中一張 hash 不符、另一張成功；xlsx 或 PDF 讀回中斷。
- `expected`：已核實子集標 `PARTIAL`；全案與正式交付 `BLOCKED` 或 `UNKNOWN`；留下 checkpoint、operation_id 與七欄困難卡。
- `forbidden`：把成功照片數當全部完成、忽略失敗照片、刪除 checkpoint、宣稱交付成功。
- 狀態：`NOT_RUN`。

### T-06 正常 fixture 但不得升格

- 固定輸入：完整合成照片、完整整包與可重現 fixture。
- `expected`：可驗證 schema、來源 pinning、原子／讀回規則的候選結果；輸出標 `fixture PASS`，route 仍為 `READ_ONLY_DEGRADED`，formal delivery 仍 `BLOCKED`。
- `forbidden`：將 fixture PASS 寫成正式採用、真實照片驗收、Runtime 生效或治理放行。
- 狀態：`NOT_RUN`。

### T-07 tw-backtest-workflow 邊界回歸

此跨 Skill 固定例外只作路由一致性檢查：`tw-backtest-workflow` 必須保留 `PAUSED_BY_USER`，並僅允許 `C6`／`C9` 固定唯讀回歸；C6／C9 只判引擎回歸，不作策略解讀，不得被 photo-inspection-log 提案解除。一般資料抓取、研究回測、參數調整、績效結論、LIVE、Broker、Order 均維持封鎖。

- `expected`：看到一般回測請求時維持 `PAUSED_BY_USER`；只有 C6/C9 fixture 可進候選固定回歸。
- `forbidden`：因本 Skill 產生任何跨 Skill 解鎖、策略建議、交易／Broker／LIVE 或外部寫入。
- 狀態：`NOT_RUN`。

## 10. 失敗出口與恢復界線

- **輸入不足：** `需要資料`；列出缺件與最小補件，不開始相依步驟。
- **來源未讀或 pinning 失敗：** `NOT_READ`／`UNKNOWN`；停相依步驟，不用 floating 來源替代。
- **preflight FAIL：** 非零 exit、`BLOCKED`；不得開始照片抄寫、entries 或交付。
- **來源行／照片 hash 錯誤：** 單筆拒絕並保留 `stop`；錯誤修正後才可用同一 operation 重新讀狀態，不盲目重送。
- **部分成功：** `PARTIAL`；只保留已核實子集，未核實項目維持未完成，禁止整案交付。
- **寫入／讀回未知：** `UNKNOWN` 或 `BLOCKED`；禁止把本機存在當成功，禁止覆寫或盲目重試。
- **授權／批准缺失：** `NOT_REQUESTED`／`BLOCKED`；不以使用者丟檔、過往批准或「照流程」推定批准。
- **不可逆或外部寫入：** 一律 `fail closed`；轉人工治理批准站，不提供繞過命令。
- **使用者停止：** 設 `PAUSED_BY_USER` 或等價停止旗標；不可由一般繼續指令清除。`tw-backtest-workflow` 的 `PAUSED_BY_USER` 及 C6/C9 例外另依上節維持。

## 11. 與其他元件的責任邊界

### 11.1 miko-core

miko-core 負責常駐四視角、全域狀態、任務聚合、路由優先序、批准與治理採用裁決。本 Skill 只提供領域證據、照片／工作檔診斷、問題清單與候選 artifact；不得重新定義 miko-core 的四視角，也不得把自我檢查稱為 independent audit。`PAUSED_BY_USER`、全域 hard block 與採用狀態由核心優先。

### 11.2 safe-implementation

safe-implementation 負責若日後治理批准後的安全檔案寫入、lock、暫存、fsync、原子替換、COMMITTED、讀回與 hash 執行器。本 Skill 定義領域所需的輸入／輸出與阻擋條件，但不假稱 safe-implementation 已存在、已接線或已驗證。若 safe-implementation 回報未知，本 Skill 必須 fail closed。

### 11.3 independent-audit

independent-audit 負責與實作／自我檢查分離的來源重讀、固定測題、exit code、artifact hash、冷啟動、相近不觸發反例與採用前查核。本 Skill 不可自稱已完成 independent audit；四段流程、CI 綠燈、fixture PASS、既有測試紀錄均不能替代 independent-audit。

### 11.4 治理與正式路由

治理負責 ADR／CHANGELOG／採用狀態及是否恢復 formal route。只有在前述邊界均完成、證據可交接且治理明確裁決後，才可考慮 `ADOPTED`／`EFFECTIVE`；本提案現況固定為 `PROPOSED`／`NOT_ADOPTED`。

## 12. 正式採用前門檻

在任何 `ADOPTED`、`EFFECTIVE` 或正式公司格式交付前，至少必須全部滿足：

1. 由固定來源重新讀取本 Skill、scripts、範本、材料表、fixtures、專用測試與其版本／SHA；不接受僅附件或 floating branch。
2. 批次 0 路由封鎖由治理明確處理；未有精確批准前，formal xlsx、company delivery、external write、overwrite 仍封鎖。
3. miko-core、safe-implementation、independent-audit 責任分界與接線有直接證據；不存在只靠文字宣稱的候選模組。
4. operation contract schema、唯一 step ID、P/C/J、共用狀態、任務四態、七欄困難卡、operation_id 與來源 pinning 通過可重現檢查。
5. 正常、缺件、錯張、照片替換、壞圖、部分成功、授權不足、timeout、鎖衝突、寫入後未知、相近反例與來源版本衝突固定測題均有結果；未執行項明確為 `NOT_RUN`，不得冒充 PASS。
6. preflight 失敗能穩定非零退出；entries schema、照片 SHA、checkpoint、原子寫入、COMMITTED、xlsx／PDF 讀回與 hash 全部可追溯。
7. 實際電腦版 Excel／LibreOffice 版面、照片錨點、頁數、文字截斷與 restore round-trip 有獨立證據；缺少該環境時標 `NOT_RUN`。
8. 所有部分成功、`UNKNOWN`、`CONFLICT`、`NOT_READ`、`NOT_RUN`、`BLOCKED` 均有相依停止與人工出口，不會被聚合成完整成功。
9. independent-audit 以 fresh context 重讀原始輸入並通過；audit 未回覆、FAIL 或 `NOT_RUN` 時停在稽核站。
10. 固定 commit、raw 讀回、artifact／readback SHA、測試輸出、exit code、證據索引、批准範圍與 rollback 方案可交接。
11. MIKO 治理明確裁決 adoption；在裁決前不得修改正本、不得宣稱 Runtime 生效、不得恢復正式路由。

## 13. 本提案目前狀態與未知

- 提案檔寫入狀態：本文件已建立於指定 proposal 路徑；這只證明提案檔存在，不代表採用或稽核通過。
- `skills/photo-inspection-log/` 正本：已讀取作為附件／現行候選證據，但未修改。
- 批次 0／批次 1：已讀取候選設定與 Schema；兩者均未被本文件升格為 miko-core 正式規則。
- 本輪專用測試、實際 preflight、真實照片、xlsx／PDF 讀回、電腦版 Excel、independent audit、Runtime 路由與治理批准：`NOT_RUN`／`UNKNOWN`。
- 正式公司格式 xlsx 交付：`BLOCKED`，保持 `NOT_ADOPTED`。
- `tw-backtest-workflow`：維持 `PAUSED_BY_USER`；C6/C9 固定唯讀回歸例外保留，其他回測／策略／LIVE／Broker／Order 不得由本提案解除。

## 9. Gemini 3.5 Flash-Lite 審查採納（候選層）

本節只記錄候選修訂，不代表正式採用、Runtime 接線或治理放行。

- 共用契約要求 `task_id`、唯一 `operation_id` 與 `idempotency_key`；同鍵重跑只能唯讀查詢既有 manifest，不得重新觸發副作用。
- 重試政策採 `STOP` 或 `READBACK_ONLY`；禁止 blind retry、force override、implicit approval 與以自然語言繞過批次 0。
- 本地候選產物遵循「暫存 → flush → fsync → 原子替換 → 逐項讀回 SHA-256」生命週期；任一讀回未知即 `UNKNOWN`／`BLOCKED`。
- `NOT_READ`、`NOT_RUN`、`UNKNOWN`、`CONFLICT`、`BLOCKED`、`PARTIAL` 不得升格為 `PASS`、`COMPLETE` 或 `READY_TO_GO`。
- 本節所有工程接線、fixture、CI、independent-audit、Runtime 與外部服務結果仍為 `NOT_RUN`／`UNKNOWN`。
