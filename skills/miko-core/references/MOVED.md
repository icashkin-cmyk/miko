# miko-core 附檔：搬移對照（原位置 → 新位置）

- 1.2.43 修剪站（MIKO 2026-11-08 21:19 指示、總召 11-09 裁決）：只搬不刪，搬移那一步句子原文不改、ID 不改不重用；搬移後同版的修改逐條列在本檔最後。
- 舊行號對 a816be1（正本 1.2.41）。SHA-256 是被搬整段（含換行）的雜湊，新位置的「搬移原文開始／結束」之間與它相同。

| 原位置（a816be1） | 行數 | bytes | 新位置 | 正文留下 | SHA-256 |
|---|---|---|---|---|---|
| SKILL.md §2.4 領域 Skill 格式 第 61-63 行 | 3 | 5780 | references/skill-format.md | 一行指回 | 4798828b13033151eb7911b14915626ef85368f9c7d21137088be61b66020828 |
| SKILL.md §4 研究與查核細則 第 184-198 行 | 15 | 5649 | references/research-and-dating.md | 一行指回 | 2c0ca71df18dd3a2282866975068a05b2c52f14b588954292a1a107bda44966d |
| SKILL.md §4 整理、重構、去重的保真細則 第 199-210 行 | 12 | 3617 | references/fidelity.md | 一行指回 | abb92e0ad8837e775a290578728697df304865b4324da48d0394b4f1f48f1c04 |
| SKILL.md §4 提示詞與 Skill 行為驗證 第 211-226 行 | 16 | 3836 | references/skill-testing.md | 一行指回 | 2ad6d415205f7ebed58545215bd0fb748df75c0bd3f1fae2d3d2e5433887b6be |
| SKILL.md §4 工程與交付常見錯誤 第 229-234 行 | 6 | 820 | references/engineering-pitfalls.md | 一行指回 | 9de4c2e2b3c22fe89085f277a11633799a1b7588f56f721eeda5ba89a4c5417d |
| SKILL.md §4 證據與狀態 第 235-243 行 | 9 | 3529 | references/evidence-states.md | 一行指回 | 14ef6763222c0a647c3c7cb64bc6dd2b76f0cad3c8473c72317bb03ed8477dbc |
| SKILL.md §5.1 核心指令六欄表 第 267-284 行 | 18 | 9374 | references/core-index.md | 一行指回 | b7c10679b75612437c204cd3db39cdf19b5d7b430649cba72caca752f666be05 |

- 留在正文沒搬的一行：a816be1 第 244 行「換聊天室」子項（原屬 §4「證據與狀態」，搬移範圍只到第 243 行），現在以縮排子項掛在正文「證據與狀態」指回行下面；evidence-states.md 不含這一行，兩處合起來才是原「證據與狀態」全文（1.2.43 稽核第一輪必改 3）。
- 搬移後的內容修改（同一版、另一個工作 commit 之後做）：core-index.md 的 K9 依 P9 改了一句（「流程鎖一行每則回覆都寫（ADR-064）」→「流程鎖一行除停止回覆外每則回覆都寫（ADR-064；停止回覆免寫、硬禁止回覆照寫，1.2.43 P9）」），所以 core-index.md 現在的區段雜湊和上表不同；上表 SHA-256 對的是純搬移那一步。其餘六個附檔區段與上表相同。
- 搬移後在正文新增的摘要：§4「提示詞與 Skill 行為驗證」指回行下加一行「修規則要對準通則」摘要（總召 2026-11-09 裁決：讀不到 raw 的環境也要看得到這條）；附檔 skill-testing.md 原文不動。
- 指回行措辭：原寫「原文不改」，改為「搬移時原文不改；搬移後的修改逐條記在 references/MOVED.md」，因為 core-index.md 搬移後改了 K9 一句（總召 2026-11-09 裁決如實更正）。

## 本版推送時的區段雜湊（重算）

| 附檔 | 純搬移那一步（上表） | 本版推送時 | 結果 |
|---|---|---|---|
| references/skill-format.md | 4798828b13033151eb7911b14915626ef85368f9c7d21137088be61b66020828 | 4798828b13033151eb7911b14915626ef85368f9c7d21137088be61b66020828 | 相同 |
| references/research-and-dating.md | 2c0ca71df18dd3a2282866975068a05b2c52f14b588954292a1a107bda44966d | 2c0ca71df18dd3a2282866975068a05b2c52f14b588954292a1a107bda44966d | 相同 |
| references/fidelity.md | abb92e0ad8837e775a290578728697df304865b4324da48d0394b4f1f48f1c04 | abb92e0ad8837e775a290578728697df304865b4324da48d0394b4f1f48f1c04 | 相同 |
| references/skill-testing.md | 2ad6d415205f7ebed58545215bd0fb748df75c0bd3f1fae2d3d2e5433887b6be | 2ad6d415205f7ebed58545215bd0fb748df75c0bd3f1fae2d3d2e5433887b6be | 相同 |
| references/engineering-pitfalls.md | 9de4c2e2b3c22fe89085f277a11633799a1b7588f56f721eeda5ba89a4c5417d | 9de4c2e2b3c22fe89085f277a11633799a1b7588f56f721eeda5ba89a4c5417d | 相同 |
| references/evidence-states.md | 14ef6763222c0a647c3c7cb64bc6dd2b76f0cad3c8473c72317bb03ed8477dbc | 14ef6763222c0a647c3c7cb64bc6dd2b76f0cad3c8473c72317bb03ed8477dbc | 相同 |
| references/core-index.md | b7c10679b75612437c204cd3db39cdf19b5d7b430649cba72caca752f666be05 | 7451f110f5ef8af88e05be1444b890962890fd7392f9476ae4c7d21e9cbf9af7 | 不同（搬移後修改，見下方逐條） |

## 1.2.45 搬移後修改（ADR-068，只新增；上方兩張表不改）
- core-index.md 的 K9：括號尾加「同一則兼有停止與硬禁止時第二行（非新對話時第一行，換領域對齊行也不寫）STOPPED_BY_USER、接硬禁止說明、最後一行照寫，1.2.45 P12」。
- research-and-dating.md：「任務不涉及任何來源日期時不用列（ADR-047）。」之後加一句日期一行的範圍（只在引用外部來源時寫；只讀 VERSION 對齊、停止回覆不寫；1.2.45 P13）；原句不改。
- skill-testing.md：「修規則要對準通則」子項下加一個子子項「新題的用詞」（新題的題目、觸發詞與 forbidden 不得照抄這次修補新增的關鍵用詞或例詞，領域名稱、狀態標籤等固定名詞不算；1.2.45 P15）；原句不改。
- 這三處修改後，三個附檔的區段雜湊和上方兩張表不同；上方兩張表不改。本版改後的整檔 SHA-256（整個檔案，不是上方表的區段雜湊）如下，之後再改這三檔時在本檔新增一節：

| 附檔 | 1.2.45 整檔 SHA-256 |
|---|---|
| references/core-index.md | 52bcb76e01ff717d2f95ecbfd50ce2a58414a813a3e2116d1f1bc4a3b629cd1b |
| references/research-and-dating.md | 441d93c0ba7f414e936efbd88736cb6e332f4b734a1c68a0df83cd6064ceb78a |
| references/skill-testing.md | 68b20b26c09921ad711590b7628642faa08b2dfb7a6a8ae2f069df546a9cf65d |
