---
doc_id: ucp-spec
name_en: Miko Creation Process (folded into miko-core)
name_zh: 通用製作流程
module: universal-creation-process
version: 0.8.7
date: 2026-11-14
status: PROPOSED
owner_role: R-CONV
adopted: false
runtime_verified: UNKNOWN
supersedes: 0.1.0
amends: 0.8.7
change_ref: review/round1.json#F-01..F-10
---

# 製作流程（Miko Creation Process, MCP）：miko-core 的製作章節

> 層級狀態：本層已併入 miko-core（D16，2026-11-14）。閉環條文見 `core-closure/core-rewrite-spec.md` 的 C1～C6，與本文件 A08～A13 一一對應。miko-core 是流程的唯一權威；本文件保留為製作流程的步驟與閘門附錄，A08 自我驗收、A10 錯誤維護、A11 有界重測、A12 獨立驗收、A13 交付收工的閉環細節由 miko-core 負責，本文件只保留閘門引用與證據位置。


## 0. 文件控制

| 欄位 | 值 |
|---|---|
| 文件識別 | `MIKO-UGA-UCP-SPEC` |
| 版本 | 0.8.7（候選，未驗收、未採用、未生效） |
| 日期 | 2026-11-14（Asia/Taipei） |
| 狀態 | `PROPOSED` |
| 適用層級 | L1：所有產物 |
| 變更來源 | Claude API 第一輪審查 F-01～F-10，加自檢補強 G-01～G-08 |

## 1. 目的與範圍

本規格定義 MIKO 一切「製作」行為的通用流程：從請求受理到獨立驗收與保存。所有產物共用同一主幹，差別只在於選用哪份欄位契約（UAC 或 USC）。

範圍內：Skill、Skill 規格書、架構書、流程設計書、治理規則、路由器文件、測試規格、文件整合與升級。

範圍外：契約欄位定義（UAC／USC）、路由演算法（RSL）、版本政策細節（LCV）、檢查器實作（TSV）。

## 2. 名詞與定義

| 名詞 | 英文識別 | 定義 |
|---|---|---|
| 產物 | artifact | 本流程輸出的任何可保存文件、規格、Skill、規則或設定 |
| 契約 | contract | 規定產物必須具備的章節、欄位與格式（UAC 或 USC） |
| 自我驗收 | self-acceptance | 製作者或同 context 驗收者依 AC 檢查，結果只能是 `SELF_PASS`／`SELF_PASS_ONLY`／`SELF_FAIL` |
| 獨立驗收 | independent acceptance | 在與製作者隔離的條件下，只依「驗收包」判定，結果為 `AUDIT_PASS`／`AUDIT_FAIL`／`NOT_RUN` |
| 獨立性等級 | independence level | 依 §2.1 判定表；等級以「可證明的最弱一環」為準，無法證明一律視為 L0 |
| 冷啟動 | cold start | 新 conversation session；不載入製作階段 context；只讀驗收包；不讀作者說明、自我驗收結論或實作思路（修正 F-03） |
| 驗收包 | audit packet | 只含候選產物、AC 表、契約版本、diff 與檢查器輸出；**不含**製作者辯解、自我驗收結論、實作思路 |
| 輪次 | round | 對「受影響 AC 全集」執行一次完整檢查或重測，不論其中有幾條失敗 |
| 預算 | cycle budget | 每個產物版本血緣允許的重測與重驗次數上限 |
| 閉環 | closed loop | 自我驗收→補強→錯誤維護→保存 diff→重測→達標才交獨立驗收，且受預算約束 |
| 流程先行 | process-first | 先定流程，再由流程推導標題、章節、欄位、格式、IO、AC、失敗出口 |
| 修正帳本 | correction ledger | `ledger/` 下的錯誤帳、否決帳、變更帳與索引；開工時與治理一起載入 |
| 錯誤紀錄 | error entry | 錯誤帳的一筆，含現象、證據、根因、修正與回歸測題，以去重鍵判重 |
| 否決紀錄 | rejection entry | 否決帳的一筆，含被否決方案、理由、替代方案與解除條件 |
| 文本純度 | text purity | 正文只放已驗收合格的繁中敘述，測試輸出與原始日誌只放證據目錄 |

### 2.1 獨立性等級判定表（修正 A12-REV-01）

| 等級 | 條件（可驗證） | 必要證據 | 可給出的最高結果 | 備註 |
|---|---|---|---|---|
| L0 | 同一 session，曾載入製作內容或自我驗收結論 | 無隔離證據 | 僅 `SELF_*`；不得作為 A12 正式驗收 | 只供自查；L0 送驗一律視為未驗 |
| L1 | 同模型、新 session 冷啟動、只讀驗收包 | session 識別、模型 ID、開包前 `sha256sum -c` 輸出、`contact_with_author=false` | `AUDIT_PASS`（限文件／契約一致性） | `adoption_support=NO`：可候選交付，不得作 `ADOPTED` 依據 |
| L2 | 不同模型冷啟動（模型 ID 與製作者不同） | 同 L1，加上雙方模型 ID 對照 | `AUDIT_PASS` | `adoption_support=YES`：可作 `ADOPTED` 依據，仍需 R-CONV 裁決 |
| L3 | 人類驗收者 | 驗收者識別（姓名或代號）、時間、簽核紀錄 | `AUDIT_PASS` | `adoption_support=YES`：正本採用建議等級；`EFFECTIVE` 仍需 Runtime 證據 |

判定規則：

