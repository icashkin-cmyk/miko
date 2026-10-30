---
name: "grilling"
description: "逐輪拷問計畫或決策直到雙方理解一致。使用者說 grill、「拷問我」「壓力測試這個方案」「逐題問到清楚」時使用；一般問答不使用。"
---

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
- 只在 MIKO 明確啟動時用（說 grill、拷問、壓力測試、逐題問到清楚），一般問答與小問題不用。
- 每題的推薦答案要附代價與一個替代做法。MIKO 回「是」只代表接受那一題的推薦答案，不代表授權任何外部操作或整包同意。
- 已經決定的事不重問；低風險細節直接採合理假設並註明，不為追問而追問。
- 查事實自己用工具查；只有大量、可平行的查找才開子代理（miko-core §4 多代理規則），不為每個小問題派子代理。
- 還有未決的相依決策時不動手實作；不依賴它的唯讀研究可以繼續。
- 一輪最多 5 題；可問的超過 5 題時，先問最影響結果的，其餘延到下一輪。MIKO 說「夠了」，或剩下的問題都不影響結果，就結束並整理共識。
- 每題格式在 ➡️ 推薦答案下面多一行「💰 代價／替代：……」。
