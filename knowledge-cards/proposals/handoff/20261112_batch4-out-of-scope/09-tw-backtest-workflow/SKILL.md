未驗收提案

# tw-backtest-workflow 提案層 Skill 替換稿

> **狀態標記：PROPOSED／NOT_ADOPTED／HISTORICAL_NOT_RUNTIME**  
> **歷史附件基線：VERSION 1.2.58／ADR-081／HEAD 6db897bbf87ffab9ade1ffd8018ece83036041b6**
> 目前正本基線：`miko-core v1.72`／`VERSION 1.2.71`／`ADR-094`／`main 5663974816c14044cc33fbf3023dc3a8d5d996a2`。
>
> 本文件是提案層草稿，不是 `skills/tw-backtest-workflow/SKILL.md` 正本的修改，不代表已採用、已測試、已稽核、已部署、已載入 Runtime、已恢復正式路由或已產出任何真實投資結論。未取得的證據標為 `UNKNOWN` 或 `NOT_RUN`；附件中的歷史實跑敘述均為 `HISTORICAL_NOT_RUNTIME`，不得作為本輪 Runtime 或正式採用證據。

## 1. 範圍、非目標與路由狀態

### 1.1 範圍

本提案只處理 `tw-backtest-workflow` 的契約層與固定回歸層：

- 以候選共用 operation contract 統一任務、操作、步驟、狀態、證據、困難卡與失敗出口。
- 強制入口先判定 `PAUSED_BY_USER`，再判斷是否屬於允許的固定回歸。
- 只保留指定固定樣本的 C6／C9 唯讀回歸，以及不產生策略解讀的唯讀契約測試。
- 對來源、輸入 manifest、資料與產物建立 pinning、hash、原子寫入及讀回規則的提案。
- 固定測題必須同時檢查 expected 與 forbidden 行為，避免只修改提示或規則讓原題變綠。

### 1.2 非目標

本提案不得擴張成投資平台、即時行情服務、資料抓取服務、Broker、下單、交易、LIVE、台指期、參數最佳化、策略研究平台、績效排名或個人化投資建議。不得以本提案恢復一般資料抓取、一般回測、策略比較、研究結論或任何投資式結論。

`C6`／`C9` 的例外只代表固定引擎回歸檢查；即使測試結果為 PASS，也不代表策略有效、資料完整、回測可交付、策略已採用或 Runtime 已生效。

### 1.3 批次 0 路由封鎖

依批次 0 候選設定，本 Skill 的路由固定為：

```text
route_mode       = PAUSED_BY_USER
adopted          = false
read_only        = true
external_write   = false
allow_force_override       = false
allow_implicit_approval    = false
allow_blind_retry          = false
unknown_is_success         = false
not_run_is_pass            = false
partial_is_complete        = false
```

允許項目僅有：

1. `fixed_regression_C6`；
2. `fixed_regression_C9`；
3. `readonly_contract_test`。

封鎖項目包括：`general_backtest`、`data_fetch`、`strategy_research`、`parameter_tuning`、`performance_conclusion`、`live`、`broker`、`order`，以及任何外部寫入、正式交付、公開發布、排程或路由恢復。

`PAUSED_BY_USER` 優先於領域 Skill 的一般繼續指令；不可由替代命令、force、隱含批准、時間經過或「只先抓資料」繞過。不可逆操作、遠端操作、外部服務寫入、交易相關動作或寫入後讀回未知時，一律 `fail closed`。

## 2. 證據、基線與共用狀態

### 2.1 證據標籤

候選流程採用批次 1 狀態：

- `NOT_READ`：來源或產物未完整讀取。
- `NOT_RUN`：規定檢查尚未執行。
- `UNKNOWN`：目前沒有可靠證據可判定。
- `CONFLICT`：來源、版本、欄位或規則互相衝突，尚未裁決。
- `BLOCKED`：路由、資料、授權或安全閘門禁止繼續。
- `PARTIAL`：只有部分子結果成立，不得聚合成全案完成。
- `PASS`：僅表示該項固定檢查具足夠直接證據，不代表 Skill 採用或 Runtime 生效。

