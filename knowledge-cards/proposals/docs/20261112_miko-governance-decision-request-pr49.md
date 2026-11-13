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
- 可處理範圍：`knowledge-cards/`，包含 `knowledge-cards/proposals/`；knowledge-cards 的唯一 writer 為 Manus 總召（來源：`knowledge-cards/README.md`「誰可以寫」與「分工原文」）。
- 非範圍：正式 miko-core、正式 Skills、`.github/`、`tests/`、`VERSION`、`sync/`、Runtime、PR 合併與任何交易／Broker／LIVE。
- 未開專案的領域 Skill：本次沒有取得可核對的專案專屬 writer 定義，維持 `UNKNOWN`，不自行新增 writer 規則。

## 2. 本次候選內容

1. 更新 `knowledge-cards/proposals/20261112_claude-governance-review-boundaries.md`，補上六個狀態軸的候選合法值與轉換條件。
2. 新增 `knowledge-cards/proposals/skills/governance-review-decision-flow/SKILL.md`，內容包括正式裁決／放行格式、前置驗收、狀態軸管理、衝突處理與放行後讀回要求。
3. 新增候選 Skill 只放在 `knowledge-cards/proposals/skills/`，尚未啟用，也不取代正式 Skill 或正本規則（來源：`knowledge-cards/README.md`「提案區」）。

## 3. 審查包前置資料

本通知對應的完整材料、差異與雜湊應以當次送審包為準；本可貼用正文不固定寫入會隨後續提交變動的 commit、版本號或舊雜湊。

已確認的材料為：

- 治理邊界知識卡：`knowledge-cards/proposals/20261112_claude-governance-review-boundaries.md`
- 候選 Skill：`knowledge-cards/proposals/skills/governance-review-decision-flow/SKILL.md`
- 裁決通知草稿：本文件。
- 固定來源、commit、VERSION、ADR、讀取時間、每檔 SHA-256：由當次審查包填入，若未讀取則寫 `NOT_READ`，不得以舊回報代替。

## 4. 前置驗收結果

### 4.1 C1～C16

前一輪以 `python3 tests/check_repo.py` 執行的結果如下；本文件在冷啟動稽核後已修改，因此這組結果不能直接當成本輪最新版本結果：

- C1～C16：前一輪均為 `PASS`。
- 總結果：前一輪 `16/16 PASS`，程序退出碼 `0`。
- C15 為提示性檢查，不阻擋；前一輪有 7 個出處例外。
- C3／C12 的前一輪輸出注明 `MIKO_PRIVATE_WORDS` 未帶或為空，只完成格式檢查，未執行私人關鍵字清單掃描。
- 本輪新增 Manus 範圍、證據標籤與困難卡分類修訂後，已重新執行 C1～C16：`PASS`，合計 `16/16 PASS`，程序退出碼 `0`；C3／C12 仍因 `MIKO_PRIVATE_WORDS` 未提供或為空，只完成格式檢查。

### 4.2 Skill 結構驗證

本輪 `quick_validate.py --path knowledge-cards/proposals/skills/governance-review-decision-flow` 回報 `Skill is valid!`。

### 4.3 格式與遠端讀回

- 使用者冷啟動稽核已指出本草稿前一版本不合格；本輪新雜湊由重新驗證結果提供，不沿用舊雜湊。
- 本輪草稿修改後的 `git diff --check`：`PASS`。
- 本輪候選文件已完成本地驗收但尚未推送；遠端 PR head 仍以當次讀回結果為準，不能宣稱遠端已包含本輪修訂。
- 獨立稽核：本輪修訂後待重新執行。

## 5. Claude API 自查閘門

- 最新修訂版本的 API 自查閘門：`NOT_RUN`。
- 原因：本輪已修改通知草稿；先前 API 自查不能覆蓋本輪新內容。
- 先前舊版 API 自查的完整回覆不能擴張解讀為本輪複核。
- API 失敗、逾時、截斷、空回覆或只有 ACK 時，應標 `BLOCKED`，停止送治理審閱並開困難卡；不得填 `PASS`。
- Claude API 複核不是獨立稽核，也不授權採用、Runtime、合併或解除停止（來源：候選協作 SOP §3.3.1 及 `knowledge-cards/README.md` 分工邊界）。

## 6. 六個狀態軸（候選值）

| 軸 | 本輪值 | 說明 |
|---|---|---|
| 來源 | `READ` | 本輪已讀取候選守則、裁決通知、候選 Skill、附件與 miko-core／VERSION；本輪修改尚未推送至遠端。 |
| 執行 | `PASS` | 本輪已完成 C1～C16、Skill validator 與 `git diff --check`。 |
| 審查 | `NOT_RUN` | 本輪修訂尚未完成 Claude 治理複核與獨立稽核。 |
| 採用 | `PROPOSED` | 尚未由 MIKO 正式採用。 |
| Runtime | `DISABLED` | 未接線、未啟用。 |
| 外部效果 | `WRITTEN` | 前一版本曾推送至 PR 分支；本輪三個候選檔案修改尚在本地工作樹，尚未推送。 |

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

