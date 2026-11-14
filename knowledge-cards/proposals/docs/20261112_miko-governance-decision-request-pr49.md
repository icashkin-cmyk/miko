未驗收提案

# MIKO 正式裁決／放行請求通知草稿（PR #49）

> 本文件是待送出的通知草稿，不是 MIKO 裁決，不代表正式採用、放行、合併或 Runtime 啟用。

## 收件與請求

**收件者：** MIKO

**主旨：** 請裁決／放行 PR #49：Claude 治理複核邊界知識卡與候選裁決流程 Skill

**請求目的：** 請 MIKO 依前置驗收資料，明確決定本 PR 是否可正式採用、是否可放行合併，以及是否允許後續接 Runtime。Manus 不代填 MIKO 的正式決定。

## 1. 對象與範圍

- PR：[#49](https://github.com/icashkin-cmyk/miko/pull/49)
- repository：`icashkin-cmyk/miko`
- branch：`manus/governor-role-sop-20261112`
- PR 狀態：目前讀回為 `OPEN`、`isDraft=true`、尚未合併；本通知草稿仍屬候選審查材料。
- 採用軸：`PROPOSED`
- 實際撰寫者：Manus 執行總召。
- 可處理範圍（ADR-088）：`knowledge-cards/`，包含 `knowledge-cards/proposals/`；knowledge-cards 的唯一 writer 為 Manus 總召（來源：`knowledge-cards/README.md`「誰可以寫」與「分工原文」）。
- 非範圍：正式 miko-core、正式 Skills、`.github/`、`tests/`、`VERSION`、`sync/`、Runtime、PR 合併與任何交易／Broker／LIVE。
- 未開專案的領域 Skill：本次沒有取得可核對的專案專屬 writer 定義，維持 `UNKNOWN`，不自行新增 writer 規則。

## 2. 本次候選內容

1. 更新 `knowledge-cards/proposals/20261112_claude-governance-review-boundaries.md`，補上六個狀態軸的候選合法值與轉換條件。
2. 新增 `knowledge-cards/proposals/skills/governance-review-decision-flow/SKILL.md`，內容包括正式裁決／放行格式、前置驗收、狀態軸管理、衝突處理與放行後讀回要求。
3. 新增候選 Skill 只放在 `knowledge-cards/proposals/skills/`，尚未啟用，也不取代正式 Skill 或正本規則（來源：`knowledge-cards/README.md`「提案區」）。

## 3. 審查包前置資料

本通知對應的完整材料、差異與雜湊應以當次送審包為準；本可貼用正文不固定寫入會隨後續提交變動的 commit、版本號或舊雜湊。下列本輪驗收數據只適用於本次讀回的工作樹，推送後須重新讀回核對。

已確認的材料為：

- 治理邊界知識卡：`knowledge-cards/proposals/20261112_claude-governance-review-boundaries.md`
- 候選 Skill：`knowledge-cards/proposals/skills/governance-review-decision-flow/SKILL.md`
- 裁決通知草稿：本文件。
- 固定來源：GitHub PR #49 遠端 head `1a42a56a025ea1a78521fdd7bf6a5338d4d83b9e`（修訂前基線）；VERSION `1.2.72`；miko-core `v1.73`；Claude 實讀時間見證據檔 r5。本輪修訂不在該基線 head 內。
- 本輪每檔 SHA-256、PR `OPEN`／`isDraft=true`／`mergedAt=null` 讀回、C1～C16 原始輸出與 Skill validator 輸出：見 `knowledge-cards/proposals/docs/20261113_pr49-current-evidence-r5.txt`（舊檔 `20261113_pr49-current-evidence.txt` 已標 HISTORICAL／STALE，不作本輪現況）。

## 4. 前置驗收結果

### 4.1 C1～C16

前一輪以 `python3 tests/check_repo.py` 執行的結果如下；本文件在冷啟動稽核後已修改，因此這組結果不能直接當成本輪最新版本結果：

- C1～C16：前一輪均為 `PASS`。
- 總結果：前一輪 `16/16 PASS`，程序退出碼 `0`。
- C15 為提示性檢查，不阻擋；前一輪有 7 個出處例外。
- C3／C12 的前一輪輸出注明 `MIKO_PRIVATE_WORDS` 未帶或為空，只完成格式檢查，未執行私人關鍵字清單掃描。
- 本輪補強 Manus 範圍、證據標籤、困難卡四類與狀態軸後，於 2026-11-14 01:07（Asia/Taipei）重新執行 `python3 tests/check_repo.py`：C1～C16 全數 `PASS`，合計 `16/16 PASS`，程序退出碼 `0`；完整輸出保存於本輪審查包。C3／C12 因 `MIKO_PRIVATE_WORDS` 未提供或為空，仍只完成格式檢查，私人關鍵字掃描為 `NOT_RUN`。（Manus 自述；其時間戳 2026-11-14 01:07 晚於實際日期，原因 `UNKNOWN`，不採信為證據時間。）
- Claude 實跑（時間見證據檔 r5，帶專案私密字清單、未略過 C6／C9）：對 head `1a42a56` 與對本機修訂樹各跑一次，皆 C1～C16 `16/16 PASS`；C3 私人關鍵字 12 個、命中 0，C12 命中 0，即私人關鍵字掃描已執行。原始輸出見 `20261113_pr49-current-evidence-r5.txt`。r5 的輸出對應 M1～M4 修訂樹，執行時間以 r5 為準。這只是機械檢查，不等於治理通過。

### 4.2 Skill 結構驗證

本輪 `quick_validate.py --path knowledge-cards/proposals/skills/governance-review-decision-flow` 回報 `Skill is valid!`。

### 4.3 格式與遠端讀回

- 使用者冷啟動稽核已指出本草稿前一版本不合格；本輪新雜湊由重新驗證結果提供，不沿用舊雜湊。
- 本輪草稿修改後的 `git diff --check`：`PASS`。
- 本輪候選文件已完成本地驗收，並在 MIKO 2026-11-13 23:42（Asia/Taipei）說「推」後由 Claude 推送到 PR 分支（推送前基線 `1a42a56a025ea1a78521fdd7bf6a5338d4d83b9e`；各次推送的 head 與 CI 見證據檔 r5）；其後的稽核小修另有新 head，一律以 GitHub 讀回為準，不在本文件預填。
- 獨立稽核：`NOT_RUN`；獨立稽核者 `UNKNOWN`，待 MIKO 指定。
- 交接讀者測試：Manus 自述 `PASS`，讀者身分與逐題原始作答不在 PR 內（`UNKNOWN`）；完整記憶／冷啟動測試：`NOT_RUN`。兩者分開命名，前者不得升格為後者。

## 5. Claude API 自查閘門

- 最新修訂版本的 API 自查閘門：`NOT_RUN`；本通知是執行前審查包，尚未預填本次自查結果。正式閘門軸只填 `PASS／BLOCKED／NOT_RUN`，自查判定另可為 `PASS／REVISE／BLOCKED／NOT_RUN`；若自查為 `REVISE`，正式閘門標 `BLOCKED` 且不得送治理審閱，修訂後須重跑自查；`REVISE` 不適用 `NOT_RUN` 的 MIKO 當次豁免路徑（MIKO 2026-11-13 23:55 台北授權由總召決定，M1）。此閘門是本候選新增流程，是否採用由 MIKO 裁決；未採用前不宣稱為現行正本規則。
- 原因：本輪已修改守則與候選 Skill；先前 API 自查不能覆蓋本輪新內容。
- 先前舊版 API 自查的完整回覆不能擴張解讀為本輪複核。
- API 失敗、逾時、截斷、空回覆或只有 ACK 時，應標 `BLOCKED`，停止送治理審閱並開困難卡；不得填 `PASS`。
- Claude API 自查不是獨立稽核，也不授權採用、Runtime、合併或解除停止；協作 SOP §3.3.1 是本 PR 內的候選文件，不是正本；`knowledge-cards/README.md` 已由 Claude 實讀全文（讀取時間與 SHA-256 見證據檔 r5），但它不是正本，只作候選來源。

## 6. 六個狀態軸（候選值）

| 軸 | 本輪值 | 說明 |
|---|---|---|
| 來源 | `READ` | 已讀回遠端 PR head、VERSION、miko-core 與本地候選檔；遠端基線是 `1a42a56`；本輪修訂已推送，其後的稽核小修以 GitHub 讀回為準，未讀回前不得宣稱遠端已包含。 |
| 執行 | `PASS` | C1～C16、Skill validator 與 `git diff --check` 已通過；C3／C12 私人關鍵字掃描在 Manus 輪因 `MIKO_PRIVATE_WORDS` 空值為 `NOT_RUN`（Claude 的 r5 輪已帶清單實跑、命中 0，見 §4.1），此為局部工具結果，不等於治理放行。 |
| 審查 | `NOT_RUN` | 本輪修訂尚未完成 Claude 治理複核與獨立稽核。 |
| 採用 | `PROPOSED` | 尚未由 MIKO 正式採用。 |
| Runtime | `DISABLED` | 未接線、未啟用。 |
| 外部效果 | `WRITTEN` | 本輪候選檔案修改已由 Claude 推送到 PR 分支（head 見證據檔 r5，經 MIKO 當次說「推」），外部效果為 `WRITTEN`（僅 `knowledge-cards/` 內、未合併）；稽核小修的推送另計。 |

## 7. MIKO 保留決定權與常設清單

以下事項不得由 Manus 或 Claude 代替 MIKO 決定（來源：候選守則 §3.4、協作 SOP §2）：

- 解除 MIKO 設定的停止或暫緩狀態。
- 新增或擴大權限。
- 刪除、覆寫、分享、權限變更、付費或其他不可逆外部行動。
- 對外發送或他平台寫入。
- Manus 改變候選原意、硬邊界、writer 或責任範圍。
- writer 範圍或角色責任發生爭議。
- Claude 與 Manus 未解決衝突的最終裁決。

本次 PR 的決定不會自動延伸為上述其他事項的授權。

## 8. Manus、Claude 與執行者邊界

- Manus 可以在 `knowledge-cards/`（ADR-088）內建立候選、保存證據、執行已授權的唯讀查核與測試，並以分支＋PR 提案。
- Manus 不直推 `main`，不審查、不放行、不宣稱已採用、不登錄 ADR、不改 `knowledge-cards/` 以外的正式路徑；候選 PR 不等於正式採用。`knowledge-cards/README.md` 已由 Claude 實讀全文（讀取時間與 SHA-256 見證據檔 r5），不是正本，只作候選來源；不作本輪正本依據。
- Manus 的停問條件包括缺授權、外部寫入、刪除、覆寫、分享、權限、費用、Runtime、停止／暫緩或其他不可逆操作；命中時只停受影響相依步驟，維持可逆狀態（來源：候選守則 §2、協作 SOP §2）。
- 小錯的定義與處理依本 PR 內候選協作 SOP §3.3.1、§3.4（路徑、標籤、漏句、名詞、格式等不改意思者，由 Claude 判定；舊稿「純錯字、標點或格式…不改變規則、責任、狀態、數字、日期或引用」已由其取代，MIKO 2026-11-13 23:55 台北授權由總召決定，M3）；本輪涉及狀態、裁決與責任文字，不屬可免複核小錯。協作 SOP 是本 PR 內候選文件，不作正本依據。
- Claude 負責治理複核與採用前審查，不把自我複核當獨立稽核；獨立稽核由未參與修改者完成；工具驗收與 Claude 複核不算獨立稽核（MIKO 2026-11-13 23:55 台北授權由總召決定，M2）。
- 「MIKO 或總召合併」不作為本通知的授權句；本通知只請 MIKO 明確決定是否合併，Manus 不代決。

## 9. 派工、回報與責任欄位

依使用者摘要但本輪未逐條核讀的附件《總召工作守則｜雙總召行列式最新版》（`NOT_READ`）所述 A0.4、W1.2、W1.3、W6.2、W7.1～W7.2，本通知暫列下列責任欄位供候選討論；附件僅是未核讀的候選參考，不是正本、驗收依據或已生效規則：

| 責任欄位 | 本案指定內容 |
|---|---|
| 主要執行者 | Manus 執行總召：整理候選、執行可授權檢查、保存證據與建立通知草稿。 |
| writer | Manus 執行總召，限 `knowledge-cards/`（ADR-088）；不得改其他正式路徑。 |
| 治理複核者 | Claude 治理總召負責治理複核與材料門檻判定；不等於 MIKO 正式採用或獨立稽核者。 |
| 機械檢查者 | `python3 tests/check_repo.py`、Skill validator 與 `git diff --check` 的工具輸出；工具成功不能當治理放行。 |
| 獨立稽核者 | `UNKNOWN`，待 MIKO 指定；不得由本輪參與修改者擔任。獨立稽核本身為 `NOT_RUN`；不把工具驗收或 Claude 複核當成獨立稽核。 |
| 整合者 | Manus 執行總召整合候選材料；正式採用與放行仍由 MIKO 決定。 |
| 讀回者 | `UNKNOWN`，待 MIKO 指定；指定後須讀回 PR／檔案完整內容並核對版本、範圍、AC、未知、禁止事項、責任欄與交付位置。 |
| 失敗處理者 | Manus 執行總召先保存錯誤、影響與下一步；涉及治理衝突、正式採用或不可逆決定時交 Claude／MIKO。 |
| 目標位置 | PR #49 分支的 `knowledge-cards/`；本通知草稿位於 `knowledge-cards/proposals/docs/`。 |
| 宣告時間 | 以每次實際執行時記錄的 Asia/Taipei 時間為準；本通知不硬編未重新驗證的時間。 |

| 類型 | 必填內容 | 卡住或缺件時找誰 |
|---|---|---|
| 派工 | 目標、來源檔、版本／commit、責任欄、驗收條件、交付位置；必要時補輸入、禁做、AC、writer、驗收者、宣告時間與回報格式 | 缺欄先補齊；缺授權或要 MIKO 親手決定，找 MIKO |
| 回報 | 結論、影響、已完成、已寫出、已測試、已讀回、未完成、限制、證據索引與任務四態；附命令、輸出、時間與 SHA-256 | 缺資料標 `NOT_READ`／`UNKNOWN`；治理衝突交 Claude／MIKO |
| 待辦 | 尚未完成事項、依賴、解除條件、執行者、操作、輸入／工具、完成判準、失敗出口與產出物 | 缺資料、授權或決定時建立困難卡，不新增不可執行工作 |
| 交接 | 現況、已完成、未完成、待決、困難卡、來源版本／commit、下一步、完整責任欄、目標位置與任務四態 | Drive 不可用先本地保存並標 `BLOCKED`；來源變動先重新對齊 |

派工預設「不要推送，只存本地；不發文、不發訊息」；只有 MIKO 明確說「推」才推送、合併或部署。`dghp-work-handoff` 本輪未核讀，該來源狀態為 `UNKNOWN`，不作本輪正本依據。

## 10. W1～W7 編號對照

以下對照是依使用者提供的《總召工作守則｜雙總召行列式最新版》摘要建立；附件本輪未逐條核讀（`NOT_READ`），僅作候選參考，不是 GitHub 正本、正式 Skill 或正式治理裁決，未經審查與放行不得宣稱生效。

| 工作列 | 附件定義 | 本案適用驗收 |
|---|---|---|
| W1 | 直接執行或委派；W1.2 規定派工欄位，W1.3 規定受派結果由指定驗收者讀回完整結果。 | 建立本通知、指定責任欄、保存驗收與讀回證據。 |
| W2 | 文章、Skill、規則審查；完整讀取附件並逐條比對正本、專案指令與 Skill。 | 對照附件與候選治理流程 Skill，分開事實、未知與待決。 |
| W3 | Skill／規則修改；局部修改、測試、獨立稽核，提案與正式採用分開。 | 修改只限 `knowledge-cards/` 候選路徑，Skill validator 與 C1～C16 逐項驗收。 |
| W4 | 正本推送、合併與回讀；推送、開 PR、更新 PR、合併是不同授權動作。 | 本輪不自動合併；若後續獲授權，須記錄動作、CI、目標 commit 與遠端讀回 SHA。 |
| W5 | Drive 存檔；只新增到核實位置，禁止覆寫、刪除、移動、分享與改權限，完成後讀回比對。 | 本通知目前不宣稱已存 Drive；若執行，須補檔案 ID、讀回與 SHA。 |
| W6 | 回報與建設性下一步；下一步須列執行者、操作、輸入／工具、完成判準、失敗出口與產出物。 | 本通知列出重跑驗收、API 自查、獨立稽核與重審的執行責任與出口。 |
| W7 | 收工、換手與額度將盡；HANDOFF 必須包含完整責任欄、來源版本／commit、目標位置與任務四態。 | 本通知作為裁決前交接索引；未完成項不得寫成完成。 |

## 11. Drive 與跨平台寫入

- Google Drive `MIKO_ARCHIVE` 只新增，不覆寫、不刪除、不移動、不分享、不改權限；寫入後依新檔 ID 讀回並以 SHA-256 比對（來源：`dghp-work-handoff` §Drive 存檔、miko-core §7）。
- 其他跨平台寫入、對外發送與設定變更，除正本 repo 的既有授權例外外，仍需 MIKO 當次明確授權。
- 本通知不宣稱已存 Drive；本輪 Drive 存檔：`NOT_RUN`。

## 12. 需要 MIKO 明確裁決的欄位

請直接逐項回覆以下欄位；未明確允許者維持保守狀態：

- 正式採用：`YES／NO`
- 是否採用 Claude API 自查閘門：`YES／NO`
- 是否採用六軸狀態格式：`YES／NO`
- 正式放行：`YES／NO`
- 合併 PR #49：`YES／NO`
- 接 Runtime：`YES／NO`
- 解除停止或暫緩：`YES／NO／不適用`
- 是否允許對外發送：`YES／NO`
- 是否允許他平台寫入：`YES／NO`
- 生效版本：
- 生效日期（Asia/Taipei）：
- 正式存放位置：
- 必須保留的限制：
- 回滾條件與負責人：
- 裁決理由：

## 13. 保守預設

在 MIKO 明確裁決、Claude 治理複核與必要獨立稽核完成前，維持：

- `採用=PROPOSED`
- `審查=NOT_RUN`
- `Runtime=DISABLED`
- 不合併 PR
- 不修改正式正本
- 不接 Runtime
- 不把 C1～C16 全 PASS 解讀為治理放行
- 不以稽核者的日期、模型意見或舊雜湊代替本輪證據

## 14. 交接與任務四態

- 責任欄：主要執行者 Manus 執行總召；writer Manus 執行總召；治理複核者 Claude；機械檢查者為本輪工具輸出；獨立稽核者 `UNKNOWN`（待 MIKO 指定）；整合者 Manus 執行總召；讀回者 `UNKNOWN`（待 MIKO 指定）；失敗處理者 Manus 執行總召，治理裁決交 Claude／MIKO；目標位置為 PR #49 分支的 `knowledge-cards/`。
- Claude 治理複核：本輪尚未執行；正式治理審查軸為 `NOT_RUN`；API 自查閘門執行前為 `NOT_RUN`。執行後結果另存審查紀錄，不預先寫入本通知。
- 獨立稽核：`NOT_RUN`；獨立稽核者與讀回者皆 `UNKNOWN`，待 MIKO 指定。
- MIKO 正式裁決：待決。
- 任務四態：**完成但有疑慮**，理由是本輪候選修訂、C1～C16 與 Skill 驗證已完成，但 API 自查、獨立稽核、治理重審與推送後讀回以 GitHub 為準。

## 15. 稽核修訂對照

本輪依冷啟動稽核逐項處理：

- 已補：派工、回報、待辦與交接欄位；卡住對象；停止／暫緩、新權限、刪除、付費、對外發送、他平台寫入與 writer 爭議清單。
- 本輪修正：Manus 執行總召適用範圍限於 `knowledge-cards/`（含 `knowledge-cards/proposals/`）；證據標籤改回 miko-core 現行標籤；困難卡類別改回缺資料、缺決定／授權／付費、技術失敗、外部依賴四類。
- 已修：移除可貼用正文中的固定版本、commit、舊雜湊與「已實讀確認」表述；改為本輪審查包填入。
- 已補來源：Manus 停問與硬邊界、knowledge-cards writer／提案區、Drive 只新增、派工回報與交接規則。
- 已依附件補入：W1～W7 對照、A0.4 責任閘門與 W1.2／W1.3／W6.2／W7.1～W7.2 責任欄位；附件本身仍是候選細化守則，不是正式正本。
- 待辦：修正 API 自查 `REVISE` 所列缺口並重跑；若取得自查 `PASS`、治理複核允許且獲 MIKO 明確推送授權，後續推送後讀回遠端 head／SHA-256（已推送版本以 GitHub 讀回為準）；獨立稽核與 MIKO 裁決仍分開處理。

## 16. 行內證據標籤與流程鎖

本通知屬可保存候選輸出；重要主張依 miko-core 行內標籤格式標示，工具結果以證據索引保存。`NOT_READ`、`NOT_RUN`、`BLOCKED`、`CONFLICT` 仍是狀態用語，不是新增證據標籤。

- 固定版本與版本號：`【來源：GitHub PR #49 修訂前基線 head 1a42a56；VERSION 1.2.72；miko-core v1.73】`。
- C1～C16、Skill validator、`git diff --check`：`【工具：tests/check_repo.py／quick_validate.py／git diff --check】`；C3／C12 私人字掃描：Manus 輪 `NOT_RUN`，Claude r5 輪已實跑（命中 0）。
- 使用者提供的 W1～W7 附件：Manus 輪狀態 `NOT_READ`（Claude 讀取狀態 `UNKNOWN`，仍只作候選參考）；協作 SOP §3.3.1 是本 PR 內候選文件，不作正本依據。
- 本輪 API 自查：執行前為 `NOT_RUN`；執行結果應另存 request／response 與 SHA-256，不預先填入本通知；不是獨立稽核或正式放行。

API 自查執行前 `NOT_RUN`；正式治理審查 `NOT_RUN`；採用軸 `PROPOSED`；Runtime `DISABLED`。

流程鎖：通過 2 項／降級 0 項／UNKNOWN 0 項。
