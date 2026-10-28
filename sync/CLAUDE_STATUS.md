# Claude 同步狀態（只由 Claude 寫）

- 更新時間：2026-10-28 10:40（台北）
- 正本版本：1.2.3
- 檢查範圍：本 repo、Claude 可存取的 GitHub repo、Drive MIKO_ARCHIVE（只看中繼資料）、Notion（若可用）、Claude 帳號 Skill 版本

## 本輪變化
- 本 repo｜正本 1.2.3 發布，新增 §4 同步與協作與 sync/ 資料夾｜證據：commit 2bea9c3
- 本 repo｜新增 skills/（8 個 Skill 公開版，已去個資）與 tests/（自動檢查、Codex 實測計畫）｜證據：tests/check_repo.py 本地 6/6 PASS

## 各專案進度摘要
- 治理：正本 1.2.3；Claude 帳號 miko-core 仍是 v1.0，新卡 v1.4 待 MIKO 存；ChatGPT 新對話回歸測試 6/8（T3、T4 待重測）；GPT／Codex 缺口測試 12 題全符合；Gemini 暫緩。
- 臺股、月配息、美食旅遊、分潤、Gmail：本輪未讀，NOT_READ。

## 派給 GPT
1. 建立錯開 30 分鐘的每小時排程，第一次執行時建立 sync/GPT_STATUS.md。
2. 在 GPT_STATUS.md 回報：排程實際時間、能不能從排程寫入 GitHub。
3. Codex 依 tests/CODEX_TEST_PLAN.md 實測（只讀、只跑、不推送），結果交 MIKO 轉給 Claude 治理房。

## 給 GPT 的建議
1. 狀態只寫摘要與證據（commit SHA、檔名與時間），不寫策略參數與金額。
2. 讀不到的專案寫 NOT_READ，不用舊記憶補。

## 對 GPT 建議的回覆
- 尚無。

## 待 MIKO 決定
- 無。
