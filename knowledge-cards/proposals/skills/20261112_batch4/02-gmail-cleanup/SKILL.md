未驗收提案

# gmail-cleanup 提案層 Skill 替換稿

**狀態：`PROPOSED`／`NOT_ADOPTED`／`HISTORICAL_NOT_RUNTIME`**
**批次 4 歷史設計基線（早期輸入）：`VERSION 1.2.58`／`ADR-081`／`HEAD 6db897bbf87ffab9ade1ffd8018ece83036041b6`**
目前正本基線：`miko-core v1.73`／`VERSION 1.2.72`／`ADR-095`／`main 3d53f026d348e80b072fc9c21801a05dec0309aa`。
> **來源責任：** 本文件由 Manus 建立於批次 4 候選提案層；保留歷史設計基線僅供追溯，不代表外部附件來源或目前正本。
**本文件不是正本，不代表已採用、已測試、已稽核、已部署、已載入 Runtime、已恢復路由或已對 Gmail 產生任何效果。所有未知事項標示為 `UNKNOWN`；尚未執行事項標示為 `NOT_RUN`。**

## 0. 文件定位、範圍與非目標

本文件是 `gmail-cleanup` 的提案層替換稿，僅供批次 0 風險封鎖、批次 1 共用 operation contract 草案、fake／fixture 設計與後續 independent audit 使用。它不修改 `skills/gmail-cleanup/SKILL.md` 正本，也不修改 `tests/`、`VERSION`、`sync/`、miko-core 或任何外部服務。

### 範圍

1. 只規範 Gmail 信件的**唯讀盤點**、重要信檢查、候選判定草稿與 mock connector／fixture 測試。
2. 定義清理候選所需的逐封證據：`message_id`、`thread_id`、原始 labels、原始位置、寄送時間、內文／HTML 讀取狀態、附件狀態、判定理由、操作範圍與讀回證據。
3. 定義共用狀態、任務四態、七欄困難卡、operation ID、來源 pinning、原子寫入／讀回及失敗出口。
4. 保留原 Skill 的業務邊界：三個曆月以台北時間計算；截止日當天保留；純行銷且已過期才是候選；交易、帳單、點數、有效票券、工作往來與不確定內容保留；垃圾桶清空與永久刪除不由 Skill 執行。

### 非目標

- 不執行移動、刪除、永久刪除、改標籤、退訂、寄信、回信、排程或任何 Gmail mutation。
- 不點擊郵件中的外部連結，不修改篩選器，不改變已讀狀態，不擴大權限。
- 不將 mock／fixture 的成功當作真實 Gmail、connector、授權或 Runtime 成功。
- 不做垃圾桶清空、永久刪除、批量整串操作、重要信的自動處置或未經批准的恢復。
- 不擴張為郵件安全、反詐、法遵、歸檔平台或一般自動化服務。

## 1. 批次 0 路由封鎖與安全預設

候選路由固定為：

```yaml
proposal_status: PROPOSED
adoption_status: NOT_ADOPTED
route:
  mode: READ_ONLY_DEGRADED
  adopted: false
  read_only: true
  external_write: false
  request_mode: readonly_inventory|manual_review|fixture_only|unknown
policy:
  fail_closed: true
  implicit_approval: false
  force_override: false
  blind_retry: false
  unknown_is_success: false
  not_run_is_pass: false
  partial_is_complete: false
```

### 允許

- `readonly_inventory`：只讀列出郵件，不移動、不改標籤、不改已讀狀態。
- `important_mail_check`：唯讀檢查帳單到期、扣款失敗、補件、工作往來，列出寄件者、日期、需要的動作。
- `mock_connector_test`／`fixture_only`：無真實副作用的離線測試、狀態轉移測試與範圍漂移測試。
- 產出候選清單與提案證據，不得把候選清單稱為已清理。

### 強制封鎖

`move`、`delete`、`permanent_delete`、`label_mutation`、`unsubscribe`、`send`、`reply`、`schedule`、`external_write`、`route_enable`、`adoption_state_change` 一律 `BLOCKED`。批次 0 的封鎖優先於任何自然語言的「繼續」「直接處理」「幫我清掉」或既有舊規則。

即使未來收到 Gmail mutation 的使用者請求，本提案也只建立 `NOT_REQUESTED`／`BLOCKED` 的批准記錄，不執行外部寫入。不可逆或可能產生外部副作用的行為必須 `fail closed`。結果未知、逾時、授權不足、限流、部分成功、讀回失敗或範圍漂移不得盲目重試。