- L-01 等級由「實際可證明」的最小值決定；任一條證據缺漏即降一級。
- L-02 驗收者若中途接觸作者說明、自我驗收結論或實作思路，降為 L0 並換人重驗，該輪計入 `audit_round`。
- L-03 同一人不得同時擔任 R-AUD 與 R-EVD，也不得與同一次 R-CONV 裁決同人。
- L-04 多位驗收者時，`independence_level` 取最低者；判定取最嚴格者（任一 `AUDIT_FAIL` 即整體 `AUDIT_FAIL`），不得以多數決；報告記 `reviewer_split=true` 並列各人判定，交 R-CONV 裁決。
| 困難卡 | difficulty card | 七欄卡：現象｜證據｜類別｜影響哪個 AC｜解除條件｜負責方｜首次發現時間 |
| 任務四態 | task quad-state | 完成／完成但有疑慮／需要資料／卡住 |

## 3. 三層分層與責任邊界

| 層 | 識別 | 適用對象 | 負責 | 不負責 |
|---|---|---|---|---|
| L1 | A：通用製作流程（本文件） | 所有產物 | 製作順序、閉環、狀態機、預算、失敗出口種類、證據與保存、獨立驗收門檻 | 章節清單、欄位名稱、Skill 步驟格式 |
| L2a | 文件契約（DOC，原 UAC） | 規格書、架構書、流程設計書、治理文件、路由器文件、測試規格、整合升級文件 | 十六章標題與每章必要欄位 | 製作流程、驗收順序、Skill 九契約 |
| L2b | Skill 契約（SKL，原 USC） | Skill | 九項必要契約、四節格式、P/C/J 七欄步驟 | 十六章、閉環順序 |

邊界規則：

- BR-01：UCP 不重複定義欄位；只規定何時、依何順序、用哪份契約。
- BR-02：UAC／USC 不重複定義流程；只規定欄位必須存在且可檢。
- BR-03：UCP 的步驟 ID 可被 UAC／USC 引用，但契約的生效不得依賴 UCP 執行；反向亦然。
- BR-04：任一責任只有一個擁有者；其餘只能列為消費。
- BR-05：凡涉及欄位名稱，UCP 一律引用 UAC／USC 的定義，不另行命名（修正 F-10）。
- BR-06：UCP 不負責宣告 Runtime 能力；能力狀態一律 `UNKNOWN` 直到有實測證據。

## 4. 流程總覽

主幹（DAG，禁止反向邊）：

```
A00 受理 → A01 來源讀取 → A02 類型判定與路由 → A03 契約鎖定
→ A04 流程先行 → A05 結構實例化 → A06 IO 與 AC 定稿 → A07 失敗出口與回復
→ A08 組裝與自我驗收 ⇄ A09 主動補強 → A10 錯誤維護與 diff
→ A11 有界重測（retest_round ≤3）→ A12 獨立驗收（audit_round ≤2）→ A13 交付與收工
```

狀態機（文件層，與 A3 字典對齊）：

```
PROPOSED → SELF_PASS → AUDIT_PASS → ADOPTED → EFFECTIVE（需 Runtime 證據）
SELF_FAIL／SELF_PASS_ONLY → 不得進 A12 為通過；AUDIT_FAIL → 回 A10
NOT_READ／NOT_RUN／UNKNOWN／BLOCKED／CONFLICT → 停相依步驟或出困難卡
STOPPED／STOPPED_BY_USER → 停止
```

禁止轉移：`PROPOSED → ADOPTED`、`SELF_PASS → EFFECTIVE`、`AUDIT_PASS → EFFECTIVE`（無 Runtime 證據時）、`SELF_PASS_ONLY → AUDIT_PASS`。

### 4.1 預算與終止證明（修正 F-08、F-09）

| 計數器 | 計數單位 | 上限 | 超限處理 |
|---|---|---|---|
| `retest_round` | 對受影響 AC 全集完整重測一次 | 3 | `BLOCKED`＋困難卡 |
| `audit_round` | 送獨立驗收一次 | 2 | `BLOCKED`＋困難卡 |

- 兩個計數器獨立，但皆屬同一「產物版本血緣」，不得因換檔名或改版本號而歸零。
- 修檔後重新計數的唯一方式：`R-OWNER` 書面同意並記錄 `budget_reset_reason`；無此紀錄即視為超限。
- 終止性：每次循環至少消耗 1 單位有限預算，預算有限 ⇒ 流程必然終止於 `AUDIT_PASS` 或 `BLOCKED`。

## 5. 步驟規格

每步定義十三欄，欄位順序即檢查順序，缺一欄即 `SELF_FAIL`。回歸測題不計入定義，列為例外欄位；例外欄位只寫測題編號與證據位置，不寫測試內容，測試細節一律留在證據目錄，這是文本純度規則在流程上的落實（2026-11-14 MIKO 指定）。

### A00 請求受理與任務分類

