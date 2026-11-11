# knowledge-cards｜Manus 任務卡（K01～K50）存放處｜2026-11-11

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

給 Manus 的規則文字（可直接貼進 Manus 的自訂指令或任務卡）：

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