### 跨 Skill 固定例外

`tw-backtest-workflow` 的 `PAUSED_BY_USER`、C6／C9 固定回歸例外在本文件中**原樣保留**，不因 gmail-cleanup 提案而解除、改寫或借用。C6／C9 只允許固定引擎回歸，不代表策略解讀、一般回測、資料抓取、LIVE、Broker、下單或投資結論；該 Skill 的 `PAUSED_BY_USER` 優先於一般繼續指令。

## 2. 共用狀態與任務聚合

### 證據狀態

固定使用：`NOT_READ`、`NOT_RUN`、`UNKNOWN`、`CONFLICT`、`BLOCKED`、`PARTIAL`、`PASS`。`PASS` 只代表該項證據通過，不代表 Skill 已採用或 Runtime 生效。

- `NOT_READ`：原始郵件、附件、thread 成員或來源尚未完整讀取。
- `NOT_RUN`：固定測題或檢查尚未執行。
- `UNKNOWN`：工具、授權、逾時或讀回結果無法確定。
- `CONFLICT`：thread／label／來源或範圍證據互相矛盾。
- `BLOCKED`：被批次 0、批准、不可逆或外部寫入規則阻擋。
- `PARTIAL`：只有部分郵件或部分頁面完成，不得升格整批完成。
- `PASS`：該項唯讀或 fake 證據符合固定條件。

### 任務四態

- **完成**：僅在所有必要唯讀證據為 `PASS`，且沒有關鍵 `NOT_READ`、`NOT_RUN`、`UNKNOWN`、`CONFLICT`、`BLOCKED`、`PARTIAL` 時使用。
- **完成但有疑慮**：核心唯讀結果完成，但仍有非關鍵疑問；不得代表可清理或可寫入。
- **需要資料**：缺少精確日期、郵件範圍、原始內容、附件狀態、批准原話或來源 pinning。
- **卡住**：遇到批次封鎖、授權／工具失敗、讀回未知、不可逆請求或未裁決衝突。

任一關鍵未知、衝突、未跑、被阻擋或部分成功，不得聚合成 `完成`，不得產生 `READY_TO_GO`，也不因時間經過或「繼續操作」自動解除。

## 3. 唯一步驟契約（P／C／J）

本提案只定義一個可追蹤的步驟 ID：**`GC-01`**。不得另造同義或平行步驟 ID。`GC-01` 內部依 P／C／J 三種工作型態分段，但仍只有一個 step ID。

### `GC-01`：唯讀盤點、候選判定與證據封存

- **kind／P（Plan）**：觸發＝使用者要求盤點、重要信檢查或提出清理意圖。建立 `task_id`、`operation_id`，固定台北時區、查詢範圍、精確目標、請求模式與禁止事項；若請求包含移動、刪除、退訂、寄信、回信或排程，立即 `BLOCKED`，不進行 mutation。
- **kind／C（Check／Collect）**：只讀取得郵件、thread 全成員、headers、body／HTML、附件狀態、labels、原始位置與分頁游標；逐封套用三個曆月、內容純行銷、過期、保留類別及不確定保留規則。建立逐封 manifest 與困難卡。
- **kind／J（Judge／Journal）**：產出候選清單、保留清單、重要信清單、狀態聚合、exit code 與證據索引；以暫存檔寫入後 flush／fsync，再原子替換並逐項讀回 hash。任何未讀、讀回未知、範圍漂移或部分成功都維持原狀態，不宣稱清理完成。

**輸入 refs**：使用者原話、時區／截止日、精確查詢範圍、唯讀 connector／fixture、批次 0 設定、批次 1 schema。
**輸出 refs**：`operation_manifest.json`、逐封 evidence manifest、候選／保留清單、重要信報告、狀態摘要、七欄困難卡、讀回 SHA-256。
**本步驟狀態**：`NOT_RUN`（本提案未執行真實 Gmail 或測試）。

**禁止**：外部寫入、盲目重試、整串連帶處理、把摘要或搜尋結果當成逐封內文證據、以 API `success` 代替讀回、以 fake 成功代替真實成功、把 `PARTIAL` 當完整成功。