- **目的**：把使用者請求轉成可執行的製作任務，先過停止／禁止／授權閘門。
- **輸入**：使用者請求原文、對話上下文、治理核心狀態（版本或 `CORE_NOT_READ`）、修正帳本（錯誤帳與否決帳）。
- **輸出**：任務卡（`task_id`、請求摘要、任務分類、產物類型候選、禁止項清單、授權狀態、`retest_round=0`、`audit_round=0`）。
- **前置條件**：可讀取使用者請求；已判定治理核心狀態；治理、錯誤帳、否決帳三份常駐文件已依序載入或已標未讀。
- **操作要求**：先依治理、錯誤帳、否決帳的順序載入常駐文件並記下版本與雜湊；再寫對齊行，格式照正本 miko-core §1.4：「已對齊：miko-core vX（正本 vY（commit 短碼｜讀取時間 YYYY-MM-DD HH:MM 台北））｜領域：名稱｜Skill：名稱與版本或無｜狀態來源：名稱（讀取日期）或 NOT_READ」，讀不到正本時寫「正本 NOT_READ」並附讀取失敗原因，工具沒回 commit 時寫 commit UNKNOWN，不補造；再逐條拆解請求；標記不可逆操作與硬禁止（下單、LIVE、Broker、外部寫入）；核心未載入時標 `CORE_NOT_READ` 並限制為候選輸出；初始化兩個計數器。
- **禁止事項**：不得把沉默當授權；不得把候選升格為正式；不得略過硬禁止；不得在核心未載入時做外部寫入。
- **檢查點**：三份常駐文件有載入結果；對齊行已寫且含正本版本、commit 與讀取時間三欄；任務卡逐條覆蓋請求；禁止項與授權狀態已列；計數器已初始化；回覆中可查核的主張都有行內標籤，最後一行是流程鎖，流程鎖的通過、降級、UNKNOWN 三數相加等於標籤數。
- **Acceptance Criteria**：`AC-A00-01` 每個請求子項有對應任務條目；`AC-A00-02` 禁止項與授權狀態已明列；`AC-A00-03` 核心狀態與計數器已標示；`AC-A00-04` 治理、錯誤帳、否決帳皆有載入結果或未讀原因；`AC-A00-05` 若判定為輕量路徑，理由齊全且不在禁止清單；`AC-A00-06` 對齊行含正本版本、commit 短碼與讀取時間，讀不到時為正本 NOT_READ 加讀取失敗時間；`AC-A00-07` 回覆有行內標籤，最後一行是流程鎖且三數相加等於標籤數。
- **Failure Handling**：請求模糊 → `UNKNOWN`＋安全預設；涉及硬禁止 → `STOPPED`。
- **Recovery**：請使用者補齊後重跑 A00；重跑不消耗預算。
- **回歸測題（例外）**：`RT-A00`；測題內容與結果見 `tests/` 與 `results_*.json`，正文只留編號，不列測試細節。
- **閉環條件**：任務卡完成且無未標示的禁止項。
- **負責角色**：R-CONV。
- **證據與保存方式**：`evidence/<task_id>/task-card.md`（含時間戳、載入結果與 SHA-256）。

### A01 來源取得與完整讀取

- **目的**：確保依據來自實際讀取，而非記憶或摘要。
- **輸入**：任務卡、來源清單、治理核心與既有正本。
- **輸出**：來源登錄表（`source_id`、位置、版本、日期、SHA-256、讀取範圍、讀取狀態）。
- **前置條件**：A00 完成；來源位置已知。
- **操作要求**：讀取決策所需的完整相關範圍（正文、表格、附錄、例外）；記錄未讀範圍；狀態用 `VERIFIED_FROM_READ`／`PARTIAL_READ`／`NOT_READ`／`CONFLICT`。
- **禁止事項**：不得以摘要、片段、記憶或舊副本冒充正文；不得把 `VERIFIED_FROM_READ` 寫成內容正確。
- **檢查點**：每份來源有狀態；未讀範圍已列；SHA-256 已記錄或標 `UNAVAILABLE`。
- **Acceptance Criteria**：`AC-A01-01` 登錄表欄位齊全；`AC-A01-02` 每個 `NOT_READ` 有原因；`AC-A01-03` 讀取時間已記錄。
- **Failure Handling**：讀不到 → `NOT_READ`，只停相依步驟；來源矛盾 → `CONFLICT`。
- **Recovery**：改用權威不低於原來源的替代來源；仍失敗則 `BLOCKED` 並寫明使用者需做的一步。
- **回歸測題（例外）**：`RT-A01`；測題內容與結果見 `tests/` 與 `results_*.json`，正文只留編號，不列測試細節。
- **閉環條件**：相依步驟所需來源皆有狀態。
- **負責角色**：R-BLD。
- **證據與保存方式**：`evidence/<task_id>/sources.json`。

### A02 產物類型判定與路由

- **目的**：判定產物類型並選擇正確路線與契約。
- **輸入**：任務卡、來源登錄表。
- **輸出**：路由決策（`artifact_type`、`route_id`、選用契約、理由）。
- **前置條件**：A00、A01 完成。
- **操作要求**：依 RSL 路由表比對八種以上產物類型；多產物逐個判定；記錄判定依據。
- **禁止事項**：不得用「最接近」模板硬套；不得同一產物掛兩份互斥契約。
- **檢查點**：`route_id` 存在於 RSL 路由表；契約與類型一致。
- **Acceptance Criteria**：`AC-A02-01` 每個產物有唯一 `route_id`；`AC-A02-02` 契約選擇有理由；`AC-A02-03` 無未路由產物。
- **Failure Handling**：無法判定 → `UNKNOWN`，列候選交 R-CONV；RSL 路由表不可讀 → `NOT_READ`，停 A02 並出困難卡（修正 F-04）。
- **Recovery**：補問或套預設路由（規格類→UAC、Skill→USC）。
- **回歸測題（例外）**：`RT-A02`；測題內容與結果見 `tests/` 與 `results_*.json`，正文只留編號，不列測試細節。
- **閉環條件**：無 `UNKNOWN` 路由。
- **負責角色**：R-CONV。
- **證據與保存方式**：`evidence/<task_id>/routing.json`。

