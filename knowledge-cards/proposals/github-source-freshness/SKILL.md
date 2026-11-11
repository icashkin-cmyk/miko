---
name: github-source-freshness
description: "GitHub 正本新鮮度、版本、commit 與固定內容驗證。Use for: checking MIKO repository VERSION, ADR, CHANGELOG, README, Skills, rules, governance, releases, PR evidence, or any task where stale raw.githubusercontent.com content could affect a decision."
---

# GitHub 正本新鮮度核對流程

本候選 Skill 尚未正式安裝；目前只放在 `knowledge-cards/proposals/`，等待 Claude 總召審查與正式放行。

## 1. 適用範圍與硬邊界

在讀取版本、ADR、Skill、規則、治理狀態、放行依據、跨平台寫入或正式交接前使用本流程。不要把單一 `raw.githubusercontent.com/<owner>/<repo>/main/<path>` 回應當成最新正本證據。

本 Skill 只驗證來源新鮮度，不授權任何寫入、推送、合併、放行或修改。Manus 目前只能處理 `knowledge-cards/` 與 `knowledge-cards/proposals/`；正本、Skill、tests、sync、版本號的正式修改交 Claude 總召。

## 2. 強制四站流程

### 站 1：API 取得 main metadata

先讀 GitHub Contents API：

```text
https://api.github.com/repos/<owner>/<repo>/contents/VERSION?ref=main
```

HTTP request 必須使用下列 headers：

```http
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2022-11-28
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Pragma: no-cache
Expires: 0
User-Agent: miko-github-source-freshness
```

記錄：`path`、blob `sha`、`size`、base64 `content`、查詢時間（Asia/Taipei）。解碼內容後確認 VERSION 至少有版本、日期、ADR 與 README SHA-256 四行。

### 站 2：API 取得 VERSION 最新修改 commit 與 main 目前 HEAD

再讀兩個：

```text
https://api.github.com/repos/<owner>/<repo>/commits?path=VERSION&per_page=5
https://api.github.com/repos/<owner>/<repo>/commits?sha=main&per_page=1
```

使用相同 API headers。第一個取第一筆的完整 commit SHA、短碼、時間與 commit message，記為「VERSION 最新修改 commit」，只作為版本變更證據。第二個取 main 目前 HEAD 的完整 commit SHA，記為「固定 commit」，站 3 所有檔案都用它讀。不得用記憶、附件、舊對話或先前回應的 commit 代替。

不可把 VERSION 最新修改 commit 當固定 commit：VERSION 之後 main 可能又改了 CHANGELOG、Skill、sync 等其他檔，用較舊的 commit 讀會得到舊內容卻仍然比對通過（實例：2026-11-11 VERSION 最後修改在 4cae500，之後 main 80b082c 又改了 CHANGELOG.md 與 skills/miko-core/SKILL.md，用 4cae500 讀這兩檔的 SHA-256 與 main 不同）。

### 站 3：固定 commit 讀內容

以站 2 的 main HEAD 完整 SHA（固定 commit）建立固定 URL：

```text
https://raw.githubusercontent.com/<owner>/<repo>/<full-commit>/<path>
```

固定 commit 的 raw request 必須使用：

```http
Accept: application/vnd.github.raw+json
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Pragma: no-cache
Expires: 0
User-Agent: miko-github-source-freshness
```

工具支援時，在固定 commit URL 加上不改變檔案路徑的 cache-busting query：

```text
?cachebust=YYYYMMDDHHMMSS
```

禁止同一輪把 `main/<path>` 與 `<full-commit>/<path>` 混用。固定 commit 讀不到時標 `NOT_READ`，不退回未固定的 main raw URL。

### 站 4：強制交叉檢查

至少驗證：

1. API Contents 的 base64 解碼內容。
2. 固定 commit raw 的內容。
3. VERSION 第 4 行宣告的 README SHA-256 與固定 commit README 的實際 SHA-256。

API 與固定 commit 不同時標 `CONFLICT`；main raw 與固定內容或 API 不同時標 `STALE`。未完成四站前，不得標示「已讀取最新正本」、不得治理、不得放行、不得寫入。