任一關鍵 `NOT_READ`、`NOT_RUN`、`UNKNOWN`、`CONFLICT`、`BLOCKED` 或 `PARTIAL` 不得聚合成 `完成` 或 `READY_TO_GO`。狀態不因繼續操作而自動解除。

### 2.2 任務四態

每次候選執行必須有一個任務總態：

- `完成`：所有必要檢查均有直接證據，且無關鍵未知、衝突、封鎖或部分成功。
- `完成但有疑慮`：指定範圍內完成，但存在非阻斷疑慮；不得轉正式交付。
- `需要資料`：缺來源、manifest、固定樣本、批准或其他必要輸入。
- `卡住`：遇到封鎖、失敗、逾時、權限、讀回未知或不可安全繼續的狀況。

本提案目前總態：`需要資料`；本提案本身未執行固定回歸，執行狀態為 `NOT_RUN`。

### 2.3 共用 operation contract

候選 operation 記錄必須符合批次 1 Schema 的基本形狀：

```text
schema_version: 1
proposal_status: PROPOSED
task_id: <不可重複、可追溯>
operation_id: <每一操作唯一、可冪等>
skill: tw-backtest-workflow
route.mode: PAUSED_BY_USER
route.adopted: false
route.read_only: true
route.external_write: false
baseline.version: 1.2.71
baseline.adr: ADR-094
baseline.head: 5663974816c14044cc33fbf3023dc3a8d5d996a2
```

`operation_id` 必須綁定輸入 manifest、命令、工具版本、來源 pin、輸出路徑、批准範圍與讀回結果。相同 `operation_id` 重跑時只讀取既有 operation 狀態，不得盲目重送任何副作用；不存在可證明的冪等性時直接 `BLOCKED`。

## 3. 唯一步驟與四段流程

本提案只定義一個可追蹤步驟 ID：`TBW-REGRESSION`。四段是同一步驟內的階段，不另造第二個步驟 ID。該步驟的候選 operation `kind` 以 `P` 為主，並在階段內明確標出 `C` 與 `J`；不得把階段名稱當成額外步驟 ID。

### `TBW-REGRESSION`（P/C/J）

- **P（Plan／前置判定）**：觸發條件為明確要求 C6、C9 或唯讀契約測試，且沒有一般回測、資料抓取、研究、調參或績效解讀目的。輸入為固定 fixture、固定測題、批次 0 設定、批次 1 Schema、來源 pin 與 operation manifest。先判 `PAUSED_BY_USER`；不符合固定回歸例外立即 `BLOCKED`。
- **C（Check／固定檢查）**：只讀固定測題與固定樣本，驗證命令、輸入、輸出、狀態、exit code、expected／forbidden、hash 與讀回證據。不得修改正本、外部資料、遠端服務或交易狀態。
- **J（Judge／聚合）**：依證據狀態與任務四態聚合；只可回報固定引擎回歸結果與未解問題。不得將 PASS 轉成採用、研究結論、策略建議、投資訊號或正式放行。

#### 3.1 問問題

1. 只接受與固定回歸或契約測試直接相關的問題：測題 ID、固定 fixture 版本、預期 exit code、expected、forbidden、輸入 SHA、工具版本與基線。
2. 若請求包含標的、日期區間、成本、事件檔等策略參數，只有在固定 C6／C9 fixture 已預先定義且不作策略解讀時才可讀取；新資料、新標的、新區間或新策略一律 `BLOCKED`。
3. 缺任何必要輸入、來源 pin、固定 expected／forbidden 或批准範圍時，標 `需要資料`／`NOT_READ`，不得自行補值。
4. 不得把歷史報告中的 2330 實跑敘述、舊版指標或附件 PASS 當成本輪測試證據。

#### 3.2 解決