### A03 契約選擇與欄位鎖定

- **目的**：鎖定本次任務適用的契約版本，欄位清單以契約為唯一來源，UCP 不重抄。
- **輸入**：路由決策、UAC／USC 契約版本。
- **輸出**：契約版本鎖定紀錄（契約 ID、版本、雜湊、適用章節範圍）；必填欄位以 UAC §7、§12 與 USC-C3／C4／C8 為唯一來源，本步只記引用位置。
- **前置條件**：A02 完成；契約版本已讀取。
- **操作要求**：讀取契約並記錄版本與雜湊；列出本次適用的章節範圍，欄位名稱不重抄；省略必填須寫理由並經 R-CONV 同意；鎖定後不得中途默默增刪。
- **禁止事項**：不得刪減必填欄位；不得用「其他」「略」替代；不得在驗收後改鎖定清單。
- **檢查點**：鎖定清單與契約版本一致；每欄有 ID。
- **Acceptance Criteria**：`AC-A03-01` 契約版本與雜湊已鎖定，欄位清單以引用位置表示、未重抄；`AC-A03-02` 每個省略有理由；`AC-A03-03` 契約版本已記錄。
- **Failure Handling**：契約版本不明 → `NOT_READ`，改用已讀版本並標示。
- **Recovery**：重讀契約或降級為候選輸出。
- **回歸測題（例外）**：`RT-A03`；測題內容與結果見 `tests/` 與 `results_*.json`，正文只留編號，不列測試細節。
- **閉環條件**：機器比對通過。
- **負責角色**：R-BLD。
- **證據與保存方式**：`evidence/<task_id>/field-lock.json`。

### A04 流程先行定義

- **目的**：先定流程，再由流程推導標題、章節、欄位、格式、IO、AC、失敗出口。
- **輸入**：欄位鎖定清單、任務卡。
- **輸出**：流程草案（步驟序列、每步 IO、分支、結束條件）。
- **前置條件**：A03 完成。
- **操作要求**：先寫製作流程再寫文件章節；每個章節可追溯到一個製作步驟；推導順序固定為 D-01 流程 → D-02 章節 → D-03 欄位 → D-04 格式 → D-05 IO → D-06 AC → D-07 失敗出口。製作流程與系統流程分開：系統流程與元件、介面、資料流屬架構書，UCP 不定義也不對應。
- **禁止事項**：不得先寫章節再回填流程；不得有無流程步驟支撐的章節；不得有無章節承接的流程步驟。
- **檢查點**：流程步驟與章節雙向對應表完整。
- **Acceptance Criteria**：`AC-A04-01` 每章節可追溯流程步驟；`AC-A04-02` 每流程步驟有章節承接；`AC-A04-03` D-01～D-07 順序有紀錄；`AC-A04-04` 對應表只含文件章節，未出現系統流程、元件或介面。
- **Failure Handling**：對應不上 → `CONFLICT`，回 A04 重排。
- **Recovery**：合併或拆分步驟後重跑對應。
- **回歸測題（例外）**：`RT-A04`；測題內容與結果見 `tests/` 與 `results_*.json`，正文只留編號，不列測試細節。
- **閉環條件**：雙向對應 100%。
- **負責角色**：R-BLD。
- **證據與保存方式**：`evidence/<task_id>/traceability.json`。

### A05 結構實例化

- **目的**：把製作流程轉成文件骨架，章節標題與編號取自契約，UCP 不自行命名。
- **輸入**：流程草案、欄位鎖定清單、契約模板。
- **輸出**：文件骨架（標題層級、章節、表格欄位、格式範例）。
- **前置條件**：A04 完成。
- **操作要求**：標題層級只用 `#`～`####`；章節標題與編號以 UAC 或 USC 為唯一來源，本步只決定適用範圍；表格欄位順序與契約一致；日期 `YYYY-MM-DD`、時間 `HH:MM:SS+08:00`。
- **禁止事項**：不得自創章節；不得改欄位順序；不得以圖片取代文字欄位。
- **檢查點**：結構檢查腳本通過。
- **Acceptance Criteria**：`AC-A05-01` 十六章或四節齊全；`AC-A05-02` 欄位名與契約逐字一致；`AC-A05-03` 格式範例存在。
- **Failure Handling**：格式錯誤 → `SELF_FAIL`，就地修正。
- **Recovery**：依契約模板重建骨架。
- **回歸測題（例外）**：`RT-A05`；測題內容與結果見 `tests/` 與 `results_*.json`，正文只留編號，不列測試細節。
- **閉環條件**：結構檢查 0 錯。
- **負責角色**：R-BLD。
- **證據與保存方式**：`evidence/<task_id>/structure-check.log`。

### A06 輸入輸出與驗收條件定稿