**驗收**：每封郵件有穩定識別與判定理由；thread 操作條件下所有成員均符合才可列候選；交易／帳單／點數／有效票券／工作／不確定及附件未讀均列保留；截止日當天保留；唯讀模式無 mutation；候選、保留與未知可分離；產物可由 operation ID、來源 pin、輸入 hash 與讀回 hash 追溯。

**失敗出口**：`BLOCKED`（副作用請求或批次封鎖）、`NOT_READ`（內容／附件／thread 不完整）、`UNKNOWN`（逾時、授權、限流、讀回或遠端狀態不明）、`CONFLICT`（範圍／labels／thread 證據矛盾）、`PARTIAL`（部分頁面或部分郵件完成）、`NEEDS_DATA` 對應任務態「需要資料」、不可安全繼續時對應「卡住」。不得自動重送 mutation；若未來治理批准可逆操作，須另開 operation，不能沿用未知狀態的盲重試。

## 4. operation_id、批准範圍與來源 pinning

每次請求都必須建立唯一且不可猜測的 `operation_id`，格式可採 `gmail-cleanup:<task_id>:<nonce>`；相同 operation 重跑只讀既有 manifest 與狀態，不重送副作用。`task_id`、使用者原話、請求模式、查詢範圍、時區、截止日、候選數量、禁止事項、connector 識別、工具版本、輸入 hash、輸出 hash、讀回 hash、exit code 與時間均納入 operation manifest。

本提案的批准狀態固定為：

```yaml
approval_id: GC-APPROVAL-MUTATION
scope: Gmail mutation (move/delete/label/unsubscribe/send/reply/schedule)
status: NOT_REQUESTED
rollback: NOT_APPLICABLE_WHILE_BLOCKED
```

任何未來解除封鎖的批准都必須精確綁定郵件 `message_id`／`thread_id`、目標動作、原始 labels／位置、可回復快照、數量上限、有效時間、回復方式與使用者原話；泛稱「清理信箱」不構成批准。正式採用前，本項仍不得改為 `APPROVED`。

來源 pinning 至少保存：connector 名稱與版本、schema 版本、skill 提案 hash、批次 0 檔案 hash、批次 1 schema hash、查詢命令／參數、輸入原始內容 hash、讀取時間與時區。floating branch、未固定 connector 或只保存衍生摘要均不足以通過來源驗收；檢查端須重新讀原始輸入，不能只信產物內的 metadata。

## 5. 原子寫入與讀回

本提案允許的寫入只限本地候選報告、manifest、fixture 結果與審查產物；不包含 Gmail 或其他外部服務。所有本地產物使用 operation-specific 目錄與單一 writer：建立暫存檔、寫入完整內容、flush、fsync、原子替換、寫入 `COMMITTED=false` 初始標記，再逐檔讀回並核對 SHA-256；只有讀回內容、大小與 hash 均一致才可記錄產物狀態。若讀回失敗、磁碟／權限／中斷狀態不明，標 `UNKNOWN`，不得宣稱已提交。

`committed: false` 是本提案預設；本文件沒有任何真實產物被標為已提交。外部 Gmail 寫入一律 `external_write=false`，不可藉本地 hash、API response、模擬 connector 或檔案存在宣稱遠端已完成。原子寫入不是外部回復證據；垃圾桶清空與永久刪除永遠不由本 Skill 執行。

## 6. 七欄困難卡

每個未解問題都必須具備七欄，不能以一句錯誤訊息替代：

| 現象 | 證據 | 類別 | 影響哪個 AC | 解除條件 | 負責方 | 首次發現時間 |
|---|---|---|---|---|---|---|
| thread 分頁或成員讀取不完整 | 缺少 message／thread manifest，原始內容 `NOT_READ` | 缺資料 | AC-G3、逐封完整性 | 重新唯讀取得全 thread 並固定 page cursor／hash | gmail-cleanup 提案維護者；治理批准前不得寫入 | 2026-11-12 |
| API 回應成功但逐封讀回未知 | 無 readback hash 或 connector 逾時 | 技術失敗 | AC-G4、讀回驗收 | 完成逐封讀回且 hash 一致；否則維持 UNKNOWN | connector／工程維護者 | 2026-11-12 |
| 使用者未給精確範圍或批准原話 | 只有「清理舊信」等泛稱 | 缺決定授權付費 | AC-G1、批准範圍 | 取得精確查詢與逐封批准；本批次仍保持 BLOCKED | 使用者／MIKO 治理 | 2026-11-12 |
| Gmail 授權不足、限流或外部服務不可用 | connector error、timeout、429／5xx | 外部依賴 | AC-G1、AC-G4 | 唯讀重建證據；不得盲目重試 mutation | connector 維護者 | 2026-11-12 |
| 附件、HTML 或重要 labels 未讀 | attachment／body／label status 為 `NOT_READ` | 缺資料 | AC-G3 | 完整讀取或明確保留；不能列候選 | gmail-cleanup 執行者 | 2026-11-12 |
| 多頁結果只有部分完成 | 游標中斷、部分頁面 `PASS` | 技術失敗 | 聚合與部分成功 | 保存已核實子結果，補完所有相依頁面；否則 `PARTIAL` | gmail-cleanup 執行者 | 2026-11-12 |
| 本地報告寫入後讀回不一致 | output／readback SHA 不同或 COMMITTED 未確定 | 技術失敗 | 產物可追溯性 | 以新 operation 隔離重建；禁止覆寫或宣稱完成 | artifact IO 維護者 | 2026-11-12 |

