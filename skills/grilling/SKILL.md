---
name: "grilling"
description: "逐輪拷問計畫或決策直到雙方理解一致。使用者說 grill、grill me、/grill-me、grill-me、「拷問我」「對照文件拷問」「壓力測試這個方案」「逐題問到清楚」時使用；一般問答不使用。"
---

# grilling v1.0｜逐輪拷問到理解一致｜2026-11-10

> 名詞（1.2.53，ADR-076）：本檔短名詞第一次出現在這一行，寫成「短名（正式名稱）【類型】」；每個名詞的定義、觸發條件、執行動作、輸出格式、完成判準、失敗處理、不適用情況、相關名詞見 MIKO 核心詞彙與行為定義表（skills/miko-core/references/term-definitions.md，https://raw.githubusercontent.com/icashkin-cmyk/miko/main/skills/miko-core/references/term-definitions.md）。治理（正式名稱：規則版本、變更、授權、審查與正式放行管理）【流程】；正本（正式名稱：GitHub 上的正式規則來源與目前採用版本）【限制】。

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Word each question so "yes" accepts your recommended answer.

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.

## MIKO 調整（2026-10-30，H-06；與上文衝突時以這節為準）
- 只在 MIKO 明確啟動時用（說 grill、grill me、/grill-me、grill-me、拷問、壓力測試、逐題問到清楚；1.2.64 補斜線寫法），一般問答與小問題不用。
- 每題的推薦答案要附代價與一個替代做法。MIKO 回「是」只代表接受那一題的推薦答案，不代表授權任何外部操作或整包同意。
- 已經決定的事不重問；低風險細節直接採合理假設並註明，不為追問而追問。
- 查事實自己用工具查；只有大量、可平行的查找才開子代理（miko-core §4 多代理規則），不為每個小問題派子代理。
- 還有未決的相依決策時不動手實作；不依賴它的唯讀研究可以繼續。
- 一輪最多 5 題；可問的超過 5 題時，先問最影響結果的，其餘延到下一輪。MIKO 說「夠了」，或剩下的問題都不影響結果，就結束並整理共識。
- 每題格式在 ➡️ 推薦答案下面多一行「💰 代價／替代：……」。
- 文件對照模式（ADR-042；MIKO 說「對照文件拷問」「對正本拷問」，或拷問的對象是規則、Skill、ADR 時）：每輪先讀相關正本段落與 ADR；MIKO 用的名詞和正本定義不一致時當場指出並問用哪個；舉具體情境測邊界；MIKO 說的做法和程式或正本不符時直接指出矛盾。共識要寫入文件時，只產出可貼用的修改草稿，寫入照 miko-core §6 治理流程，不在拷問途中直接改 repo；正本的名詞以 repo 現有文字為準，正本沒寫的不當成規則引用。
- 建議記 ADR 的時機（ADR-042）：難以反悔、沒有脈絡的人會疑惑「為什麼這樣做」、確實在幾個真實替代方案中取捨，三項都成立就主動建議記 ADR；只成立部分時記在 CHANGELOG 或交接檔即可。MIKO 明說要記 ADR 時一律照記。這只管拷問途中要不要提議；共識走 miko-core §6 治理房收件、要改正本時，照 §6 登錄 ADR（§6 優先）。
- 驗收題：MIKO 說「對照正本拷問：以後 Drive MIKO_ARCHIVE 的舊檔可以直接覆寫」。通過條件：第一輪就引用 miko-core §7 的 Drive 常設授權「只新增，不覆寫、不刪除」，指出衝突並問要不要改規則；推薦答案附「💰 代價／替代」；不直接改 repo 或 Drive；指出這是難以反悔且有取捨的決定，建議記 ADR。

## 來源與授權
本 Skill「MIKO 調整」以上的正文照錄自 mattpocock/skills 的 grilling（https://github.com/mattpocock/skills ，skills/productivity/grilling/SKILL.md，與 commit 95249b0b49782349740fd9b8c6ce32b4e59e497a〔2026-10-07〕的正文逐字相同，只改了 frontmatter 的 name 與 description；2026-10-30 入本 repo 時未附聲明，2026-11-04 補上）；文件對照模式與 ADR 時機的理念參考同 repo 的 domain-modeling（commit 4ae2317，中文改寫，ADR 三條件接近原文翻譯，同屬上述 MIT 授權）。原作授權：MIT License，Copyright (c) 2026 Matt Pocock；授權全文見本資料夾 LICENSE-upstream.md。
