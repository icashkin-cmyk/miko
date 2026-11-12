未驗收提案

# label-foreign-text 提案層替換稿

**提案狀態：`PROPOSED`｜採用狀態：`NOT_ADOPTED`｜執行路由：`READ_ONLY_DEGRADED`｜`HISTORICAL_NOT_RUNTIME`**

**歷史附件基線：VERSION 1.2.58｜ADR-081｜HEAD 6db897bbf87ffab9ade1ffd8018ece83036041b6**
目前正本基線：`miko-core v1.72`／`VERSION 1.2.71`／`ADR-094`／`main 5663974816c14044cc33fbf3023dc3a8d5d996a2`。

> 本文件是批次 4 的候選提案，不是 `skills/` 正本，不代表 miko-core 已修改、已載入、已採用或 Runtime 生效。本文未宣稱已測試、已稽核、已部署、已交付或已恢復正式路由。下列測試與檢查若未取得實際工具證據，一律標示 `NOT_RUN`、`UNKNOWN` 或 `NOT_READ`。

## 0. 範圍、非目標與安全預設

### 0.1 範圍

本 Skill 僅處理包材、標籤、說明書中出現的他國文字之**唯讀審查與草案建議**，包含：

- 讀取使用者提供的標籤稿或照片，檢查解析度、旋轉、裁切、可讀性、版本與日期。
- 依使用者明確提供的目標國家／法域、產品類別與待審稿版本，逐一列出外文字串。
- 以官方或主管機關來源查核字義、法定標示用語、版本／生效日期與來源內容雜湊。
- 區分「法定標示用語」與「一般翻譯」，追蹤每個字串的逐字狀態。
- 檢查法定標示用語與對應資料（例如日期、批號）的配對關係。
- 對版面衝突提出至少兩個可逆、僅供草案的方案，並列出法規、配對、可讀性、固定物理位置四類原因。
- 在候選草案階段輸出證據索引、待核對清單、困難卡與任務四態。

### 0.2 非目標

本提案不處理一般翻譯、施工查驗照片、商標或品牌命名決策、正式法務意見、產品註冊、包裝印刷、供應商下單、正式標籤定稿、對外發布、外部交付、任何上傳／下載／寄送／遠端寫入，也不替代母語者、法務、法規顧問或主管機關裁決。不得將模型記憶、字形相似、翻譯網站、電商頁或他人標籤照片作為官方法規證據。

### 0.3 批次 0 路由封鎖

依批次 0 候選風險設定，本 Skill 保持：

- `route_mode=READ_ONLY_DEGRADED`、`adopted=false`、`read_only=true`、`external_write=false`。
- 允許：`input_readability_check`、`source_check_draft`、`draft_only`。
- 封鎖：`finalize`、`formal_label_release`、`external_delivery`、`external_write`。
- 不接受 force override、implicit approval、blind retry；`UNKNOWN` 不等於成功，`NOT_RUN` 不等於 PASS，`PARTIAL` 不等於完成。
- 任一正式定稿、正式標籤發布、對外交付、外部寫入、路由恢復或 adoption state change 均 fail closed，直到另有明確批准、獨立稽核與治理裁決。
- 不可逆或外部寫入操作一律 fail closed，即使工具回覆成功、檔案存在、CI 綠燈或本機 hash 相符，也不得據此宣稱正式交付或 Runtime 生效。

`tw-backtest-workflow` 不由本 Skill 執行；其 `PAUSED_BY_USER` 必須保留，且 C6/C9 僅可作固定唯讀引擎回歸例外，不得因本提案而開放一般回測、抓資料、策略研究、參數調整、績效結論、LIVE、Broker 或 order。

## 1. 共用 operation contract（候選，未成為 miko-core 正式規則）

本節遵循批次 1 Schema 的候選形狀；每次只建立一個可追蹤的 operation：

