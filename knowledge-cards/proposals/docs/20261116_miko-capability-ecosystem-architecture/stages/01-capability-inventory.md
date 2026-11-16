未驗收提案

# Stage 1｜Capability Inventory 全域能力目錄

- 目的：回答「目前到底擁有什麼」，並分離 installed、callable、executable、verified、adopted、runtime_read_back。
- 輸入：G0 清單、所有 Skill、工具、MCP、API、Browser、Runtime、帳號連線狀態。
- 輸出：Capability Inventory、依賴圖、能力重複報告、未驗證清單。
- 前置條件：G0 PASS；每筆來源可追溯。
- 操作要求：逐筆記錄版本、用途、觸發、I/O、權限、限制、最後驗證與證據。
- 禁止事項：不得以檔案存在冒充可呼叫；不得以登入畫面冒充授權；不得以文件描述冒充執行證據。
- 檢查點：能力狀態是否分欄；依賴是否可解析；重複能力是否標出。
- Acceptance Criteria：每個納入項目都有 inventory record；未知欄位標 UNKNOWN；狀態不可混寫。
- Failure Handling：來源讀不到標 NOT_READ；權限不足標 BLOCKED；只停受影響項目。
- Recovery：補讀來源或重新授權後重建增量 inventory，保留舊版。
- Regression Test：將 verified 改成 installed、移除 dependency、製造同名不同版，均應被捕捉。
- 閉環條件：Inventory、差異、狀態與證據相互一致，G1 PASS。
- 負責角色：IMPLEMENTER／TESTER／INDEPENDENT_AUDITOR。
- 證據與保存：`schemas/capability-inventory.schema.md` 與 `evidence/stage-01/`。