1. 建立或讀取唯讀 operation manifest，記錄 `task_id`、`operation_id`、基線、固定 fixture、輸入檔、輸入 SHA-256、命令、工具版本、開始／結束時間與預期結果。
2. 先驗證 `PAUSED_BY_USER` 與 C6／C9 例外，再驗證輸入 schema、日期升冪、OHLC 合理性、事件／還原價格互斥與固定 fixture 完整性。
3. 來源必須 pin 到 immutable ref、明確檔案、版本或內容 SHA-256；floating `main`、未標版本的遠端內容或衍生 metadata 不得作唯一證據。
4. 固定測試若需產生本地報告，使用 operation-specific 暫存路徑與單一 writer；先寫暫存、flush、fsync、原子替換，再寫 `COMMITTED`。任何寫入錯誤、鎖衝突、磁碟不足、中斷或讀回未知均 `fail closed`。
5. 寫入後重新讀回每個產物並核對 SHA-256、operation_id、基線與內容；缺讀回或 hash 不符不得標 `PASS`。本機讀回不能推論遠端發布或 Runtime 生效。

#### 3.3 後設

1. 只檢查固定回歸契約是否覆蓋原始缺口：`PAUSED_BY_USER` 優先、事件旗標恰好三選一、manifest／來源 pin、schema／錯誤類別／穩定 exit code、PIT／look-ahead／樣本不足／成本／基準／28 欄適用性阻擋，以及 C6／C9 固定回歸。
2. 四視角、自我檢查、CI 綠燈、固定測試 PASS 與 `independent-audit` 分開記錄；任何一項不能替代另一項。
3. 只允許對測試契約提出局部修補提案；不得藉修補擴大成資料抓取、研究、調參或投資平台。
4. 若測試出現部分成功，只保留已核實的子結果，總態為 `PARTIAL` 或 `完成但有疑慮`，不得包裝成完整成功。

#### 3.4 檢查

1. 逐項比較 actual 與 expected，並檢查 forbidden 是否確實未發生。
2. 保存 stdout、stderr、exit code、來源／工具 pin、輸入與輸出 hash、讀回 hash、狀態與困難卡索引。
3. `NOT_RUN`、`UNKNOWN`、`CONFLICT`、`BLOCKED` 或讀回未知時，輸出相應狀態與失敗出口，不得用「未發現問題」取代證據。
4. 固定 C6／C9 通過時，輸出措辭必須是「固定引擎回歸項目已具備該次檢查證據」（若實際執行）；不得寫成「策略有效」「可交易」「已採用」或「Runtime 生效」。本提案當前仍為 `NOT_RUN`。

## 4. 來源 pinning、原子寫入與讀回

### 4.1 Source pinning

每個來源、工具與 fixture 至少記錄：來源識別、immutable ref 或檔案路徑、版本／commit、用途、讀取時間、原始內容 SHA-256、命令與 exit code。檢查端必須重新讀取原始輸入；只讀衍生 metadata、報告內 hash 或前次 operation 結果不足以證明來源一致。來源衝突保留雙方證據並標 `CONFLICT`，不得自行選邊。

### 4.2 原子寫入

雖然目前路由為唯讀，若固定回歸需保存本地診斷產物，候選契約仍要求：單一 writer、exclusive lock、operation-specific 暫存檔、禁止覆寫原始檔、flush、fsync、原子替換、最後才寫 `COMMITTED`。中斷、權限錯誤、磁碟滿、鎖遺留或替換不確定時，標 `UNKNOWN`／`BLOCKED`，不得清理掉唯一證據，也不得重試可能已產生副作用的操作。

### 4.3 寫入後讀回

讀回必須逐檔比對內容 SHA-256、operation_id、基線、schema 與 `COMMITTED` 狀態。讀回逾時、檔案不存在、hash 不符、部分讀回或遠端結果不明均為失敗出口；不可宣稱已提交、已發布、已生效。任何外部寫入在本提案中一律禁止，即使有 API 成功回應也不得繞過路由封鎖。