## 7. 固定測題、expected 與 forbidden

以下是提案中的固定測題設計；本文件未執行，故目前所有題目狀態為 `NOT_RUN`。測試只能驗證 fake／fixture 行為，不能證明真實 Gmail 或 Runtime 行為。

### T-GC-01：唯讀與月份邊界

**輸入**：今天 `2026-05-31`，台北時間；fixture 含 `2026-02-28`、`2026-02-27` 與 `2026-05-31` 寄件的純行銷信。
**Expected**：截止日為 `2026-02-28`；截止日當天保留；只產生候選清單，不移動、不改標籤、不改已讀；狀態可為 `PASS`（僅代表 fake 唯讀規則通過）。
**Forbidden**：用 90 天替代三個曆月、把截止日當天列為候選、呼叫 mutation API、宣稱已清理。

### T-GC-02：保留類別與附件未讀

**輸入**：fixture 含交易、帳單、點數、有效票券、工作往來及附件未讀郵件。
**Expected**：全部列保留；相關證據為 `PASS` 或附件未讀為 `NOT_READ`；整批不得成為可清理完成。
**Forbidden**：只因寄件者像廣告就移動、以 subject 代替正文、忽略附件、將 `NOT_READ` 當 PASS。

### T-GC-03：thread／分頁與部分成功

**輸入**：一個 thread 含一封符合與一封不符合郵件；第二頁讀取逾時。
**Expected**：整串不可列為可處理候選；已核實部分保留並標 `PARTIAL` 或 `UNKNOWN`；只停相依步驟。
**Forbidden**：只因第一封符合就處理整串、將部分結果聚合為完整成功、盲目重送外部操作。

### T-GC-04：授權、timeout、限流與讀回未知

**輸入**：mock connector 回傳 permission denied、timeout、429／5xx、成功但 readback timeout。
**Expected**：依序輸出明確狀態 `BLOCKED`／`UNKNOWN`；exit code 非零或對應失敗出口；不執行 mutation，不盲目重試。
**Forbidden**：API success 即當完整成功、對未知 POST 自動重試、以本地 manifest 代替遠端讀回。

### T-GC-05：範圍漂移與批准不足

**輸入**：使用者只批准精確 message IDs，但 fixture／查詢回傳額外郵件。
**Expected**：額外郵件標 `BLOCKED` 或 `CONFLICT`，不處理；批准狀態仍 `NOT_REQUESTED`（本提案）。
**Forbidden**：擴大範圍、以泛稱意圖作隱含批准、觸發 move／delete／label mutation。

### T-GC-06：原子寫入與讀回

**輸入**：模擬磁碟中斷、權限錯誤、寫入後 hash 不一致。
**Expected**：不產生可宣稱提交的半成品；狀態 `UNKNOWN`／`BLOCKED`；保留暫存與錯誤證據供審查，不覆寫既有可信產物。
**Forbidden**：只看檔案存在、忽略 hash、把 `COMMITTED` 猜成 true。

## 8. 與其他責任方的邊界

### miko-core

miko-core 負責全域路由、共用狀態與治理裁決；本 Skill 只提供 gmail 領域的候選判定與證據需求。miko-core 的 `READ_ONLY_DEGRADED`、`BLOCKED`、`PAUSED_BY_USER`、批准與 adoption gate 優先於本文件；本文件不得自行解除全域封鎖、修改正式 Runtime 或宣稱生效。

