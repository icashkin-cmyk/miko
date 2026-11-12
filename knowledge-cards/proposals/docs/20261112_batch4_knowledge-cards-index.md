# 2026-11-12 批次 4：Skill 修復提案總體執行清單與知識卡索引

> **文件性質：未驗收的批次索引與執行清單。**
>
> 本文件只彙整 `/home/ubuntu/work-miko-audit/knowledge-cards/proposals/` 下的提案結果，不修改任何 `skills/` 正本、Runtime、外部服務、帳號卡、Drive、Git、CI 或正式交付物。
>
> 十份文件目前均為 `PROPOSED`／`NOT_ADOPTED`／`HISTORICAL_NOT_RUNTIME` 之類的未採用狀態。以下內容不得解讀為已採用、已測試、已稽核、已部署、已載入或已恢復正式路由。任何工程接線、固定測題、冷啟動、independent-audit、治理批准與 Runtime 行為，除提案結果明示已做的檔案層唯讀檢查外，均維持 `NOT_RUN`、`NOT_READ` 或 `UNKNOWN`。

## 1. 批次總體裁決與硬性門檻

### 1.1 全批次共同門檻

1. **批次 0：READ_ONLY_DEGRADED／PAUSED_BY_USER 優先。** 各 Skill 的批次 0 路由封鎖以其提案中的具體白名單為準；不可逆操作、外部寫入、正式交付、公開發布、交易或安全結論一律 `fail closed`。
2. **批次 1 只是一組候選共用規格。** 包含共用證據狀態、任務四態、七欄困難卡、唯一 `step_id`、P/C/J、唯一 `operation_id`、四段流程、部分成功聚合與相依停止規則；尚未證明已接入 `miko-core` 或任何正式 Runtime。
3. **不得把未知或部分成功升格為完成。** `NOT_READ`、`NOT_RUN`、`UNKNOWN`、`CONFLICT`、`BLOCKED`、`PARTIAL` 均不可自動聚合為 `PASS`、`COMPLETE` 或 `READY_TO_GO`。
4. **外部或不可逆行為必須有明確批准。** 需要精確範圍、批准原話、目標、操作清單、回復方式、冪等／重入策略、固定來源與工具 pin、原子提交、`COMMITTED` 證據、寫入後讀回與 hash；任一項未知即停止。
5. **固定保留回測封鎖。** `tw-backtest-workflow` 維持 `PAUSED_BY_USER`；只保留 C6/C9 固定唯讀回歸例外，不得作策略研究、交易、績效或投資解讀。
6. **正式採用前的共同驗收。** 須完成 fake／fixture、正常與失敗路徑、授權／限流／逾時／部分成功／來源衝突案例、固定測題 expected／forbidden、safe-implementation、independent-audit、固定 commit/raw 讀回、逐檔或產物 SHA、冷啟動／新對話回歸及 MIKO 治理裁決。

### 1.2 目前不可宣稱事項

- 不得宣稱十份提案已修改正本、已採用或已生效。
- 不得宣稱任何提案已接上正式 Runtime、路由已恢復、外部服務已驗證或外部寫入已完成。
- 不得以附件中的歷史 PASS、既有測試或候選腳本存在性取代本輪可重現的驗收證據。
- 不得以本索引取代各 Skill 的專用測題、責任邊界、來源證據或治理裁決。

## 2. 建議依賴順序與總體執行清單

以下順序是**待治理批准後**的候選執行順序，不代表已執行。每一站完成前，依賴它的後續站不得宣稱通過。

### Stage 0：治理與狀態基線（所有 Skill 的前置）

- 鎖定附件基線 `VERSION 1.2.58`／`ADR-081`／`HEAD 6db897bbf87ffab9ade1ffd8018ece83036041b6`，並以 immutable ref、raw 讀回及 SHA 證明來源。
- 先由 MIKO 治理裁決本批次候選共用契約是否可進入實作；未裁決前只保留提案層。
- 定義並機械化共用 enum、任務四態、七欄困難卡、`step_id`／P-C-J、`operation_id`、來源 pinning、相依停止、非零退出、原子寫入、`COMMITTED` 與讀回 hash。
- 確認 `miko-core`、`safe-implementation`、`independent-audit` 的正本、接線責任與不重疊邊界；目前均有不同程度 `UNKNOWN`／`NOT_READ`／`NOT_RUN`。

### Stage 1：共用唯讀契約與安全閘門

候選先處理：`make-skill`、`multi-agent-coordination-engine`、`grilling`。