## 5. 固定測題與 C6/C9 回歸例外

以下是提案層的固定測題契約；本文件未執行，actual、exit code、stdout、stderr、hash 與測試時間均為 `NOT_RUN`。

| 測題 | expected | forbidden |
|---|---|---|
| `TBW-R0-PAUSE` | 一般回測、資料抓取、策略研究、調參、績效結論在 `PAUSED_BY_USER` 下被拒絕；不產生外部副作用 | 先抓資料後才檢查暫停；用 force、替代旗標或隱含批准繞過；回傳策略結果 |
| `TBW-R1-EVENTS-XOR` | `--events`、`--adjusted`、`--ignore-events` 必須恰好三選一；零個或多個均為明確錯誤與穩定非零 exit code | 多旗標被靜默選第一個；缺旗標仍輸出正式結果；錯誤只靠 assert 或不穩定訊息 |
| `TBW-R2-MANIFEST-PIN` | 輸入 schema、manifest、範圍與 SHA-256 一致才可進固定檢查 | hash 不符仍計算；floating 來源當唯一基準；衍生 metadata 取代原始讀回 |
| `TBW-R3-PIT-LOOKAHEAD` | 只用決策日前資料；未來資料、全樣本統計、look-ahead 或 prefix 不一致時停止 | 偷看未來仍輸出結果；把 `NOT_CHECKED` 當 PASS；以提示詞取代故障測試 |
| `TBW-R4-DATA-SCHEMA` | CSV 欄位、日期升冪、OHLC、成交量與錯誤類別明確驗證；失敗非零退出 | 依賴 `assert` 作公開契約；壞資料被部分讀取後繼續；缺欄被當空值 |
| `TBW-R5-COST-BENCHMARK` | 成本、成交規則與買進持有基準均有明確證據；缺資料標 `UNKNOWN`／樣本不足 | 不含成本的績效被當正式結果；缺基準仍下優劣結論；未知填 0 |
| `TBW-R6-CORPORATE-EVENT` | 個股事件、還原價格、ETF 股利條件依契約阻擋或明示狀態 | ETF 缺事件／還原價格仍通過；`--ignore-events` 被當含息結果；事件跨區間被靜默忽略 |
| `C6` | 固定常數重算帳本與既定 expected 值一致；只回報引擎回歸 | 通過即宣稱策略有效、可交易、已採用或可 LIVE |
| `C9` | 固定的偷看隔日開盤、量能、最後一天、全樣本統計、事件、hash、順延取消與 ETF 稅率回歸符合 expected | 只測 happy path；失敗被 WARN 掩蓋；C9 PASS 被升格成完整回測或正式結論 |

C6／C9 是唯一保留的固定回歸例外。其測試資料、expected、工具版本與 fixture 必須 pin；若固定題本身變更，需新 operation_id、新證據與重新 independent audit。歷史附件中「C6／C9 全過」的文字只屬 `HISTORICAL_NOT_RUNTIME`，本輪未重跑即為 `NOT_RUN`。

## 6. 失敗出口與重試規則

- 使用者要求一般回測、資料抓取、研究、調參或績效結論：`BLOCKED`，不進資料層。
- `PAUSED_BY_USER` 缺失、被繞過或狀態衝突：`BLOCKED`，停止全部相依步驟。
- 輸入缺欄、格式錯誤、日期或 OHLC 不合法：`NOT_RUN`／`BLOCKED`，回報穩定錯誤類別與非零 exit code。
- manifest、來源 pin、工具版本或 SHA 缺失／不符：`NOT_READ`／`CONFLICT`／`BLOCKED`，不得猜測或靜默替換。
- 逾時、網路、授權、外部服務或官方來源失敗：本 Skill 不得重試外部抓取；標 `UNKNOWN` 或 `BLOCKED`。替代來源不可在本 Skill 本輪自行啟用。
- 固定測試部分通過：保留已核實子結果，標 `PARTIAL`，只停失敗項目的相依步驟，不升格全案完成。
- 寫入、原子替換、COMMITTED 或讀回未知：`UNKNOWN`／`BLOCKED`，不盲目重試；若可能已有副作用，先停止並等待人工裁決。
- 同一 `operation_id` 重跑：只讀 operation 狀態與既有證據，不重新送出副作用。