## 3. 可重複執行的驗證工具

本候選 Skill 的 `scripts/verify_github_source.py` 是低自由度驗證器。執行：

```bash
python3 scripts/verify_github_source.py \
  --repo icashkin-cmyk/miko \
  --paths VERSION CHANGELOG.md README.md skills/miko-core/SKILL.md
```

工具會：

- 以 API headers 讀 `VERSION` metadata、VERSION commit history 與 main 目前 HEAD。
- 以 main HEAD 固定 commit 和零快取 headers 讀指定檔案；讀完再查一次 main HEAD，若已變動標 `STALE`，需重跑。
- 比對 API VERSION 與固定 commit VERSION。
- 以 SHA-256 比對 VERSION 第 4 行宣告的 README 雜湊。
- 輸出 JSON 證據，包含版本、ADR、commit、讀取時間、每個檔案的狀態與錯誤。
- 任一強制檢查失敗時以非零結束碼結束，不得把部分成功當 PASS。

若工具環境不能連線或不能設定必要 headers，標 `BLOCKED`，改用 GitHub API 與固定 commit；無替代來源時只停相依步驟。

## 4. 對齊行

成功取得 API commit 時：

```text
已對齊：miko-core vX｜正本 vY（commit abc1234｜讀取時間 YYYY-MM-DD HH:MM 台北）｜領域：名稱｜Skill：名稱與版本或無｜狀態來源：GitHub <owner>/<repo> main（YYYY-MM-DD）
```

工具只有檔案內容而沒有 commit 時，寫 `commit UNKNOWN`；不可補造。來源讀不到時寫 `正本 NOT_READ` 與實際失敗時間。

VERSION 第 4 行是 README SHA-256，不是 Git commit；兩者必須分開記錄。

## 5. 失敗分類與處置

| 狀態 | 觸發 | 處置 |
|---|---|---|
| `NOT_READ` | API、固定 commit 或必要檔案讀不到 | 停止相依步驟；不把未讀內容當已驗證 |
| `UNKNOWN` | 工具未回 commit、讀取時間或完整證據不足 | 保留未知欄位；不補造、不標 PASS |
| `STALE` | main raw 或快取內容落後固定 commit | 保留為過期證據；以固定 commit 為準 |
| `CONFLICT` | API、固定 commit 或 SHA-256 不一致 | 停止治理與寫入，列出差異交 Claude 總召與 MIKO |
| `BLOCKED` | 沒有網路、授權或零快取控制不可用 | 標出缺口與負責人；只停相依步驟 |
| `FAIL` | 已完成檢查但比對未通過 | 保留原始證據；修正後重新跑完整四站 |

## 6. 完成判準

只有以下全部成立才可標示來源核對完成：

- API Contents 成功取得 VERSION metadata 與內容。
- VERSION 最新修改 commit 與 main 目前 HEAD 已由 API 實際取得。
- 同一個 main HEAD 固定 commit 已讀取所有本輪必要檔案，且讀完後 main HEAD 未變動。
- 必要 raw requests 帶有零快取 headers；可用時含 cache-busting。
- API、固定 commit 內容與 README SHA-256 比對通過。
- 證據含版本、ADR、commit、讀取時間、來源 URL、SHA-256 與狀態。
- 沒有 `NOT_READ`、`CONFLICT`、`STALE` 或未處理的 `UNKNOWN`。
- 正本相依後續操作依治理與授權規則完成；本 Skill 本身不授權寫入。

## 7. 禁止事項

- 不得只讀 raw main URL 就宣稱最新。
- 不得把 cache-busting 當成固定 commit。
- 不得把 VERSION 第 4 行 README SHA-256 當成 Git commit。
- 不得把舊快取內容覆蓋新正本判定。
- 不得因 API 失敗而繞回未固定的 main raw。
- 不得在來源 `CONFLICT` 時自行選邊。
- 不得因來源驗證通過而宣稱取得寫入或放行權限。