- 先驗證批次 0 路由、批准邊界、單一 writer、並行上限、fresh context、重入／重試上限與不得委派事項。
- 建立 fake／fixture 與固定測題，確認未知、衝突、部分成功、使用者停止、授權不足及相依停止不會聚合成完成。
- 特別確認 `grilling` 不會把自身檢查誤當 independent audit，且多代理協調不會越過治理與 writer 邊界。

### Stage 2：來源、媒體與安全查核類

候選先處理：`label-foreign-text`、`visual-content-intelligence`、`photo-inspection-log`、`tw-alert-check`。

- 建立來源內容／原始檔／工具版本／命令／exit code／查閱時間／SHA 的完整證據鏈。
- 先完成輸入可讀性、法域／產品／標籤版本、URL-only、個資與照片替換／壞圖等阻擋測題。
- 固定逐來源、逐日期、逐地點、逐時區及衝突處理；部分來源成功不得形成完整安全結論。
- 對 `photo-inspection-log` 另外驗證 manifest、圖片與列對應、xlsx/PDF round-trip、checkpoint、原子寫入及讀回。

### Stage 3：受限領域操作流程

候選先處理：`dghp-travel`、`gmail-cleanup`。

- 先完成範圍、批准、逐項證據、恢復方式與外部寫入封鎖測試。
- `dghp-travel` 維持固定 `READ_ONLY_DEGRADED`；不得進入 `READY_TO_GO`、`real_trip_release`、booking、payment、navigation 或 external write。
- `gmail-cleanup` 維持所有 move／delete／label mutation／unsubscribe／send／reply／schedule 等封鎖；需補足 thread、附件、分頁、label 快照、逐封讀回與搬錯恢復 fixture。
- 住宿、交通、餐飲、返程、郵件部分成功與範圍漂移均須有相依停止與已核實／未核實證據傳播。

### Stage 4：回測封鎖與固定回歸

- `tw-backtest-workflow` 僅驗證 `PAUSED_BY_USER` 優先、C6/C9 唯讀固定回歸、旗標 XOR、manifest／hash、PIT／look-ahead、schema、成本／基準、事件與固定錯誤出口。
- 禁止抓新資料、一般回測、策略比較、交易路由或投資式解讀。
- 任何歷史實跑或附件 PASS 均須在目前 checkout 以固定 commit/raw／SHA 重新讀回後，才可作為待審證據；目前仍 `NOT_RUN`。

### Stage 5：獨立稽核、冷啟動與治理採用

- 對十份提案逐一執行專用測試與固定測題，保存命令、exit code、產物、讀回 hash 及失敗路徑。
- 由 independent-audit 在 fresh context 重讀提案、正本／接線與證據，不得由 Skill 自身的 J 段或四視角 PASS 取代。
- 完成冷啟動／新對話回歸，確認狀態不會遺失、不會誤恢復路由，且 `PAUSED_BY_USER` 與批次 0 封鎖優先。
- MIKO 治理須另行裁決是否採用、採用哪些部分、是否保留 `READ_ONLY_DEGRADED`／`PAUSED_BY_USER`；裁決前維持本索引所有未採用聲明。

## 3. 十份提案知識卡索引

### 3.1 dghp-travel

- **提案路徑：** `knowledge-cards/proposals/skills/20261112_batch4/01-dghp-travel/SKILL.md`
- **狀態：** `PROPOSED_NOT_ADOPTED`；歷史／提案層，不是 Runtime 證據。
- **批次門檻：** 批次 0 固定 `READ_ONLY_DEGRADED`；封鎖 `READY_TO_GO`、`real_trip_release`、booking、payment、navigation、external_write。批次 1 的共用狀態、四態、七欄卡、`operation_id`、四段流程及部分成功聚合均僅為候選。正式採用前須完成 fake／fixture、來源 pinning、原子寫入、讀回 SHA、independent-audit、固定回歸、冷啟動與治理裁決。
- **依賴順序：** Stage 0 共用契約 → Stage 2 來源／日期／地點證據 → Stage 3 交通／住宿／餐飲／返程閉環 → Stage 5 稽核與治理。
- **未解決項：** 住宿契約仍缺入住／退房／行李／跨日／取消／房況未知；工具的原子輸出、既有輸出政策、讀回 SHA、磁碟滿／權限／中斷狀態未驗證；`food_pool` 的 PENDING 聚合、行程 URL 內容 hash／版本／衝突、個資最小化與逐段來源／快照 hash 未閉合；正本未修改，工程、外部來源與 Runtime 均未驗證。
- **下一站：** 治理批准後建立受限 fake／fixture 與行程閉環固定測題；在此之前只可維持提案層與唯讀封鎖。

### 3.2 gmail-cleanup