## 7. 七欄困難卡

每個阻塞、未知、衝突、部分成功或重試問題都必須填滿七欄：

| 現象 | 證據 | 類別 | 影響哪個 AC | 解除條件 | 負責方 | 首次發現時間 |
|---|---|---|---|---|---|---|
| 一般回測入口可能先抓資料再檢查暫停 | 附件報告 §2.9；批次 0 將 route 固定為 `PAUSED_BY_USER` | 技術失敗 | AC-R0 路由優先與零副作用 | 入口先判暫停，並由固定測題證明不可繞過 | Skill 維護者／independent-audit | 2026-11-12 附件核對 |
| 事件旗標未形成硬性 XOR 契約 | 附件報告 §2.9；現行說明僅文字要求三選一 | 技術失敗 | AC-R1 事件模式與穩定 exit code | 實作 schema／parser 與 `TBW-R1-EVENTS-XOR` | Skill 維護者 | 2026-11-12 附件核對 |
| manifest、來源 pin、checkpoint、輸出／讀回 hash 不閉環 | 附件報告 §2.9；批次 1 Schema 要求 operation／artifact 欄位 | 缺資料 | AC-R2 證據可追溯與讀回 | 提供 immutable pin、operation manifest、原子寫入與逐檔讀回測試 | Skill 維護者／independent-audit | 2026-11-12 附件核對 |
| 輸入驗證依賴 `DictReader`／`assert`，錯誤契約不穩定 | 現行 Skill 附錄 A；附件報告 §2.9 | 技術失敗 | AC-R3 schema、錯誤分類與非零退出 | 明確 validator、錯誤類別、exit code 與 fixture | Skill 維護者 | 2026-11-12 附件核對 |
| PIT、look-ahead、樣本不足、基準與事件未知可能仍產出解讀 | 現行 Skill §3、§6；固定回歸尚未於本提案重跑 | 缺資料 | AC-R4～AC-R7 證據與相依停止 | 固定測題 expected／forbidden、缺證據即 fail closed | Skill 維護者／independent-audit | 2026-11-12 附件核對 |
| 正式採用、Runtime 恢復與回測放行尚無治理證據 | 批次 0／1 候選設定；本文件為提案層 | 缺決定授權付費 | AC-R8 採用閘門 | 完成專用測試、independent audit、固定 commit 讀回與 MIKO 明確裁決 | MIKO 治理／independent-audit | 2026-11-12 附件核對 |

## 8. 與其他元件的責任邊界

### 8.1 miko-core

`miko-core` 負責全域四視角主流程、品質閘門、共用狀態與採用治理邊界；本 Skill 只負責臺股回測領域的固定回歸契約與領域輸入檢查。本 Skill 不得複製或取代 miko-core 的常駐四視角，也不得自行解除 `PAUSED_BY_USER`、改變全域狀態 enum 或宣稱治理採用。

### 8.2 safe-implementation

`safe-implementation`（若被治理正式採用）負責安全實作、原子檔案生命週期、鎖、暫存、fsync、原子替換、清理與讀回的共用工程機制。本 Skill 只提出必須滿足的回測 artifact contract；不得自行另造一套共用 writer，也不得把本地 hash 當遠端或 Runtime 證據。若共用機制未讀取、未接線或未驗證，標 `UNKNOWN`／`NOT_READ`。

### 8.3 independent-audit

`independent-audit` 負責以獨立上下文審查修改後的路由、狀態、AC、來源 pin、exit code、寫入／讀回與固定回歸；不由本 Skill 作者、本次四視角或 CI 綠燈自我替代。independent audit 未完成、FAIL、未回覆或 `NOT_RUN` 時，維持 `PAUSED_BY_USER`，不得交付或恢復正式路由。

