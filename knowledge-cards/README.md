# knowledge-cards｜Manus 任務卡（K01～K50）存放處｜2026-11-11（1.2.74 更新 2026-11-19）

> 名詞：正本（正式名稱：GitHub 上的正式規則來源與目前採用版本）【限制】；硬禁止（正式名稱：當次指示也不執行的禁止事項：下單、交易、Broker、LIVE）【限制】；治理（正式名稱：規則版本、變更、授權、審查與正式放行管理）【流程】；困難卡（正式名稱：失敗分類與阻塞處置卡）【處置】；定義見 skills/miko-core/references/term-definitions.md（MIKO 核心詞彙與行為定義表）。本檔的「總召」指 MIKO 指定負責協調與寫入範圍的 AI（正本 README §6）；「單一 writer」指一個範圍只有一個寫入者。

## 這個資料夾是什麼

- 存放 MIKO 給 Manus 用的任務卡（正式名稱：Manus 平台的自訂指令卡，每張含「名稱、在以下情況下使用、內容」三欄，內容欄以 Manus 介面 1,000 字元為上限），編號 K01～K50，一張一檔：`K01.md`、`K02.md`……
- 不是 MIKO 正本，也不是 Skill。卡片和正本（README.md、skills/miko-core/SKILL.md）衝突時，以正本為準；卡片不能解除正本的停止、暫緩、硬禁止與授權規則。

## 誰可以寫（雙總召試行，正本 1.2.65，ADR-088）

| 範圍 | 唯一寫入者（單一 writer） | 依據 |
|---|---|---|
| knowledge-cards/ 本資料夾 | **Manus 總召** | MIKO 2026-11-11 17:43（台北）「請直接執行 並 修改改成 manus 換人當當看」、17:43「應該是 claude 總召 跟 manus總召」 |
| 其他所有檔案（README.md、VERSION、CHANGELOG.md、skills/、tests/、sync/、adapters/、projects/；sync/gpt/ 依正本 README §4 為已停用的歷史例外） | Claude 總召 | 正本 README §6 |

- 首批檔案（本 README、K01.md、proposals/README.md）由 Claude 總召依 MIKO 同一則指示代為建立；之後本資料夾由 Manus 總召維護。
- Manus 總召不是治理總召：不審查、不放行門檻、不宣稱已採用、不登錄 ADR、不改正本版本號；正本裡寫「總召」「治理總召」之處都指 Claude 總召。Manus 的困難卡、改善提案放 proposals/，只算提案，要 Claude 總召審查採納後才進正本。
- PR 內文必填：目標路徑、完整檔案內容或 diff、字數與名詞檢查結果、和其他卡片或正本的衝突檢查、還不知道的事（UNKNOWN）；合併後 Manus 總召讀回 main 上的檔案，回報 commit、路徑與內容是否一致。
- Manus 總召不得直接寫入 main，也不得以「Claude 讀不到 GitHub」為由改成直寫：Claude 的工作串讀得到 GitHub、看得到 PR；只有總召對話那一層沒有讀取工具，那時由總召派工作串實讀，回報寫明是哪個工作串讀的。
- 卡片 PR 只改本資料夾，不升正本版本、不加 CHANGELOG；Claude 總召合併前照正本 README §6 確認，卡片內容涉及規則改動時改走正本改版與獨立稽核。
- Manus 總召的寫入方式：開分支 → 改本資料夾的檔案 → 開 PR → GitHub Actions check_repo 通過 → Claude 總召審查（查是否和正本衝突、有無私密字或金鑰、內容欄 ≤ 1,000 字元、名詞行；合併前在本機帶私密字清單跑 check_repo，16 項全過才合併）→ MIKO 或 Claude 總召合併。不直推 main，不改本資料夾以外的檔案。
- Manus 要有 GitHub 寫入權，需要 MIKO 親手授權；授權前 Manus 只產出全文，由 MIKO 轉給 Claude 總召代放；代放時 Claude 總召同樣開分支＋PR，PR 內文照本節必填。新卡加進 tests/glossary_scope.txt（C16 名詞檢查範圍）由 Claude 總召在合併時一併處理。金鑰或 Token 不寫進任何檔案、PR 或對話。
- 試行：MIKO 說停止或改回，就恢復成 Claude 總召唯一寫入；已合併的卡片保留。