- **提案路徑：** `knowledge-cards/proposals/skills/20261112_batch4/02-gmail-cleanup/SKILL.md`
- **狀態：** `PROPOSED_NOT_ADOPTED_VERIFIED_WRITE`；此處的 verified write 僅指提案檔層級結果，不代表 Gmail 或 Runtime 寫入。
- **批次門檻：** 批次 0 `READ_ONLY_DEGRADED`，封鎖 move、delete、permanent_delete、label mutation、unsubscribe、send、reply、schedule 及 external_write。批次 1 的狀態、四態、七欄卡與 operation contract 尚未採用；正式採用前須完成 fake／fixture、固定測題、safe-implementation、independent-audit、固定 commit raw 讀回與冷啟動／新對話回歸。
- **依賴順序：** Stage 0 → Stage 1 共用安全契約 → Stage 3 Gmail 唯讀證據與恢復 fixture → Stage 5。
- **未解決項：** 缺完整 operation manifest、冪等 ID、單一 writer、原子寫入與逐封讀回 SHA；thread 全成員、正文／HTML、附件、label 快照、分頁、授權／timeout／部分成功／搬錯恢復未由 fixture 驗證；connector、授權、mutation、遠端讀回、固定測題、lint、CI、治理及 Runtime 均 `UNKNOWN`／`NOT_RUN`。
- **下一站：** 先完成唯讀 connector fixture 與可回復快照 schema；未獲精確批准前不得嘗試任何 Gmail mutation。

### 3.3 grilling

- **提案路徑：** `knowledge-cards/proposals/skills/20261112_batch4/03-grilling/SKILL.md`
- **狀態：** `PROPOSED/NOT_ADOPTED/HISTORICAL_NOT_RUNTIME`。
- **批次門檻：** 批次 0 只允許 `manual_question_round`、`proposal_output`、`readonly_source_review`；封鎖 formal delivery、auto consensus、delegated write、external write。批次 1 共用狀態、四態、七欄卡、`operation_id` 與 `GRL-READONLY-001` 僅為候選；須完成 fake／fixture、固定測題、來源 pin、原子寫入／讀回、independent-audit、固定 commit/raw/SHA 與治理裁決。
- **依賴順序：** Stage 0 → Stage 1 多代理／問題輪次契約 → Stage 5。
- **未解決項：** 缺可執行 step ID、P/C/J、輸入輸出、驗收與失敗出口；候選 `contracts.py`、`artifact_io.py`、`gates.py`、`source_pin.py` 的存在與接線未驗證；缺正常／失敗／部分成功／未知／授權不足／相近反例；未證明 operation manifest、單一 writer、atomic commit、讀回 SHA 與遠端／Runtime 證據鏈。
- **下一站：** 先把每輪最多五題、依賴排序、停止條件、fresh context 與非觸發反例轉成可重現 fixture；禁止以自我檢查代替 independent audit。

### 3.4 label-foreign-text

- **提案路徑：** `knowledge-cards/proposals/skills/20261112_batch4/04-label-foreign-text/SKILL.md`
- **狀態：** `PROPOSED_NOT_ADOPTED_HISTORICAL_NOT_RUNTIME`。
- **批次門檻：** 批次 0 只允許 input readability check、source check draft、draft only；封鎖 finalize、formal label release、external delivery、external write。批次 1 的 schema、task／operation ID、P/C/J、六種證據狀態、四態與七欄卡為候選；須完成來源／工具 pin、fake／fixture、原子寫入與讀回 SHA、independent-audit 與治理裁決。
- **依賴順序：** Stage 0 → Stage 2 輸入可讀性／法域／官方來源 → Stage 5。
- **未解決項：** 原 Skill 只有 SKILL.md，scripts、README、ACCEPTANCE、fixtures、專測未驗證；v0.1 與專案版本並置；缺 operation_id、來源 pinning、原子寫入、讀回 SHA、冪等重跑、個資／敏感資訊遮罩及錯誤／逾時／權限／CONFLICT／PARTIAL 測試；真實來源與 Runtime 未驗證。
- **下一站：** 先建立輸入可讀性與標籤版本／法域 fixture，明確把草稿檢查與正式標籤發布分離。

### 3.5 make-skill