- **目的**：把每步的 IO 與 AC 寫成可檢驗句子。
- **輸入**：文件骨架、流程草案。
- **輸出**：IO 表與 AC 表；欄位名稱一律沿用 UAC §7、§12 與 USC-C3／C4／C8 的定義，不另命名。
- **前置條件**：A05 完成。
- **操作要求**：本步只做任務級 IO 與 AC 實例化，不重複定義契約判定標準；流程 AC 只驗執行完成與證據存在，內容判定引用 UAC 或 USC 的 AC ID；AC 必須可被第三方用文件與工具判定；每條 AC 對應至少一個測試案例；AC 定稿後不得放寬。
- **禁止事項**：不得用無判準詞（完整、正確、良好）；不得讓製作者同時是唯一判定者；不得在驗收後放寬 AC。
- **檢查點**：每條 AC 有 ID、方法、證據、判定者；每條 AC 有測試案例。
- **Acceptance Criteria**：`AC-A06-01` AC 覆蓋所有必填欄位；`AC-A06-02` 每條 AC 有測試案例；`AC-A06-03` 獨立驗收時判定者非製作者；`AC-A06-04` 流程 AC 未複製契約判定標準，引用處有 AC ID。
- **Failure Handling**：AC 不可判定 → `SELF_FAIL`，改寫。
- **Recovery**：把主觀詞改為可觀察條件，並記錄為新版本 AC（不得就地覆蓋）。
- **回歸測題（例外）**：`RT-A06`；測題內容與結果見 `tests/` 與 `results_*.json`，正文只留編號，不列測試細節。
- **閉環條件**：掃描 0 禁用詞、覆蓋率 100%。
- **負責角色**：R-BLD。
- **證據與保存方式**：`evidence/<task_id>/ac.json`。

### A07 失敗出口與回復設計

- **目的**：為每步定義失敗出口、狀態碼、重試上限與回復路徑。
- **輸入**：IO 表、AC 表、A3 狀態字典。
- **輸出**：失敗出口表（步驟、失敗類別、狀態碼、出口、重試上限、回復動作、負責方）。
- **前置條件**：A06 完成。
- **操作要求**：每步至少一個失敗出口；重試上限為有限整數；回復路徑不得成環；需人工介入者標負責方。
- **禁止事項**：不得無上限重試；不得「失敗就重跑全流程」而無終止條件；不得把 `BLOCKED` 寫成 `PASS`。
- **檢查點**：出口表覆蓋所有步驟；重試上限皆有限；回復圖無環。
- **Acceptance Criteria**：`AC-A07-01` 每步至少一個失敗出口；`AC-A07-02` 所有重試上限為有限整數；`AC-A07-03` 回復路徑可終止。
- **Failure Handling**：發現環 → `CONFLICT`，切斷並改人工裁決。
- **Recovery**：加入終止條件或升級 `BLOCKED`。
- **回歸測題（例外）**：`RT-A07`；測題內容與結果見 `tests/` 與 `results_*.json`，正文只留編號，不列測試細節。
- **閉環條件**：0 環、0 無上限重試。
- **負責角色**：R-BLD。
- **證據與保存方式**：`evidence/<task_id>/failure-exits.json`。

### A08 組裝與自我驗收

- **目的**：組裝候選產物並依 AC 逐條自我驗收。
- **輸入**：骨架、IO 表、AC 表、失敗出口表、正文。
- **輸出**：候選產物 vN、自我驗收表（逐條 AC：`SELF_PASS`／`SELF_PASS_ONLY`／`SELF_FAIL`／`NOT_RUN`）。
- **前置條件**：A05～A07 完成。
- **操作要求**：逐條 AC 填結果與證據位置；`NOT_RUN` 寫缺什麼；自我驗收結果只能是自我層標籤。
- **禁止事項**：不得把 `SELF_PASS` 寫成 `ACCEPTED`；不得把未跑寫 `PASS`；不得省略 AC。
- **檢查點**：AC 逐條有結果；證據可開啟。
- **Acceptance Criteria**：`AC-A08-01` 覆蓋 100% AC；`AC-A08-02` 無空結果；`AC-A08-03` 只用自我層標籤。
- **Failure Handling**：任何 `FAIL` → `SELF_FAIL`，進 A09。
- **Recovery**：修正後回 A08。
- **回歸測題（例外）**：`RT-A08`；測題內容與結果見 `tests/` 與 `results_*.json`，正文只留編號，不列測試細節。
- **閉環條件**：無 `FAIL`、無空值。
- **負責角色**：R-SELF（優先與製作者不同 context；同 context 時須標記 `same_context=true`）。
- **證據與保存方式**：`evidence/<task_id>/self-acceptance-vN.json`（不放入驗收包）。

### A09 主動補強

- **目的**：對 `SELF_FAIL` 與可推導的缺口主動補強，不只回報缺口。
- **輸入**：自我驗收表、來源登錄表。
- **輸出**：補強清單（缺口、來源依據、修改內容、影響範圍）。
- **前置條件**：A08 有 `FAIL` 或缺口。
- **操作要求**：每缺口先判斷可否由既有來源或規格推導；可推導者直接補；不可推導者標 `UNKNOWN` 並列原因。
- **禁止事項**：不得憑空創造來源；不得為通過而放寬 AC；不得只寫「待補」。
- **檢查點**：每缺口有決定（補／`UNKNOWN`／`BLOCKED`）。
- **Acceptance Criteria**：`AC-A09-01` 缺口 100% 有決定；`AC-A09-02` 補強有來源依據；`AC-A09-03` AC 未被放寬。
- **Failure Handling**：缺來源 → `UNKNOWN`；缺授權 → `BLOCKED`。
- **Recovery**：補齊後回 A08。
- **回歸測題（例外）**：`RT-A09`；測題內容與結果見 `tests/` 與 `results_*.json`，正文只留編號，不列測試細節。
- **閉環條件**：無未處理缺口。
- **負責角色**：R-BLD。
- **證據與保存方式**：`evidence/<task_id>/reinforcement.json`。

### A10 錯誤維護與 diff 保存