- Manus 可以在 `knowledge-cards/` 內建立候選、保存證據、執行已授權的唯讀查核與測試，並以分支＋PR 提案。
- Manus 不直推 `main`，不審查、不放行、不宣稱已採用、不登錄 ADR、不改 `knowledge-cards/` 以外的正式路徑；候選 PR 不等於正式採用（來源：`knowledge-cards/README.md`）。
- Manus 的停問條件包括缺授權、外部寫入、刪除、覆寫、分享、權限、費用、Runtime、停止／暫緩或其他不可逆操作；命中時只停受影響相依步驟，維持可逆狀態（來源：候選守則 §2、協作 SOP §2）。
- 純錯字、標點或格式的小錯，只有在不改變規則、責任、狀態、數字、日期或引用，且仍保留 diff 並依稽核規則重新確認時，才可列為小錯；本輪涉及狀態、裁決與責任文字，不屬可免複核小錯（來源：協作 SOP §3.3.1）。
- Claude 負責治理複核與採用前審查，不把自我複核當獨立稽核；獨立稽核由未參與修改者或機械檢查完成。
- 「MIKO 或總召合併」不作為本通知的授權句；本通知只請 MIKO 明確決定是否合併，Manus 不代決。

## 9. 派工、回報與責任欄位

依附件《總召工作守則｜雙總召行列式最新版》A0.4、W1.2、W1.3、W6.2、W7.1～W7.2，本通知使用下列責任欄位：

| 責任欄位 | 本案指定內容 |
|---|---|
| 主要執行者 | Manus 執行總召：整理候選、執行可授權檢查、保存證據與建立通知草稿。 |
| writer | Manus 執行總召，限 `knowledge-cards/`；不得改其他正式路徑。 |
| 驗收者 | Claude 治理總召負責治理複核；C1～C16 與 Skill validator 由本執行階段實際執行並保存輸出，不能把工具成功當治理放行。 |
| 整合者 | Manus 執行總召整合候選材料；正式採用與放行仍由 MIKO 決定。 |
| 讀回者 | 指定的後續執行者，須讀回 PR／檔案完整內容並核對版本、範圍、AC、未知、禁止事項、責任欄與交付位置。 |
| 失敗處理者 | Manus 執行總召先保存錯誤、影響與下一步；涉及治理衝突、正式採用或不可逆決定時交 Claude／MIKO。 |
| 目標位置 | PR #49 分支的 `knowledge-cards/`；本通知草稿位於 `knowledge-cards/proposals/docs/`。 |
| 宣告時間 | 以每次實際執行時記錄的 Asia/Taipei 時間為準；本通知不硬編未重新驗證的時間。 |

| 類型 | 必填內容 | 卡住或缺件時找誰 |
|---|---|---|
| 派工 | 目標、來源檔、版本／commit、責任欄、驗收條件、交付位置；必要時補輸入、禁做、AC、writer、驗收者、宣告時間與回報格式 | 缺欄先補齊；缺授權或要 MIKO 親手決定，找 MIKO |
| 回報 | 結論、影響、已完成、已寫出、已測試、已讀回、未完成、限制、證據索引與任務四態；附命令、輸出、時間與 SHA-256 | 缺資料標 `NOT_READ`／`UNKNOWN`；治理衝突交 Claude／MIKO |
| 待辦 | 尚未完成事項、依賴、解除條件、執行者、操作、輸入／工具、完成判準、失敗出口與產出物 | 缺資料、授權或決定時建立困難卡，不新增不可執行工作 |
| 交接 | 現況、已完成、未完成、待決、困難卡、來源版本／commit、下一步、完整責任欄、目標位置與任務四態 | Drive 不可用先本地保存並標 `BLOCKED`；來源變動先重新對齊 |

派工預設「不要推送，只存本地；不發文、不發訊息」；只有 MIKO 明確說「推」才推送、合併或部署（來源：`dghp-work-handoff`「派工」）。

## 10. W1～W7 編號對照

以下對照直接取自使用者提供的《總召工作守則｜雙總召行列式最新版》；該附件是 W1～W7 的可執行細化守則，但不是 GitHub 正本、正式 Skill 或正式治理裁決，未經審查與放行不得宣稱生效。

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

- 責任欄：主要執行者 Manus 執行總召；writer Manus 執行總召；驗收者 Claude 治理總召／本輪指定機械檢查；整合者 Manus 執行總召；讀回者待本輪重跑時指定；失敗處理者 Manus 執行總召，治理裁決交 Claude／MIKO；目標位置為 PR #49 分支的 `knowledge-cards/`。
- Claude 治理複核：本輪待送審。
- 獨立稽核：本輪待重審。
- MIKO 正式裁決：待決。
- 任務四態：**完成但有疑慮**，理由是本輪三處修訂與 C1～C16／Skill 驗證已完成，但 API 自查、獨立稽核、治理重審與本輪修改推送尚未完成。

## 15. 稽核修訂對照

本輪依冷啟動稽核逐項處理：

- 已補：派工、回報、待辦與交接欄位；卡住對象；停止／暫緩、新權限、刪除、付費、對外發送、他平台寫入與 writer 爭議清單。
- 本輪修正：Manus 執行總召適用範圍限於 `knowledge-cards/`（含 `knowledge-cards/proposals/`）；證據標籤改回 miko-core 現行標籤；困難卡類別改回缺資料、缺決定／授權／付費、技術失敗、外部依賴四類。
- 已修：移除可貼用正文中的固定版本、commit、舊雜湊與「已實讀確認」表述；改為本輪審查包填入。
- 已補來源：Manus 停問與硬邊界、knowledge-cards writer／提案區、Drive 只新增、派工回報與交接規則。
- 已依附件補入：W1～W7 對照、A0.4 責任閘門與 W1.2／W1.3／W6.2／W7.1～W7.2 責任欄位；附件本身仍是候選細化守則，不是正式正本。
- 待辦：讀回最新 PR head；完成最新版本 Claude API 自查與獨立稽核；若獲授權再推送本輪候選修訂；再送 MIKO 裁決。