- **提案路徑：** `knowledge-cards/proposals/skills/20261112_batch4/05-make-skill/SKILL.md`
- **狀態：** `PROPOSED_NOT_ADOPTED_HISTORICAL_NOT_RUNTIME`。
- **批次門檻：** 批次 0 僅允許 local lint design、readonly review、proposal output；封鎖 git push、Drive DELTA、account card write、runtime enable、public publish。不可逆／外部寫入一律 fail closed；回測仍 `PAUSED_BY_USER`，只留 C6/C9。批次 1 與正式採用門檻同 Stage 0／1／5。
- **依賴順序：** Stage 0 → Stage 1 共用操作契約 → Stage 5（再考慮任何 Git／Drive／帳號卡／Runtime 行為）。
- **未解決項：** S9-S11 的批准、目標、回復、固定 commit、讀回契約不足；push／CI pending／Drive 讀回 timeout／帳號卡未生效未知未封口；S7／S10／S11 缺 manifest、預期 SHA、重跑及部分成功矩陣；版本／歷史基準與六欄／七欄語義有衝突；候選 scripts 與正本接線未驗證。
- **下一站：** 先完成唯讀 manifest／SHA／非零退出與回復設計；治理明確批准前，禁止 push、Drive、帳號卡、Runtime enable 或 route restore。

### 3.6 multi-agent-coordination-engine

- **提案路徑：** `knowledge-cards/proposals/skills/20261112_batch4/06-multi-agent-coordination-engine/SKILL.md`
- **狀態：** `PROPOSED_NOT_ADOPTED`。
- **批次門檻：** 批次 0 封鎖 delegation、parallel writer、shared writer、secret handling、external write 與正式交付；不可逆／外部寫入 fail closed。批次 1 每個 operation 必須有 schema_version、task／operation ID、唯一 step ID、P/C/J、證據狀態、四態與七欄卡；正式採用前須完成 F-01～F-12、相近不觸發反例、safe-implementation、independent-audit、repo／lint／專測／冷啟動／回歸與治理裁決。
- **依賴順序：** Stage 0 → Stage 1，且先於依賴多代理的 `grilling`；Stage 5。
- **未解決項：** 觸發條件與 miko-core 四視角責任重疊；缺至少兩個獨立、互不寫入、fresh context 的唯讀子問題硬條件；最大並行數、授權邊界、writer 互斥、不得委派事項、冪等鍵、來源 pin、原子寫入／讀回及部分成功聚合未證實；固定測題、專測、independent-audit、miko-core／safe-implementation 接線均未完成。
- **下一站：** 先定義並驗證唯讀協調器的觸發／停止／並行／writer 契約，再讓 `grilling` 或其他 Skill 依賴它。

### 3.7 photo-inspection-log

- **提案路徑：** `knowledge-cards/proposals/skills/20261112_batch4/07-photo-inspection-log/SKILL.md`
- **狀態：** `PROPOSED_NOT_ADOPTED_HISTORICAL_NOT_RUNTIME`。
- **批次門檻：** 批次 0 只允許 preflight diagnostics、manifest hash audit、workfile read、fixture test；封鎖 formal xlsx export、company delivery、external write、overwrite existing delivery。批次 1 固定 `PCL-AUDIT-001` 與候選 operation contract；缺批准、來源 pin、原子提交、COMMITTED、讀回或 SHA 即停止；須完成 AC-T1～AC-T12、independent audit、固定 commit/raw、冷啟動與治理裁決。
- **依賴順序：** Stage 0 → Stage 2 媒體／manifest／來源鏈 → Stage 5；其 xlsx/PDF 驗收不得先於來源與原子 IO 契約。
- **未解決項：** 共用 contracts、safe IO、source pin、entries validator 接線未證實；照片替換、壞圖、checkpoint hash、七欄卡、PDF／版面抽查、restore／詞庫／set 的互斥與讀回未測；真實照片、preflight、entries、xlsx/PDF round-trip、Excel、專測及 independent audit 均 `NOT_RUN`／`UNKNOWN`。
- **下一站：** 先建立只讀 manifest／壞圖／來源行對應 fixture，再驗證工作檔原子性與 round-trip；正式 xlsx 交付保持封鎖。

### 3.8 tw-alert-check

- **提案路徑：** `knowledge-cards/proposals/skills/20261112_batch4/08-tw-alert-check/SKILL.md`
- **狀態：** `PROPOSED_NOT_ADOPTED`。
- **批次門檻：** 批次 0 封鎖 official safety conclusion、closure conclusion、traffic safety release、activity safety release 與 external write。批次 1 的共用狀態、四態、七欄卡、`TWAC-P0`、P/C/J 與 operation contract 僅為候選。批次 2 逐來源／逐日期 immutable pin、原始內容 SHA、工具版本、命令、exit code、查閱時間與衝突並列；批次 3 原子寫入／讀回；批次 4／5 AC-T1～T12、independent audit、固定 commit raw、治理裁決。
- **依賴順序：** Stage 0 → Stage 2 官方警報／停班停課／天氣／交通／活動來源 → Stage 5；不得從單一來源直接產生完整安全結論。
- **未解決項：** 缺逐來源／逐日期狀態、相依停止、權威邊界與衝突處理；缺多日／地點／時區／凌晨明天雙日證據；JSON／Markdown 索引、fake adapter、fixture、專測、operation ID、單一 writer、原子寫入、COMMITTED、讀回 SHA、safe-implementation／miko-core／independent-audit 接線均未證明。
- **下一站：** 先建立逐來源、逐日期、逐時區證據矩陣與衝突 fixture；在治理裁決前只保留唯讀草稿，禁止正式安全結論。