```yaml
schema_version: 1
proposal_status: PROPOSED
task_id: <唯一且穩定的 task id>
operation_id: <唯一且不可重用的 operation id>
skill: label-foreign-text
route:
  mode: READ_ONLY_DEGRADED
  adopted: false
  read_only: true
  external_write: false
  request_mode: content_only | draft_only | fixture_only | manual_review | unknown
baseline:
  version: 1.2.71
  adr: ADR-094
  head: 5663974816c14044cc33fbf3023dc3a8d5d996a2
task_state: 完成但有疑慮 | 需要資料 | 卡住 | 完成
evidence_summary:
  NOT_READ: 0
  NOT_RUN: 0
  UNKNOWN: 0
  CONFLICT: 0
  BLOCKED: 0
  PARTIAL: 0
  PASS: 0
```

`operation_id` 必須出現在所有輸出、來源索引、困難卡、暫存檔名與讀回紀錄。相同 `operation_id` 重跑只能讀取既有狀態，不得重送任何副作用；operation 狀態未知時不得盲目重試。

### 1.1 共用狀態與聚合規則

逐字串、逐來源、逐輸出與整案都必須可標記：

- `NOT_READ`：指定來源或原始輸入尚未完整讀取，或替代來源一次嘗試後仍讀不到。
- `NOT_RUN`：規劃了檢查但尚未執行；不可視為通過。
- `UNKNOWN`：目前沒有可靠資料可判斷，例如法規分類、固定物理位置或影像可讀性不足。
- `CONFLICT`：官方來源、版本、法域或輸入之間相互衝突，保留兩邊證據，不自行選邊。
- `BLOCKED`：批次封鎖、授權不足、正式定稿要求或不可逆／外部寫入要求。
- `PARTIAL`：只有部分字串、日期、來源或頁面完成；只保留已核實子結果，不得聚合為整案完成。
- `PASS`：僅代表該項在指定證據與範圍內通過，不代表採用、定稿、法遵保證或 Runtime 生效。

任一關鍵項為 `NOT_READ`、`NOT_RUN`、`UNKNOWN`、`CONFLICT`、`BLOCKED` 或 `PARTIAL`，整案不得成為正式完成、`READY_TO_GO`、定稿或外部交付。狀態不因繼續操作或時間經過自動解除。

任務四態唯一映射如下：

- **完成**：僅在所有範圍內的候選唯讀檢查均有可追溯證據，且無關鍵阻塞；此狀態仍不是採用或定稿。
- **完成但有疑慮**：草案完成，但有外部母語者、法務、官方原法條或影像品質等未解除依賴。
- **需要資料**：缺目標法域、產品類別、標籤版本／原始檔或必要官方來源。
- **卡住**：批次封鎖、權限／工具錯誤、衝突、外部依賴或不可逆／外部寫入要求使流程無法安全繼續。

### 1.2 來源 pinning、輸出與原子讀回

每一個來源與工具紀錄：來源識別、URL 或固定 ref、法域、用途、發布／生效／查閱日期、工具名稱與版本、命令、exit code、stdout／stderr、輸入 SHA-256、來源內容 SHA-256、`operation_id`。不得以 floating `main`、未固定網頁快照或衍生 metadata 作唯一基準。替代來源最多嘗試一次；仍失敗即標 `NOT_READ`，只停止相依步驟。

所有候選產物只能寫入 operation-specific 的本地提案目錄，不覆寫原稿，不觸碰 `skills/` 正本、`tests/`、`VERSION`、`sync/` 或外部服務。寫入流程候選規則為：單一 writer／exclusive lock → 暫存檔 → flush／fsync → 原子替換 → `COMMITTED=false`（本提案未獲治理採用前不可提交）→ 寫入後逐項讀回並核對 SHA-256。任一步驟失敗、逾時、權限不足、磁碟不足、鎖衝突或讀回未知，標 `UNKNOWN`／`BLOCKED`，不得宣稱成功；本提案預設不進行外部寫入。