- **目的**：每次修改保存前後 diff 與理由，讓錯誤可追溯。
- **輸入**：修改前後版本、補強清單。
- **輸出**：unified diff、變更紀錄（原因、位置、影響的 AC）、修正帳本更新（錯誤帳、變更帳）。
- **前置條件**：有實際修改。
- **操作要求**：錯誤發生時先定位到最小受影響單元，單元可以是步驟、欄位、章節或帳本條目；只修該單元，重測只跑受影響的檢查器與測題，不重跑整包流程。只有三種情況才擴大範圍：錯誤跨兩個以上步驟、錯誤改到契約或欄位定義、受影響單元沒有可單獨執行的檢查；擴大的理由要寫進變更帳，不能只寫全面重跑。修完只保留該單元的 diff，未動的檔案不重算雜湊。每筆變更對應至少一個 AC 或缺口 ID；先算去重鍵，命中既有條目就地更新並保留前一版，未命中才新增；不得覆寫歷史版本。
- **禁止事項**：不得只留最終版；不得無理由改動無關段落；不得刪除失敗紀錄。
- **檢查點**：diff 可套用；變更紀錄與 diff 對應。
- **Acceptance Criteria**：`AC-A10-01` 每輪修改有 diff；`AC-A10-02` 每筆變更有理由；`AC-A10-03` 歷史版本未被覆寫；`AC-A10-04` 變更帳已就地更新且對應 diff 與證據；`AC-A10-05` 錯誤修復的 diff 只含受影響單元，重測範圍與擴大理由已記入變更帳。
- **Failure Handling**：diff 缺失 → `SELF_FAIL`。
- **Recovery**：由版本庫或備份重建 diff。
- **回歸測題（例外）**：`RT-A10`；測題內容與結果見 `tests/` 與 `results_*.json`，正文只留編號，不列測試細節。
- **閉環條件**：diff 可套用且紀錄完整。
- **負責角色**：R-EVD。
- **證據與保存方式**：`evidence/<task_id>/diff/round-<n>.patch`。

### A11 有界重測

- **目的**：修改後重跑受影響檢查與全部回歸，確認沒有退化。
- **輸入**：新版本、diff、測試集。
- **輸出**：重測結果（每項 `PASS`／`FAIL`／`NOT_RUN`）、`retest_round` 值。
- **前置條件**：A10 完成。
- **操作要求**：一輪＝對受影響 AC 全集完整重測一次；另加一題新題；重測後更新 `retest_round`。
- **禁止事項**：不得只重跑失敗項；不得超過 3 輪仍宣稱進行中；不得在 `FAIL` 下交付。
- **檢查點**：`retest_round` 已更新；回歸集全跑。
- **Acceptance Criteria**：`AC-A11-01` 回歸集 100% 有結果；`AC-A11-02` `retest_round ≤ 3`；`AC-A11-03` 無 `FAIL` 才可進 A12。
- **Failure Handling**：超過 3 輪 → `BLOCKED`＋困難卡。
- **Recovery**：縮小範圍、補來源或改設計；預算重置須 `R-OWNER` 書面同意並記 `budget_reset_reason`。
- **回歸測題（例外）**：`RT-A11`；測題內容與結果見 `tests/` 與 `results_*.json`，正文只留編號，不列測試細節。
- **閉環條件**：全 `PASS` 且 `retest_round ≤ 3`。
- **負責角色**：R-SELF。
- **證據與保存方式**：`evidence/<task_id>/retest-round-<n>.json`。

### A12 獨立驗收交接
- **目的**：在可證明的隔離條件下判定產物是否符合 AC，避免自我驗收冒充獨立驗收。
- **輸入**：驗收包（規格見附錄 A）、封裝雜湊清單 `audit-packet/MANIFEST.sha256`。
- **輸出**：獨立驗收報告 `audit-report.md`（含附錄 A.4 固定欄位）、`audit-verify.log`、`independence_level`、`adoption_support`、逐條 AC 判定；報告置於包外 `evidence/<task_id>/`。
- **前置條件**：A11 全 `PASS`；驗收包已封裝且 `sha256sum -c` 通過；驗收者未讀取自我驗收結論、作者說明或實作思路；驗收者非 R-BLD／R-SELF／R-EVD。
- **操作要求**：先驗封裝再開包（驗證失敗即 `BLOCKED`，不得繼續）；只讀包內檔案；逐條 AC 依報告 schema 填 `verdict`、`evidence_ref`、`reason`；寫明 `independence_level`、`contact_with_author`、`reviewer_id`、`reviewed_at`、`tool_versions`；等級依 §2.1 以最弱一環判定。
- **禁止事項**：不得由 R-BLD／R-SELF 兼任；不得先看自我驗收結論；不得修改包內任何檔案；L0 不得給 `AUDIT_PASS`；不得把 `AUDIT_PASS` 寫成 `ADOPTED` 或 `EFFECTIVE`（`ADOPTED` 需 R-CONV 裁決）。
- **檢查點**：封裝雜湊一致；報告欄位齊全；每條 AC 有判定與證據引用；等級與證據相符；`contact_with_author=false`。
- **Acceptance Criteria**：`AC-A12-01` 驗收者隔離且 `independence_level ≥ L1`；`AC-A12-02` 逐條 AC 有判定與證據引用；`AC-A12-03` 標籤與等級一致；`AC-A12-04` 封裝驗證通過且報告欄位齊全；`AC-A12-05` 接觸作者或包內竄改一律不得 `AUDIT_PASS`；`AC-A12-06` `AUDIT_PASS` 未經 R-CONV 不得標 `ADOPTED`／`EFFECTIVE`。
- **Failure Handling**：`AUDIT_FAIL` → 回 A10 並 `audit_round+1`；封裝雜湊不符或包內缺件 → `BLOCKED`，原報告作廢、重新封裝；驗收者接觸作者 → 降 L0、換人重驗並 `audit_round+1`；無合格驗收者 → `BLOCKED`（不得降格為自我驗收）。
- **Recovery**：修正後由 R-EVD 重新封裝（新 `packet_version`、新雜湊）再送驗；上限 2 輪；重驗不得沿用舊報告。
- **回歸測題（例外）**：`RT-A12`；測題內容與結果見 `tests/` 與 `results_*.json`，正文只留編號，不列測試細節。
- **閉環條件**：`AUDIT_PASS` 且 `audit_round ≤ 2` 且等級 ≥ L1 且封裝驗證通過且報告欄位齊全。
- **負責角色**：R-AUD（不得兼 R-EVD、不得與同次 R-CONV 同人）。
- **證據與保存方式**：`evidence/<task_id>/audit-report.md`、`audit-verify.log`、`audit-packet/MANIFEST.sha256`；報告與封裝清單一併入交付包，不得事後修改。
### A13 交付、保存與收工交接

