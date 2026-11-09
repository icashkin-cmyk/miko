# miko repo 工作須知（給在本 repo 工作的 Claude Code）

本 repo 是 MIKO 的 AI 規則正本（公開 repo）。README.md 是正本，skills/miko-core/SKILL.md 開頭的「對應正本」用來核對是否同步（skills/README.md）；本檔只摘錄在 repo 裡動手時要先知道的條文，不新增規則，與正本或 Skill 正文衝突時以正文為準。

## 開工
- 先讀 skills/miko-core/SKILL.md，再讀 VERSION（第 1 行正本版本、第 4 行 README 的 SHA-256），對齊行照抄實際讀到的版本（miko-core §1；check_repo C10）。
- git 操作前一律 git pull（治理專案指示；skills/make-skill S9）。

## 改動規則
- Skill 改版用局部修改，不整份重寫；舊條文保留、改寫或寫進「## 刪除清單」附理由（ADR-036；tests/check_repo.py C11 要求子句保留 ≥ 90%）。
- 每個 Skill 只有一個 writer；其他專案改 Skill 或規則先整理成提案交總召（治理專案指示「單一 writer」表）。
- 公開 repo 不放工程名稱、單位名稱、人名、個人資料，xlsx／csv 內容也算（治理專案指示；check_repo C12）。
- 一律繁體中文；API、函式、變數、Key、介面名稱與狀態識別碼保留原文（README §7；skills/multi-agent-coordination-engine；帳號偏好〔檔案與語言〕）。

## 正本改版要動的地方
README 標題版本、VERSION 四行（第 4 行是 README 的 SHA-256）、CHANGELOG.md 新增一行（只新增）、adapters/README.md 版本、skills/miko-core/SKILL.md 的「對應正本」；並在 Drive MIKO_ARCHIVE 存一份 DELTA（治理專案指示「正本改版」；check_repo C1、C10 檢查版本一致與 SHA-256）。

## 推送前後
- 推送前執行 python3 -I -B tests/check_repo.py（C6、C9 用固定樣本跑回測引擎回歸檢查，不算違反回測暫停 PAUSED_BY_USER，照跑；--skip-backtest 只當選項，用了 C6、C9 印 NOT_RUN、不算 PASS；1.2.51 ADR-074 取代 1.2.44 ADR-067 的略過方向，CI 同標準），私密字清單用環境變數 MIKO_PRIVATE_WORDS 帶入，15 項全過才推（1.2.43 起 15 項；C15 只提示不擋；1.2.44～1.2.50 回測暫停期間曾是其餘 13 項全過、C6／C9 NOT_RUN，1.2.51 起恢復 15 項；1.2.53 起加 C16 詞彙定義表檢查共 16 項，ADR-076）；已 commit 後再跑時帶 MIKO_BASE=<底本 commit>，否則 C11 比的是 HEAD、會顯示「無改動」（1.2.53 稽核第一輪）；清單不得寫進 repo、commit 訊息或任何公開檔（治理專案指示「推送前必做」）。會跑到 MIKO 暫停中任務的檢查項怎麼標，依 skills/make-skill S9。
- 規則或 Skill 修改先經獨立稽核，不自審（skills/independent-audit §3 擇一方式）；稽核後再改任何一個字要重新稽核（miko-core ADR-050）。
- 推送後確認 GitHub Actions check_repo 通過，raw 讀回主要檔案比對 SHA-256（治理專案指示，推送後確認；skills/make-skill S10）。

## 硬邊界
下單、交易、Broker、LIVE 一律不做；台指期停止中；金鑰不寫進 repo、雲端或交接檔，在雲端容器時不寫入任何檔案、請 MIKO 填到平台密鑰設定（README §7、miko-core §7）。