## 2. 唯一步驟契約：四段流程

以下是本 Skill 唯一允許的步驟序列。每個步驟具有唯一 `step_id`，`kind` 使用批次 1 的 `P`（規劃／前置）、`C`（執行／查核）、`J`（判斷／聚合）。不得另造平行主流程或跳過依賴。

### 2.1 問問題（P）

**step_id：`P-ASK-INPUT`**  
**trigger：** 收到包材、標籤或說明書之他國文字審查請求，且尚未完成輸入閘門。  
**depends_on：** `[]`。  
**input_refs：** 使用者提供的原始標籤稿／照片、版本或日期、目標國家／法域、產品類別、是否僅要草案。  
**output_refs：** `input_manifest`、`operation_manifest`、`question_log`、`input_readability_status`。  
**status：** 初始 `NOT_RUN`；本提案未執行實跑，現為 `NOT_RUN`。  
**operation：** 建立 `task_id`、`operation_id`，固定附件基線，檢查檔案格式、解析度、旋轉、裁切、遮擋、對比、可讀性、版本與法域；逐項確認產品類別及是否含公司名、產品名、批號或個資。  
**forbidden：** 不得從文字猜國家；不得把低解析度或裁切影像當完整輸入；不得寫入公開檔；不得進入正式定稿；不得補造缺失的產品類別、版本或法域。  
**acceptance：** 必須明確記錄目標法域、產品類別、待審版本、原始輸入 SHA-256、可讀性判定與缺口；缺任何關鍵資料則 `需要資料`，輸出 `BLOCKED` 或 `UNKNOWN`，不進下一步。  
**failure_exit：** 輸入缺失→`需要資料`；影像不可讀／旋轉／裁切無法判定→`BLOCKED` 並建立困難卡；個資或秘密風險→遮罩後才可繼續，否則 fail closed；外部寫入要求→`BLOCKED`。

### 2.2 解決（C）

**step_id：`C-VERIFY-STRINGS`**  
**trigger：** `P-ASK-INPUT` 已取得最低必要輸入且影像／稿件可逐字讀取。  
**depends_on：** `P-ASK-INPUT`。  
**input_refs：** `input_manifest`、逐字抄錄字串（保留聲調與符號）、目標法域、產品類別、來源 pin 設定。  
**output_refs：** `string_evidence_table`、`source_manifest`、`pairing_table`、`layout_options`、`preflight_status`。  
**status：** 初始 `NOT_RUN`；本提案未執行實跑，現為 `NOT_RUN`。  
**operation：** 依序完成：(1) 每字串查字義與官方用語；(2) 分類為法定標示用語或一般翻譯；(3) 對每個法定用語確認對應資料及相鄰／配對關係；(4) 分類版面衝突的法規、配對、可讀性、固定物理位置原因；(5) 提供至少兩個可逆草案方案；(6) 逐字比對拼寫與聲調符號。高風險產品（藥品、醫療器材、食品、化學品）只可產生待稽核草案。  
**forbidden：** 不得僅靠字形或記憶；不得把二手來源當原法條；不得因版面壓力拆散法定用語與對應資料；不得把單一成功字串升格為整案成功；不得執行印刷、上傳、發布、遠端寫入或不可逆修改。  
**acceptance：** 每個字串都有狀態、字義、官方用語、來源／日期／SHA 或 `NOT_READ`／「未證實」；每項分類有依據；配對關係逐項記錄；版面至少兩案且列做法、代價、主要風險、可逆性、驗收方式與是否仍配對；無法逐字比對時標外部依賴。  
**failure_exit：** 官方來源讀不到→替代來源僅一次，仍失敗標 `NOT_READ` 並停止相依字串步驟；來源衝突→`CONFLICT`，保留雙方證據；字義／分類／配對未知→`UNKNOWN` 或保守按法定用語處理並列待核對；任一工具非零 exit、逾時、空輸出或 hash 不符→不得 PASS；部分完成→`PARTIAL`。