### 3.9 tw-backtest-workflow

- **提案路徑：** `knowledge-cards/proposals/skills/20261112_batch4/09-tw-backtest-workflow/SKILL.md`
- **狀態：** `PROPOSED_NOT_ADOPTED`。
- **批次門檻：** 路由固定 `PAUSED_BY_USER`；只允許 C6、C9、readonly contract test。任何不可逆、外部寫入、讀回未知、關鍵 UNKNOWN／NOT_RUN／CONFLICT／BLOCKED／PARTIAL 均 fail closed。需驗證暫停優先、旗標 XOR、manifest／hash、PIT／look-ahead、schema、成本／基準、事件與 28 欄適用性。
- **依賴順序：** Stage 0 → Stage 4 固定唯讀回歸 → Stage 5；不得依賴一般資料抓取或策略研究。
- **未解決項：** `backtest_contract.py`、`preflight_fixed_regression.py` 與專測接線未驗證；缺 operation ID、冪等、防盲目重試、原子寫入、讀回 SHA、COMMITTED、四態／證據狀態／七欄卡實際契約；歷史 PASS 未重跑；C6、C9、lint、CI、冷啟動及真實回測均 `NOT_RUN`；miko-core／safe-implementation／independent-audit 接線未讀取。
- **下一站：** 先驗證 `PAUSED_BY_USER` 在入口最前端阻擋，再只跑固定 C6/C9 唯讀回歸；不得恢復一般回測或交易解讀。

### 3.10 visual-content-intelligence

- **提案路徑：** `knowledge-cards/proposals/skills/20261112_batch4/10-visual-content-intelligence/SKILL.md`
- **狀態：** `PROPOSED_NOT_ADOPTED`。
- **批次門檻：** 批次 0 封鎖 content_and_miko、formal_proposal、engineering_import、download、upload、external_write、public_publish；所有外部／不可逆行為 fail closed。批次 1 唯一步驟 ID、P/C/J、六種證據狀態、四態、七欄卡及固定 commit/raw／SHA／冷啟動／independent-audit／治理裁決仍為前置條件。
- **依賴順序：** Stage 0 → Stage 2 輸入／來源／媒體 manifest → Stage 5；不得把 vci_check 結構 PASS 當正式交付 PASS。
- **未解決項：** probe、frames、transcript、analysis、proposal 的輸入／輸出 manifest 與來源 SHA 傳播未實作／驗證；outdir 清理與 operation-specific 隔離未證實；`NOT_FOUND` 與 `NOT_READ`／`UNKNOWN` 接線未驗證；來源替換、並行重跑、寫入後未知、授權不足、URL-only、部分成功測題未執行；所有工程、測試、Runtime 與 external service 均 `NOT_RUN`／`UNKNOWN`。
- **下一站：** 先建立只讀 probe／frame／transcript／analysis manifest 與來源 hash 傳播 fixture，驗證 operation-specific outdir；維持下載、上傳、外部寫入與公開發布封鎖。

## 4. 交接與驗收紀錄要求

下一站若獲治理批准，必須逐 Skill 產生可追溯的驗收包，至少包含：

- 固定來源／工具 immutable ref、版本、命令、exit code、查閱時間與原始內容／產物 SHA。
- 唯一 `task_id`、`operation_id`、`step_id`、批准範圍、P/C/J、輸入／輸出 manifest、禁止事項與失敗出口。
- fake／fixture 及 expected／forbidden 測題的逐題結果；包含成功、失敗、UNKNOWN、CONFLICT、BLOCKED、PARTIAL、停止、重入、逾時、限流、授權不足與相近不觸發反例。
- 原子寫入暫存／fsync／替換／`COMMITTED`／讀回 SHA 證據；讀回未知必須保留 `UNKNOWN` 或 `BLOCKED`，不得猜測成功。
- independent-audit 的 fresh-context 結果、冷啟動／新對話回歸、治理裁決與採用範圍。

在上述證據包完成並獲正式裁決以前，本索引與十份 Skill 提案均維持**僅提案區、未採用、未稽核、未接正式 Runtime**。