- **目的**：交付合格產物並保存證據，完成收工交接。
- **輸入**：`AUDIT_PASS` 產物、全部證據。
- **輸出**：交付包、MANIFEST、收工報告（任務四態、困難卡、未驗證清單、聲明）、修正帳本快照。
- **前置條件**：A12 `AUDIT_PASS`；未合格不得交付（任何 `FAIL`／`NOT_RUN`／空值皆阻擋）。
- **操作要求**：計算 SHA-256；列未驗證與 `UNKNOWN`；如實聲明未寫入 GitHub／未採用／未生效。
- **禁止事項**：不得把候選寫成已採用；不得省略困難卡；不得在無證據時宣稱 Runtime 生效。
- **檢查點**：MANIFEST 可驗證；收工報告欄位齊全；回覆格式自查通過——Type B 回覆含完整四段，後設四項（事實／推論／未知分開、最強反例、最可能錯的一點、偽陽性或偽陰性）逐項寫出，輕量格式不得套用到 Type B；最後一行是流程鎖且三數相加等於標籤數。
- **Acceptance Criteria**：`AC-A13-01` MANIFEST 驗證通過；`AC-A13-02` 任務四態已寫；`AC-A13-03` 未驗證清單與困難卡已列；`AC-A13-04` 三份帳的快照與雜湊已入交付包；`AC-A13-05` Type B 回覆的後設四項逐項寫出，未以輕量格式替代。
- **Failure Handling**：MANIFEST 不符 → `BLOCKED`。
- **Recovery**：重建 MANIFEST 後重驗。
- **回歸測題（例外）**：`RT-A13`；測題內容與結果見 `tests/` 與 `results_*.json`，正文只留編號，不列測試細節。
- **閉環條件**：交付包驗證通過且聲明完整。
- **負責角色**：R-EVD。
- **證據與保存方式**：`delivery/<task_id>/MANIFEST.sha256`。

## 6. 閉環規格

1. A08 自我驗收 → A09 主動補強 → A10 錯誤維護與 diff → A11 有界重測（≤3 輪）→ 全 `PASS` 才進 A12。
2. A12 失敗回 A10，`audit_round` 上限 2；超過即 `BLOCKED`。
3. 未合格不得交付：`FAIL`／`NOT_RUN`／空值／L0 驗收皆不得進 A13。
4. 自我驗收結果不得作為交付依據；交付必須有 `AUDIT_PASS`。

## 7. 失敗出口表

| 狀態 | 意義 | 出口 |
|---|---|---|
| `SELF_FAIL` | 自我驗收未過 | 回 A09／A10 |
| `SELF_PASS_ONLY` | 僅同 context 自我驗收 | 不得交付；需 L1 以上 |
| `AUDIT_FAIL` | 獨立驗收未過 | 回 A10 |
| `NOT_READ` | 來源未讀 | 停相依步驟 |
| `NOT_RUN` | 未執行 | 補執行或標缺資料 |
| `UNKNOWN` | 無法判定 | 列待決 |
| `CONFLICT` | 未裁決衝突 | 交 R-CONV |
| `BLOCKED` | 卡住 | 出困難卡 |
| `STOPPED`／`STOPPED_BY_USER` | 停止 | 停止 |

## 8. 角色

| 角色 | 職責 | 兼任限制 |
|---|---|---|
| R-OWNER | 授權、預算重置裁決 | 不擔任 R-AUD |
| R-CONV | 治理總召、路由與衝突裁決 | 可兼 R-SELF，不得兼 R-AUD（同一次） |
| R-BLD | 製作 | — |
| R-SELF | 自我驗收 | 可與 R-BLD 同人，但須標 `same_context=true` |
| R-AUD | 獨立驗收 | 不得為 R-BLD／R-SELF／R-EVD；不得與同次 R-CONV 同人；須 `independence_level ≥ L1` |
| R-EVD | 證據與封裝 | — |

## 9. 證據與保存

證據存於 `evidence/<task_id>/`；驗收包另存 `audit-packet/`，內容與封裝依附錄 A。封裝後計算 SHA-256，驗收者開包前必須驗證且不得修改。

## 10. 驗收條件彙總

見第 5 節，共 55 條（A00 7 條、A13 5 條、A10 5 條、A04 4 條、A06 4 條，A12 共 6 條，其餘每步 3 條）。

## 11. 回歸測試

`RT-A00`～`RT-A13` 共 14 組，由 TSV 執行器執行；任一組 `NOT_RUN` 視為未通過。