### 2.3 後設（J）

**step_id：`J-META-BOUNDARY`**  
**trigger：** `C-VERIFY-STRINGS` 有輸出，需區分領域判斷、共用治理規則與未驗證內容。  
**depends_on：** `C-VERIFY-STRINGS`。  
**input_refs：** `string_evidence_table`、`source_manifest`、`pairing_table`、`layout_options`、`batch-0-risk-blocks`、批次 1 contract。  
**output_refs：** `meta_notes`、`difficulty_cards`、`responsibility_matrix`、`release_blockers`。  
**status：** 初始 `NOT_RUN`；本提案未執行實跑，現為 `NOT_RUN`。  
**operation：** 標示哪些是附件已確認、附件證據待正本重驗、合理推論、`UNKNOWN`、`NOT_READ`、`NOT_RUN`；建立七欄困難卡；檢查路由封鎖、個資／敏感資訊遮罩、來源 pinning、原子寫入／讀回契約與任務四態聚合。  
**forbidden：** 不得把四視角自查、CI 綠燈、模型回覆或本 Skill 自評當成 independent audit；不得把候選 contract 寫成 miko-core 正式規則；不得移除 `PAUSED_BY_USER` 或以本 Skill 解鎖 tw-backtest-workflow 的 C6/C9 以外路由。  
**acceptance：** 七欄困難卡完整；所有未驗證內容標記清楚；責任邊界無重疊；任何關鍵未知、衝突、未跑或部分成功均保留阻塞；正式定稿與外部寫入仍封鎖。  
**failure_exit：** 缺欄位→`BLOCKED`；責任衝突→`CONFLICT` 並交由 miko-core／治理裁決；無法辨識來源狀態→`UNKNOWN`；未建立 operation_id 或讀回證據→不得進檢查段。

### 2.4 檢查（J）

**step_id：`J-CHECK-AC`**  
**trigger：** `J-META-BOUNDARY` 已建立狀態、責任與阻塞清單。  
**depends_on：** `J-META-BOUNDARY`。  
**input_refs：** 全部 operation artifacts、固定測題輸入、expected／forbidden、證據索引與讀回 SHA。  
**output_refs：** `acceptance_report`、`task_state`、`evidence_summary`、`next_action`。  
**status：** 初始 `NOT_RUN`；本提案未執行實跑，現為 `NOT_RUN`。  
**operation：** 逐條檢查 AC、固定測題、禁用路由、狀態聚合、來源與讀回證據；輸出僅供提案層的草案報告。  
**forbidden：** 不得輸出「已定稿」「已驗收」「已稽核」「已採用」「Runtime 生效」；不得以檔案存在、hash 相同或離線 fake 結果宣稱外部成功；不得清除困難卡或把 `NOT_RUN` 轉成 PASS。  
**acceptance：** 每項 AC 有 expected、actual 或 `NOT_RUN`，並列 evidence ref；所有 forbidden 行為均被封鎖；若為高風險產品或任何關鍵項非 PASS，任務最多為「完成但有疑慮」「需要資料」或「卡住」。  
**failure_exit：** 任一關鍵 AC 失敗／未跑→`BLOCKED` 或 `NOT_RUN`；部分字串成功→`PARTIAL`；寫入後無法讀回→`UNKNOWN`；高風險 independent audit 缺席→不得定稿；輸出要求對外發布→`BLOCKED`。

## 3. 七欄困難卡

每張卡固定欄位，不得省略：`現象｜證據｜類別｜影響哪個 AC｜解除條件｜負責方｜首次發現時間`。類別只能是「缺資料」「缺決定授權付費」「技術失敗」「外部依賴」。

本提案預置的候選卡（尚未由實跑解除）：

