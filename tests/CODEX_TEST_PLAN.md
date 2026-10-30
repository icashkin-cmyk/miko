# Codex 實測計畫（MIKO 正本 1.2.3）

目的：由 Codex（不同模型、可以執行程式）獨立實測 MIKO 正本與 Skill 公開版。這是稽核，不是改版：只讀、只跑、只回報。

## 規則
- 不要推送、不要開 PR、不要改任何檔案；不發文、不發訊息（正本 §4 派工預設）。結果直接回覆給 MIKO，由 MIKO 原文轉給 Claude 治理房。
- 每一步寫出實際執行的命令與輸出；沒跑就寫「未執行」，不推測結果。
- 台指期維持停止；不下單、不交易。

## 步驟
1. 取得 repo：`git clone https://github.com/icashkin-cmyk/miko.git`（或 `git -C ~/miko pull --ff-only`），回報 `git log --oneline -1`。
2. 自動檢查：在 repo 根目錄執行 `python3 tests/check_repo.py`，貼出完整輸出。通過條件：8/8 PASS。
3. 回測引擎重算：進 `skills/tw-backtest-workflow/scripts/`，執行 `python3 bt_min.py 2330_202501_202505.csv`，另外用你自己寫的獨立程式手算第一筆訊號日期、成交價與股數，和 bt_min 的結果比對（Skill 驗收 AC-S6）。
4. 規則體檢：讀 README.md 與 skills/*/SKILL.md，依四類（條件不完整／規則模糊／規則互相衝突／步驟容易被跳過）列問題，每條附檔名與行號；找不到就寫「未發現」與你檢查了什麼。
5. 回歸測試：依 README §8，T1～T14 每題用一到兩句回答，並自己標 PASS／FAIL／UNKNOWN。

## 回報格式
- commit：
- 步驟 2：check_repo 輸出原文
- 步驟 3：bt_min 輸出摘要＋獨立手算結果＋是否一致
- 步驟 4：問題清單（類別｜檔名:行號｜說明）
- 步驟 5：T1～T14 答案與自評
- 未執行或失敗的步驟與原因