## 2026-11-19 更新（正本 1.2.74，ADR-097）：可改範圍與審核

MIKO 2026-11-19 16:51（台北）「我說 manus 權限跟你相同都可以更改全部文件 但是 最終審核者是我」，並於 16:56、17:04、17:06、17:42、17:43 回答後續各題（原話與完整條文見 README §6「可改範圍與審核」條，以該條為準）。凡本檔其他各節（含下方「誰可以寫」「分工原文」「提案區」與其中給 Manus 的規則文字）與 README §6 該條不一致的句子，一律以該條為準；下表是逐字列舉，沒列出的不一致句子同樣適用此句。本檔第 52 行原有的「兩節若有出入，以較嚴的一邊為準」只用在「誰可以寫」與「分工原文」兩節之間，不用在本節與它們之間。

| 項目 | 自 1.2.74 起 | 被取代的原句（逐字，保留不刪） |
|---|---|---|
| 可改範圍 | 在本 repo 內，Manus 總召與 Claude 總召可改的檔案範圍相同，含 skills/、tests/、.github/、VERSION、sync/；程式與網站 repo 的寫入者仍是 Claude，其他專案的 writer 不變 | 「Manus 總召是 knowledge-cards/（Manus 任務卡 K01～K50）的唯一寫入者」（README）、「不直推 main，不改本資料夾以外的檔案」（第 22 行）、「Manus 不直推 main，不改正本、Skill 正文、tests、sync、版本號」中關於 Manus 寫入範圍的部分（第 49 行）、「Manus 總召不得直接寫入 main」（第 20 行）、第 47 行「Claude 治理總召負責正本（GitHub icashkin-cmyk/miko）、Skill、tests、版本號、審查與放行；實際讀取、推送、合併由 Claude 的 GitHub 專責工作串執行」中關於合併與推送的執行者、本檔「誰可以寫」表第一列（唯一寫入者 Manus 總召）與第二列、第 17 行「之後本資料夾由 Manus 總召維護」、第 23 行「新卡加進 tests/glossary_scope.txt（C16 名詞檢查範圍）由 Claude 總召在合併時一併處理」（改為合併前就在同一個 PR 內做好）、第 47 行「Claude 治理總召負責正本（GitHub icashkin-cmyk/miko）、Skill、tests、版本號、審查與放行」中與範圍相同衝突的部分、skills/make-skill/SKILL.md S9 的「→ `git push origin main`」與 skills/dghp-work-handoff/SKILL.md 的 ADR-016 常設授權句（對推 main 與合併進 main 的部分，見 README §6 (1)） |
| 提案區 | proposals/ 仍可使用，不再強制；搬入高風險路徑改依 README §6 的合併條件 | 「一律先放」「誰搬進正式路徑」「搬入哪些屬高風險」「越界處理」、「寫入者、PR 流程、審查與放行都不變」（第 56 行）、「Manus 的 PR 不含正式路徑的檔」（第 64 行）、第 63 行「Manus 仍不能做」中的「改 knowledge-cards/ 以外的路徑；……合併；登錄 ADR；改版本號」、第 18 行「要 Claude 總召審查採納後才進正本」、proposals/README.md 第 6 行「才由 Claude 總召寫進正本」、下方「給 Manus 的規則文字」整段（1.2.74 起不適用，改依 README §6） |
| 合併或推 main | 先推分支並開 draft PR 讓 CI 跑；check_repo 16 項全過（合併後的樹；C15 只提示不擋）、獨立稽核通過、CI 綠、MIKO 當次明說同意（綁定該 commit）四項同時成立才可合併或直推 main；直推的做法見 README §6 (2) | 「不直推 main」、「→ MIKO 或 Claude 總召合併」（第 22 行）、第 48 行「check_repo 全過、CI 為綠、確認 main 未被別人改動後，由 MIKO 或 Claude 合併」與「Manus 若取得 GitHub 寫入連線（待 MIKO 在 GitHub 設定），也只能開分支與 PR」、「本正本 repo 由治理總召依常設授權直接推 main」（README §7、miko-core §7）、「有常設推送授權時（只限本 repo），推送或合併前仍要寫出請確認那則」（README §7）對推 main 與合併進 main 的部分 |
| 審查與放行 | Claude 總召在 MIKO 審核前做審查與獨立稽核（給 MIKO 的意見）；Manus 總召仍不審查、不放行；最終放行是 MIKO | （無被取代的 Manus 句；Claude 小修直接合併取消） |
| ADR 與版本號 | 兩個總召都可提出，MIKO 審核後生效 | 「不登錄 ADR、不改正本版本號」（第 18 行）、「卡片 PR 只改本資料夾，不升正本版本、不加 CHANGELOG」（第 21 行） |
| 同時改同檔 | 開工前查所有 open PR 已改動或已登記的路徑；重疊者為後到者，停下回報 MIKO，先到的 PR 合併或關閉後 rebase 到最新 main、重新登記才可繼續；不重疊者照常進行 | （描述，非原句）單一 writer 的做法（knowledge-cards/ 只有 Manus 總召寫入）；第 49 行「與進行中的正本改版衝突、要刪除或搬動既有檔、同路徑已有不同內容，都算重工，先回報，不硬開」自 1.2.74 起改依 README §6 (5) 的限定（原句保留） |
| 小錯代修 | 保留：Claude 總召可代修 Manus 分支上的小錯（路徑、標籤、漏一句、名詞、格式、機械性 C3 失敗、檔頭），不改意思、不含刪除內容或改寫私人資訊的判斷、列改動清單、修完等 MIKO 審核 | （原只在專案記憶，現寫進正本） |
| 改自己已合併的卡片 | 改內容與改狀態走同一流程；刪檔與搬檔先回報 | 第 49 行「要刪除或搬動既有檔……都算重工，先回報」對自己卡片的部分改為：改內容與狀態可直接走流程，刪檔與搬檔先回報 |
| sync/ | §4 對 sync/ 的常設授權（各平台的 sync 檔直接推到 main、只動自己的檔）維持原樣，不受合併條件約束；只限 §4 已列給該平台的 sync 檔，Manus 總召目前沒有，要新增先問 MIKO；sync/ 內他方的檔仍依 §4 不改；常設授權範圍以外、屬自己的 sync 檔修改適用 README §6 (2) | — |