## 9. 正式採用前門檻

下列條件全部具備前，狀態必須維持 `PROPOSED／NOT_ADOPTED`，路由維持 `PAUSED_BY_USER`：

1. MIKO 明確裁決本提案範圍與固定 baseline；不可用 implicit approval 或 force override。
2. 建立並驗證專用 `backtest_contract.py`、固定回歸資產與測試檔；候選檔案是否存在、接線與實際通過目前均 `UNKNOWN`／`NOT_RUN`。
3. C6／C9 及全部固定測題的 expected／forbidden、非零 exit code、失敗出口、相近不觸發反例與部分成功測試均有可重現證據。
4. 來源、工具、fixture、輸入與產物具 immutable pin、manifest、operation_id、輸出 SHA、讀回 SHA、原子寫入與 `COMMITTED` 證據。
5. 驗證 PIT、look-ahead、事件、成本、基準、樣本不足、ETF 條件與 28 欄適用性；任何未知不得被填零或包成正式結論。
6. `independent-audit` 以獨立上下文完成且非 FAIL；四視角、CI、固定回歸與 independent audit 的證據彼此分離。
7. 固定 commit／tag 的正本 raw 內容重新讀回並核對 SHA；本地提案路徑、附件報告或本機檔案存在不得替代正本證據。
8. 冷啟動、新對話、相近反例與路由不可繞過檢查完成；結果、命令、exit code 與環境記錄可交接。
9. MIKO 完成 ADR／採用狀態裁決後，才可另行決定是否將 `NOT_ADOPTED` 改為採用狀態；在此之前不得寫 `ADOPTED`、`EFFECTIVE`、`READY_TO_GO` 或 Runtime 生效。

## 10. 本提案的未知與未執行項目

- 目前未讀取或驗證 miko-core、safe-implementation、independent-audit 的正本接線與實際 Runtime 行為：`NOT_READ`／`UNKNOWN`。
- 未執行 `backtest_contract.py`、`preflight_fixed_regression.py`、C6、C9、專用測試、lint、CI、冷啟動或任何真實回測：`NOT_RUN`。
- 未驗證任何外部資料、FinMind、TWSE／TPEx、連接器、授權、遠端寫入或正式回測結果：`UNKNOWN`。
- 附件歷史版本、歷史實跑與歷史 PASS 不代表目前 checkout、目前正本、正式採用或 Runtime：`HISTORICAL_NOT_RUNTIME`。

**提案結論：** 可以提出契約修補，但在批次 0 封鎖、批次 1 共用契約、固定 C6／C9 回歸、independent audit 與 MIKO 治理裁決全部完成前，`tw-backtest-workflow` 僅可維持 `PAUSED_BY_USER`，不可恢復任何一般回測、資料抓取、研究或投資式結論路由。

## 9. Gemini 3.5 Flash-Lite 審查採納（候選層）

本節只記錄候選修訂，不代表正式採用、Runtime 接線或治理放行。

- 共用契約要求 `task_id`、唯一 `operation_id` 與 `idempotency_key`；同鍵重跑只能唯讀查詢既有 manifest，不得重新觸發副作用。
- 重試政策採 `STOP` 或 `READBACK_ONLY`；禁止 blind retry、force override、implicit approval 與以自然語言繞過批次 0。
- 本地候選產物遵循「暫存 → flush → fsync → 原子替換 → 逐項讀回 SHA-256」生命週期；任一讀回未知即 `UNKNOWN`／`BLOCKED`。
- `NOT_READ`、`NOT_RUN`、`UNKNOWN`、`CONFLICT`、`BLOCKED`、`PARTIAL` 不得升格為 `PASS`、`COMPLETE` 或 `READY_TO_GO`。
- 本節所有工程接線、fixture、CI、independent-audit、Runtime 與外部服務結果仍為 `NOT_RUN`／`UNKNOWN`。