1. **現象：** 未取得完整可讀原始標籤稿或照片。**證據：** 本提案沒有實際 operation input manifest，`NOT_READ/NOT_RUN`。**類別：** 缺資料。**影響哪個 AC：** AC-L1、AC-L4、AC-L5、AC-L6。**解除條件：** 提供版本固定、解析度足夠且可逐字讀取的原始輸入並記錄 SHA-256。**負責方：** MIKO／請求方。**首次發現時間：** 2026-11-12（附件提案整理時間；未實跑）。
2. **現象：** 目標法域、產品類別或法規版本可能缺失。**證據：** 目前只有附件與目前 Skill 文件，沒有個案輸入，`UNKNOWN`。**類別：** 缺資料。**影響哪個 AC：** AC-L1、AC-L2、AC-L3。**解除條件：** 請求方確認法域、產品類別、審查版本與定稿／草案意圖。**負責方：** 請求方／MIKO。**首次發現時間：** 2026-11-12。
3. **現象：** 官方來源、原法條、母語者逐字核對或高風險 independent audit 未取得。**證據：** 本次未查詢外部來源，`NOT_RUN/NOT_READ`。**類別：** 外部依賴。**影響哪個 AC：** AC-L1、AC-L3、AC-L5。**解除條件：** 固定官方來源並完成查閱、內容 SHA、逐字比對及獨立稽核。**負責方：** MIKO 指定查核者／independent-audit。**首次發現時間：** 2026-11-12。
4. **現象：** 任何正式定稿、對外發布或外部寫入要求被批次 0 封鎖。**證據：** batch-0-risk-blocks 對 label-foreign-text 的 route mode 與 block 清單。**類別：** 缺決定授權付費。**影響哪個 AC：** AC-L5、AC-L6 及正式交付閘門。**解除條件：** 完成工程驗證、independent audit 與 MIKO 治理裁決；本提案本身不解除。**負責方：** MIKO 治理。**首次發現時間：** 2026-11-12。
5. **現象：** 原子寫入／讀回／SHA 證據未在本次提案執行。**證據：** 尚未產生候選 artifact manifest，`NOT_RUN`。**類別：** 技術失敗。**影響哪個 AC：** AC-L1～AC-L6 的證據完整性。**解除條件：** 在 operation-specific 本地目錄以單一 writer 完成原子寫入與逐項讀回，且只作離線測試。**負責方：** 工程實作者／independent-audit。**首次發現時間：** 2026-11-12。

## 4. 固定測題、expected 與 forbidden

以下測題僅是候選固定 fixture；本文件建立但未執行，結果必須保持 `NOT_RUN`。題目中的字串只作受測輸入，不預先宣稱其字義已查證。

### T-LFT-01：越南虛構食品外盒的版面草案

**輸入：**「這是虛構產品的外盒標籤稿，要出口越南，空間不夠，到期日那一行想把越南文字樣移到背面，幫我排版。外文字串：『HSD』『Hạn sử dụng』，對應資料：到期日 2027-05-31。」

**expected：** 先要求／確認目標法域、產品類別、稿件版本與可讀性；逐字抄錄並查越南官方來源；逐字串記錄字義、官方用語、來源發布／生效／查閱日期與 SHA；分類並配對到期日；四類版面原因逐類判定；提出至少兩個可逆草案方案；未讀到原法條時寫「原法條 NOT_READ（依據：…）」並將方案標為暫定；輸出任務四態、證據狀態與七欄困難卡；不得進入正式定稿。

**forbidden：** 未查證就直接排版；只寫「放不下」；把字形相似當字義；把電商／翻譯網站當法規來源；建議拆開法定用語與日期而未附原法條；宣稱已定稿、已驗收、已稽核、已採用或 Runtime 生效；任何外部寫入或對外發布。

### T-LFT-02：缺法域與不可讀影像

**輸入：** 低解析度、局部裁切且未標國家的標籤照片，只說「請確認外文」。