## 附錄 A：驗收包規格（修正 A12-REV-03）

### A.1 正面清單

驗收包目錄固定為 `audit-packet/`，只允許下列檔案；多一個檔即不合格。

```
audit-packet/
├── MANIFEST.sha256          # 包內所有檔案的雜湊，第一行固定為本清單自身以外的全部檔案
├── packet-meta.yaml         # packet_version、task_id、封裝者、封裝時間、契約版本、產物版本
├── artifact/                # 候選產物正本（不含作者註解）
├── ac/ac-table.md           # AC 表（來源：UAC §12 或 USC-C8，附版本）
├── contract/                # 契約版本（uac-spec.md 或 usc-spec.md 的對應版本）
├── diff/round-<n>.patch     # 只保留 unified diff 內容，去除 commit message、註解與作者說明
└── checks/                  # 檢查器原始輸出（JSON），不得含作者評語或自我驗收結論
```

### A.1.1 包外證據

`audit-report.md`、`audit-verify.log` 與 `audit-packet/MANIFEST.sha256` 的留存副本置於 `evidence/<task_id>/`，不放入包內；驗收者只讀包內，報告寫在包外（修正 A-01）。

### A.2 排除清單

不得放入：作者辯解、自我驗收結論、實作思路、對話紀錄、待辦清單、未來計畫。diff 若含上述內容，必須先去除再封裝。

### A.3 封裝與驗證

1. R-EVD 依 A.1 建包，`packet-meta.yaml` 記 `packet_version`（`pkt-<YYYYMMDD>T<HHMMSS+0800>-v<semver>`）。
2. 對包內所有檔案計算 SHA-256 寫入 `MANIFEST.sha256`（格式同 `sha256sum`）。
3. 驗收者開包前執行 `sha256sum -c audit-packet/MANIFEST.sha256`，輸出存 `audit-verify.log`；任一 `FAILED` 即 `BLOCKED`。
4. 驗收者不得寫入包內；若需註記，一律寫在包外的 `audit-report.md`。

### A.4 驗收報告固定欄位

| 欄位 | 說明 |
|---|---|
| `task_id`、`packet_version` | 對應封裝 |
| `reviewer_id`、`reviewer_model`、`reviewed_at` | 驗收者與時間 |
| `independence_level` | L0～L3，依 §2.1 判定 |
| `contact_with_author` | `true`／`false`；`true` 時必須降 L0 |
| `manifest_check` | `PASS`／`FAIL` |
| `tool_versions` | 檢查器與模型版本 |
| `audit_round` | 本次為第幾輪獨立驗收（1～2） |
| `results[]` | 每條 AC：`ac_id`、`verdict`、`evidence_ref`、`reason` |
| `overall` | `AUDIT_PASS`／`AUDIT_FAIL`／`BLOCKED` |
| `adoption_recommendation` | `NONE`／`RECOMMEND_ADOPT`（僅建議，`ADOPTED` 由 R-CONV 裁決） |

### A.5 竄改與作廢

封裝雜湊不符、包內缺件或出現排除清單內容時，該報告作廢，重新封裝並 `audit_round+1`；不得以口頭說明補正。

## 附錄 C：輕量路徑（LITE）

輕量路徑是給低風險、低影響、單一檔案、可逆、且不涉及跨平台寫入的產物用的縮減流程。它的目的不是降低標準，而是避免小任務被整套流程擋住而選擇繞過治理。判定發生在 A00：請求同時滿足五個條件才可走 LITE，五個條件是單一產物、可逆、不涉及治理規則或 Skill 正本、不涉及契約修改、不涉及跨平台寫入。

LITE 保留的步驟是 A00 分級、A01 讀來源、A03 鎖欄位、A06 定 AC、A08 自我驗收、A13 交付。可以省略的是 A04 流程先行、A05 結構實例化、A07 失敗出口、A09 主動補強、A11 有界重測、A12 獨立驗收；A10 只保留一句 diff 說明，不要求完整 patch。省略的每一步都要在任務卡寫明省略理由，不能只寫「簡化」。

禁止走 LITE 的範圍是：治理規則、Skill 正本、契約與路由文件、跨平台寫入、任何不可逆操作、以及會影響多個專案的變更。這些一律走完整路徑，沒有例外。

中途升級的規則是：一旦發現請求涉及禁止範圍，立刻升級為完整路徑並補跑缺少的步驟，已完成的步驟不重做；升級時在變更帳寫一筆，記錄升級原因與補跑清單。

LITE 的驗收條件是 AC-A00-05：判定為 LITE 時，五個條件逐條有理由，且不在禁止清單內。因為 LITE 省略獨立驗收，LITE 產物不得標為已採用，只能作為草稿或參考；要進正本或標已採用，必須補跑完整路徑。

## 12. 未決事項

| ID | 描述 | 狀態 |
|---|---|---|
| UCP-OPEN-01 | 重試上限 3／2 是否為正式數值 | PENDING_DECISION |
| UCP-OPEN-02 | 正式採用是否要求 L3（人類）驗收 | PENDING_DECISION（候選交付最低 L1；`ADOPTED` 最低 L2；正本建議 L3） |
| UCP-OPEN-03 | 預算重置的正式授權格式 | PENDING_DECISION |
| UCP-OPEN-04 | 修正帳本未讀時是否阻擋開工（目前為可繼續但須列未讀） | PENDING_DECISION |
| UCP-OPEN-05 | LITE 的「低風險」是否要改成可量化門檻（例如行數、影響檔案數） | PENDING_DECISION |