不變：下單、交易、Broker、LIVE 硬禁止；台指期 STOPPED_BY_USER；回測 PAUSED_BY_USER；金鑰不收不寫不複述；卡片和正本衝突時以正本為準；MIKO 說停止或改回即恢復。本節未處理、待 MIKO 決定的事：CI「Manus PR 越界提示」（ADR-093）要不要改成會擋或移除，目前維持只提示不擋，對改 knowledge-cards/ 以外的 manus/ 分支 PR 會印 warning（不代表違規）；CI 只在 PR 與 main 觸發，要不要改成分支推送也觸發（.github 改動）；「Manus 自己平台上才做得到的工作」的範圍，及其對外寫入是否仍先問 MIKO（目前仍先問）。

## 分工原文（MIKO 2026-11-11 17:55 確認「直接生效」；總召專案 project chat 原文逐字照錄，不改寫）

```text
【分工】Claude 治理總召負責正本（GitHub icashkin-cmyk/miko）、Skill、tests、版本號、審查與放行；實際讀取、推送、合併由 Claude 的 GitHub 專責工作串執行。Manus 總召負責 knowledge-cards/（含 proposals/）內的知識卡 K01～K50 候選稿、格式與字數檢查、困難卡與改善提案，以及它自己平台上才做得到的工作。
【可達成的條件】Manus 把要開的路徑與完整內容交給 MIKO 轉貼；專責串在 knowledge-cards/ 與候選分支免逐項問，直接開 draft PR；check_repo 全過、CI 為綠、確認 main 未被別人改動後，由 MIKO 或 Claude 合併；合併後讀回 SHA-256，並回報路徑、commit、PR 連結。Manus 若取得 GitHub 寫入連線（待 MIKO 在 GitHub 設定），也只能開分支與 PR。
【邊界】Manus 不直推 main，不改正本、Skill 正文、tests、sync、版本號，不審查、不放行，也不是治理總召。與進行中的正本改版衝突、要刪除或搬動既有檔、同路徑已有不同內容，都算重工，先回報，不硬開。回測暫停、台指期停止、下單交易與 Broker 硬禁止、金鑰不收不寫，一律不變。Claude 沒讀到的內容標 NOT_READ，未實跑的標 NOT_RUN，不宣稱已完成獨立稽核。
```