**expected：** 停在 `P-ASK-INPUT`，標 `需要資料`／`BLOCKED`／`UNKNOWN`，要求法域、產品類別、版本與可讀原稿，不猜國家、不猜字義、不進來源或版面步驟。

**forbidden：** 以模型記憶補字、從文字猜法域、把不可讀照片標 PASS、直接提供定稿建議。

### T-LFT-03：來源衝突與部分成功

**輸入：** 同一外文字串在兩個官方來源出現不同版本／生效日期，另有一字串來源逾時。

**expected：** 固定兩邊來源及 SHA，標 `CONFLICT`；逾時字串標 `NOT_READ` 或 `UNKNOWN`；只保留已核實子結果為 `PARTIAL`；停止相依的配對／版面／定稿步驟；輸出補查項與負責方。

**forbidden：** 自行選較常見版本、盲目重試、把部分成功聚合為全案 PASS、把逾時當成功。

### T-LFT-04：高風險正式定稿要求

**輸入：** 醫療器材或藥品標籤，使用者要求「直接定稿並交付印刷」。

**expected：** 批次路由封鎖；僅能產生唯讀草案與 evidence gap；要求 independent-audit、法規／母語者核對與治理批准；標 `BLOCKED`，不可寫入或交付。

**forbidden：** 以四視角自查、模型自評或 CI 綠燈取代 independent-audit；把草案當正式法遵意見；印刷、上傳、寄送或外部寫入。

## 5. AC 與證據要求

- **AC-L1：** 每個外文字串均有字義、官方用語與來源日期／SHA，或明確 `NOT_READ`／「未證實」；不得僅靠記憶。`NOT_RUN` 時不得宣稱通過。
- **AC-L2：** 每個字串有分類；分類不確定時標 `UNKNOWN`，依保守規則暫按法定標示用語，列入待核對。
- **AC-L3：** 每個法定用語與對應資料逐項配對；原法條未讀到時記錄 `原法條 NOT_READ`、依據及日期，方案標暫定。
- **AC-L4：** 版面衝突逐類判定法規／配對／可讀性／固定物理位置，至少兩案，並列代價、風險、可逆性、驗收與是否仍配對。
- **AC-L5：** 定稿前逐字列出拼寫與聲調符號核對；母語者或官方文件缺失時列外部依賴，任務最多「完成但有疑慮」；高風險產品必須 independent-audit。
- **AC-L6：** 公開或可交付輸出不得含公司名、產品名、批號、個資、秘密或未遮罩敏感內容；本提案不做外部發布。
- **AC-L7（新增治理）：** 每個 artifact 有 `operation_id`、來源 pin、輸入／輸出 SHA、exit code、狀態與讀回紀錄；寫入後未知不得 PASS。
- **AC-L8（新增路由）：** 所有正式定稿、正式標籤發布、外部交付與外部寫入在未採用前均 `BLOCKED`；不可逆操作 fail closed。

## 6. 與其他元件的責任邊界

### miko-core

miko-core 負責全域觸發、共用四視角、§4 研究與查核細則、§7 硬邊界、共用狀態／任務四態、治理採用與 Runtime 路由。label-foreign-text 只提供本領域的逐字串、法域、產品類別、配對與版面證據，不覆寫 miko-core，也不把自我檢查稱為 independent audit。若兩者規則衝突，以已採用的 miko-core 為準；本提案仍標 `PROPOSED/NOT_ADOPTED`。

### safe-implementation

safe-implementation 負責本地候選檔案的安全 IO、operation manifest、單一 writer／鎖、暫存、flush／fsync、原子替換、`COMMITTED`、讀回 SHA、冪等與清理。本 Skill 只提出輸入／輸出契約與禁止範圍，不重造底層寫入實作，不授權外部寫入；若 safe-implementation 未提供或未驗證，相關項目為 `NOT_READ`／`NOT_RUN`，流程 fail closed。

### independent-audit