### safe-implementation

safe-implementation 負責實作層的單一 writer、鎖、暫存／fsync／原子替換、讀回 hash、重跑冪等、connector timeout／錯誤封裝與非零退出。它不負責決定哪些郵件是交易、帳單、工作或已過期廣告，也不能以技術成功代替使用者批准或治理採用。本提案僅定義介面與驗收要求；候選 scripts 是否存在、是否接線為 `UNKNOWN`／`NOT_READ`。

### independent-audit

independent-audit 負責以固定 commit／來源 pin 重新讀取原始文件與產物，驗證路由不可繞過、狀態聚合、固定測題 expected／forbidden、批准範圍、逐封證據、讀回 hash 與相近不觸發反例。四視角、自我檢查、CI 綠燈或 mock PASS 均不能取代 independent audit。稽核未完成、FAIL 或 `NOT_RUN` 時，本 Skill 保持 `NOT_ADOPTED`、`READ_ONLY_DEGRADED`。

## 9. 正式採用前門檻

在下列條件全部具備前，不得改為 `ADOPTED`／`EFFECTIVE`，不得恢復 Gmail mutation 路由：

1. miko-core 明確採用批次 0／批次 1 共用契約，並固定 immutable ref、版本、ADR、HEAD 與 SHA。
2. 本提案的核心缺口以可追溯工程資產落地：逐封 manifest、thread／分頁／附件 fixture、mock connector、狀態與 exit code、七欄困難卡、operation manifest、原子寫入與讀回。
3. 所有固定測題、相近不觸發反例、授權不足、timeout、限流、部分成功、搬錯恢復、範圍漂移與重跑冪等測試均有命令、輸出、exit code、版本與 SHA；未執行者保持 `NOT_RUN`。
4. 真實 Gmail mutation 若未來要考慮，須另取得本輪精確使用者批准、逐封目標與可回復快照；本文件現階段永不自動批准。
5. safe-implementation 完成 code／artifact review，並確認不可逆與外部寫入 fail closed；無盲目重試與未知成功。
6. independent-audit 以不同檢查端完成且通過，並保留證據索引；任何 FAIL、未回覆或 `NOT_RUN` 均停在稽核站。
7. MIKO 治理完成 ADR／採用狀態裁決；固定 commit raw 讀回、冷啟動與新對話回歸均通過。
8. 正式採用後仍保留「垃圾桶清空與永久刪除由 MIKO／使用者手動處理」的不可越權邊界。

## 10. 目前結論與未驗證事項

本文件完成的是提案文字與可驗收契約的設計，任務態為**完成但有疑慮**：來源文件已讀取，但未執行真實 Gmail、mock connector、固定測題、lint、CI、independent audit、Runtime 冷啟動、外部讀回或治理採用。上述事項均為 `NOT_RUN` 或 `UNKNOWN`，不能被解讀為 PASS。

附件報告指出的核心問題與技術債已納入本提案：缺批准與恢復閘門、缺逐封識別／labels／位置／operation ID／快照、API 成功與讀回未知未封口、thread／附件／分頁／部分成功證據不足、缺狀態／困難卡／任務四態／來源 pinning／非零退出、缺原子寫入與逐封讀回，以及缺 mock／fixture 測試資產。這些內容是附件證據與候選設計，不是目前正本或 Runtime 的既成事實。

## 9. Gemini 3.5 Flash-Lite 審查採納（候選層）

本節只記錄候選修訂，不代表正式採用、Runtime 接線或治理放行。

- 共用契約要求 `task_id`、唯一 `operation_id` 與 `idempotency_key`；同鍵重跑只能唯讀查詢既有 manifest，不得重新觸發副作用。
- 重試政策採 `STOP` 或 `READBACK_ONLY`；禁止 blind retry、force override、implicit approval 與以自然語言繞過批次 0。
- 本地候選產物遵循「暫存 → flush → fsync → 原子替換 → 逐項讀回 SHA-256」生命週期；任一讀回未知即 `UNKNOWN`／`BLOCKED`。
- `NOT_READ`、`NOT_RUN`、`UNKNOWN`、`CONFLICT`、`BLOCKED`、`PARTIAL` 不得升格為 `PASS`、`COMPLETE` 或 `READY_TO_GO`。
- 本節所有工程接線、fixture、CI、independent-audit、Runtime 與外部服務結果仍為 `NOT_RUN`／`UNKNOWN`。