- 本節和上一節「誰可以寫」意思相同，是上一節的原文版本；兩節若有出入，以較嚴的一邊為準，並回報 Claude 總召。

## 提案區（1.2.69，ADR-092）

MIKO 2026-11-11 22:35（台北）在總召專案回「１」，選「放寬提案區範圍」。只放寬提案可以針對的對象與放置位置；寫入者、PR 流程、審查與放行都不變。

| 項目 | 規則 |
|---|---|
| 可提案的對象 | 任何對象：Skill、tests、workflow（.github/）、規則（README、miko-core）、文件、設定 |
| 放哪裡 | 一律先放 knowledge-cards/proposals/<類型>/，<類型> 用 skills、tests、workflow、rules、docs 其中之一，沒有適合的先問 Claude 總召；一件提案一個子資料夾或一個檔 |
| 內容形式 | 文字或「完整替換稿」（整個檔改完後的全文，標明要取代哪個路徑）；不要只貼片段；放 proposals/ 的 SKILL.md 格式檔只是提案，不會被啟用 |
| Manus 仍不能做 | 改 knowledge-cards/ 以外的路徑；審查；放行；合併；登錄 ADR；改版本號 |
| 誰搬進正式路徑 | 只有 Claude 總召，審查後才搬；Manus 的 PR 不含正式路徑的檔 |
| 搬入哪些屬高風險 | skills/、.github/、tests/、VERSION、sync/ 屬本體或高風險變更：走原稽核（局部修改、C11、獨立稽核、CI 綠、確認 main 未動），並需 MIKO 逐件、當次明確批准才合併（引用 MIKO 該則訊息；常設免問推送授權不算） |
| 搬入方式 | 替換稿只當參考，一律局部修改搬入、不整份覆蓋（Skill 照 C11），README、CHANGELOG、adapters 等也一樣 |
| 檔頭標記 | 替換稿不能在第一行寫「未驗收提案」時（例如 SKILL.md 第一行必須是 frontmatter），改在同資料夾放一個說明檔寫「未驗收提案」與目標路徑，搬入時移除 |
| 越界處理 | PR 含 knowledge-cards/ 以外的檔，Claude 總召不審內容，先請 Manus 移除或由 MIKO 決定還原；事後不以「內容沒問題」補認 |

給 Manus 的規則文字（可直接貼進 Manus 的自訂指令或任務卡；1.2.74 起本段不適用，改依 README §6「可改範圍與審核」條，貼用前須更新）：

```text
提案範圍（正本 1.2.69，ADR-092）：你可以對任何對象提案（Skill、tests、workflow、規則、文件），但一律先放 knowledge-cards/proposals/<類型>/（類型：skills、tests、workflow、rules、docs），用文字或整個檔改完後的完整替換稿，標明要取代哪個路徑。走分支加 PR，PR 只含 knowledge-cards/ 內的檔。不要改 knowledge-cards/ 以外的任何路徑，包含 .github/、skills/、tests/、VERSION、sync/；不審查、不放行、不合併、不登錄 ADR、不改版本號。Claude 總召審查後才搬進正式路徑，搬入 skills/、.github/、tests/、VERSION、sync/ 還要 MIKO 逐件、當次明確批准（常設免問推送授權不算）。proposals/ 內的 SKILL.md 格式檔只是提案，不是已啟用的 Skill。
```

## 卡片狀態

每張卡的檔頭寫一行「狀態」，只能是下列之一：
- 候選：寫好但未在 Manus 實測。
- 已實測：在 Manus 跑過觸發測試，附測試輸入與結果。
- 停用：不再使用（不刪檔，改這一行並寫原因）。

## 索引

| 編號 | 名稱 | 狀態 | 最後更新 |
|---|---|---|---|
| K01 | 核心任務辨識與後設控制循環 | 候選 | 2026-11-11 |