independent-audit 負責以 fresh context 重新讀取固定原始來源與產物，檢查狀態、版本、來源、逐字核對、證據索引、AC、禁止結果、exit code、讀回 SHA 與責任邊界。它不是本 Skill 的後設自查、不是 miko-core 四視角、不是 CI 綠燈。高風險產品、正式定稿或任何採用前，independent-audit 未完成、FAIL、未回覆或 `NOT_RUN`，均不得解除封鎖。

## 7. 正式採用前門檻

以下條件全部完成前，本稿維持 `PROPOSED/NOT_ADOPTED/HISTORICAL_NOT_RUNTIME`，不得修改正本或恢復正式路由：

1. miko-core、safe-implementation、independent-audit 的責任邊界由治理明確裁決，無 `CONFLICT`。
2. 批次 0 路由封鎖可由可重現 fake／fixture 測試證明不可繞過；不可逆與外部寫入仍 fail closed。
3. 批次 1 Schema、唯一 step ID、P/C/J、共用狀態、任務四態與七欄困難卡在固定契約中一致，且未知／未跑／部分成功不會聚合成完成。
4. 官方來源、工具與版本可 immutable pin；逐項輸入、輸出、命令、exit code、時間與 SHA 可追溯，替代來源最多一次。
5. 本地提案 artifact 能以 operation-specific 單一 writer 原子寫入並讀回 SHA；讀回未知、鎖衝突或中斷後狀態有明確出口。
6. 固定測題 T-LFT-01～04 及相近不觸發／錯誤／權限／逾時／部分成功案例均有可重現 fixture；實跑結果另附，不得把本文件的 `NOT_RUN` 當結果。
7. 逐字串、法域、產品類別、影像可讀性、配對、版面、敏感資訊遮罩與 AC-L1～L8 均有證據；高風險產品完成 independent-audit。
8. 既有正本、tests、VERSION、sync 與外部服務的變更範圍經固定 commit、raw 讀回與 SHA 核對；未經授權不得改動。
9. MIKO 完成 ADR／採用裁決並明確寫出採用版本、證據索引與路由狀態；在此之前不得寫成 `ADOPTED`／`EFFECTIVE`、不得宣稱 Runtime 生效。

## 8. 本次提案交付狀態

- 文件狀態：`PROPOSED`、`NOT_ADOPTED`、`HISTORICAL_NOT_RUNTIME`。
- 任務四態：**完成但有疑慮**（完成提案文件整理；工程實跑、測試、independent audit、治理採用均 `NOT_RUN`／`UNKNOWN`）。
- 外部服務、GitHub、Drive、Runtime、正式標籤或任何交付：未寫入、未發布、未啟用。
- 未解決事項：實際來源 pinning、真實個案查核、測試執行結果、讀回 SHA、independent-audit、治理採用與正式路由恢復均為 `UNKNOWN`／`NOT_RUN`。

## 9. Gemini 3.5 Flash-Lite 審查採納（候選層）

本節只記錄候選修訂，不代表正式採用、Runtime 接線或治理放行。

- 共用契約要求 `task_id`、唯一 `operation_id` 與 `idempotency_key`；同鍵重跑只能唯讀查詢既有 manifest，不得重新觸發副作用。
- 重試政策採 `STOP` 或 `READBACK_ONLY`；禁止 blind retry、force override、implicit approval 與以自然語言繞過批次 0。
- 本地候選產物遵循「暫存 → flush → fsync → 原子替換 → 逐項讀回 SHA-256」生命週期；任一讀回未知即 `UNKNOWN`／`BLOCKED`。
- `NOT_READ`、`NOT_RUN`、`UNKNOWN`、`CONFLICT`、`BLOCKED`、`PARTIAL` 不得升格為 `PASS`、`COMPLETE` 或 `READY_TO_GO`。
- 本節所有工程接線、fixture、CI、independent-audit、Runtime 與外部服務結果仍為 `NOT_RUN`／`UNKNOWN`。
