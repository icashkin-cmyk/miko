# miko-core 附檔：跨 Skill 共用規則（SR）

- 1.2.43 修剪站新增（MIKO 2026-11-08 21:19「葉子要審視是不是每個枝重複的 重複就是寫進miko」；總召 11-09 裁決）。
- 收錄條件：兩個以上 Skill 都有、miko-core 原本沒有的規則。只收各處完全相同的共同部分；各 Skill 多出來的差異留在原處。
- 原處不刪：輕量任務不讀 miko-core 正文與附檔（代入卡第 0 項），所以原句保留，句尾標「同 miko-core SR-n」；以後改規則，本檔與各原處同一版一起改。
- 編號 SR-n 不重用；和正文衝突時以正文為準。

| ID | 共用規則（共同部分） | 出處（a816be1） | 各處差異（留在原處） |
|---|---|---|---|
| SR-1 | 流程表一律 6 欄（ADR-004） | dghp-travel 第 48 行、tw-backtest-workflow 第 86 行、miko-core/references/governance-module.md（原四視角引擎第 252 行） | dghp-travel 與 tw-backtest-workflow 列出六個欄名（步驟／交付物、負責人、前置依賴、驗收條件、證據位置、狀態與下一步），dghp-travel 寫「需要流程表時」並註明取代原件 16 欄 ProcessStep16；四視角引擎限「工程任務的」、沒列欄名，另加「舊 16 欄依承接對照併入；不得藉減欄放寬權限或驗收」 |
| SR-2 | STOP_FOR_GPT_REVIEW 等審查門檻，只能由總召以正式審查紀錄放行 | miko-core/references/governance-module.md（原四視角引擎第 303 行）、tw-backtest-workflow 第 13 行 | 四視角引擎另列 PENDING_GPT_REVIEW；回測寫「不自審解鎖」 |
| SR-3 | 正式審查紀錄逐項標 ACCEPT／REJECT／DEFER，附證據與範圍 | independent-audit 第 36 行、miko-core/references/governance-module.md（原四視角引擎第 303 行） | independent-audit 寫「總召依它寫」 |
| SR-4 | 交給其他 AI 或另一個 Claude 對話的正式交接用 19 欄 FINAL_HANDOFF | dghp-work-handoff 第 49 行、tw-backtest-workflow 第 86 行；miko-core §6 指向 references/governance-module.md（原四視角引擎 §7） | 回測註明「原寫『交給 Codex 時』，ADR-039」 |

- 原處加標記的時間：各 Skill 到自己的升級站時照重複比對表加（tw-backtest-workflow 只出提案）；1.2.43 推送時各原處還沒有「同 miko-core SR-n」標記（政策已寫、標記各站補）。
