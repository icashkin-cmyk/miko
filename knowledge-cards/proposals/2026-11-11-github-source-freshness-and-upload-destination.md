# GitHub 正本讀取新鮮度與提案上傳位置規則提案

文件狀態：Manus 候選提案，尚未正式採用  
提案日期：2026-11-11（Asia/Taipei）  
提案來源：本次 `raw.githubusercontent.com` 舊快取誤讀事件  
適用 repo：`icashkin-cmyk/miko`  
預定放置位置：`knowledge-cards/proposals/`  
責任狀態：Manus 建立提案；Claude 總召審查與整合；MIKO 決定正式採用與放行

## 一、問題

同一個 `raw.githubusercontent.com` URL 可能被讀取工具或 CDN 回傳舊內容。本次固定 URL：

```text
https://raw.githubusercontent.com/icashkin-cmyk/miko/main/VERSION
```

曾回傳 `1.2.49 / ADR-072`，但 GitHub `main` 實際已更新為 `1.2.68 / ADR-091`。若直接把 raw 回應當成最新正本，會造成版本、Skill、模型分級與治理規則全部依錯誤基準執行。

## 二、正式名稱

**正本新鮮度核對流程（GitHub 正本版本的 API 查詢、commit 固定、零快取讀取與交叉驗證流程）**【流程】

定義：任何涉及正本版本、ADR、Skill、規則、治理、放行、跨平台寫入或正式交接的任務，必須先用 GitHub API 取得 `main` 的最新版本 metadata，再取得 VERSION 最新修改 commit，接著固定該 commit 讀取相關檔案；raw URL 只能作為固定 commit 的內容讀取來源，不能單獨作為最新版本證據。

## 三、強制執行順序

### 1. 先讀 GitHub API Contents

先讀：

```text
https://api.github.com/repos/icashkin-cmyk/miko/contents/VERSION?ref=main
```

必須取得並記錄：

- `path`
- `sha`
- `size`
- `content`
- 查詢時間（台北）

若 API 回應沒有內容、解析失敗或不是檔案，標 `NOT_READ`，停止所有依賴正本版本的步驟。

### 2. 再讀 VERSION 的 commit 歷史

再讀：

```text
https://api.github.com/repos/icashkin-cmyk/miko/commits?path=VERSION&per_page=5
```

從第一筆實際回傳資料取得：

- 最新修改 commit 完整 SHA
- commit 短碼
- commit 日期
- commit message
- 是否包含版本號與 ADR

不得使用記憶、附件、舊對話或快取中的 commit 取代 API 實際回傳值。

### 3. 固定 commit 讀取正本內容

取得最新 commit 後，所有同一輪核對的 VERSION、CHANGELOG、README、Skill 與 references，必須改用固定 commit URL：

```text
https://raw.githubusercontent.com/icashkin-cmyk/miko/<固定commit>/<檔案路徑>
```

不要在同一輪混用 `main/<檔案>` 與固定 commit 的檔案。若固定 commit 的檔案讀不到，標 `NOT_READ`，不改回使用未固定的 `main` raw URL 繞過問題。

### 4. raw URL 必須禁用快取

使用 raw URL 時，工具呼叫必須設定：

```text
max_age_seconds=0
```

若工具支援 URL cache-busting，再加入不影響路徑的查詢參數，例如：

```text
?cachebust=YYYYMMDDHHMM
```

但 cache-busting 不能取代固定 commit，也不能取代 GitHub API。只有「API metadata＋最新 commit＋固定 commit 內容」全部相符，才可判定讀取完成。

### 5. 交叉驗證

至少比對以下三項：

1. GitHub API Contents 的 `content` 解碼結果。
2. 固定 commit raw URL 的檔案內容。
3. VERSION 第 4 行宣告的 README SHA-256，與固定 commit 讀到的 README 實際 SHA-256。

三者不一致時標 `CONFLICT`，列出三份內容、來源 URL、讀取時間與 SHA-256；不得自行選一份繼續治理或寫入。

## 四、對齊行固定格式

來源讀取成功且工具回傳 commit 時：

```text
已對齊：miko-core vX｜正本 vY（commit abc1234｜讀取時間 YYYY-MM-DD HH:MM 台北）｜領域：名稱｜Skill：名稱與版本或無｜狀態來源：GitHub icashkin-cmyk/miko main（YYYY-MM-DD）
```

工具只回檔案內容、沒有回 commit 時：

```text
已對齊：miko-core vX｜正本 vY（commit UNKNOWN｜讀取時間 YYYY-MM-DD HH:MM 台北）｜領域：名稱｜Skill：名稱與版本或無｜狀態來源：GitHub raw 固定 commit（YYYY-MM-DD）
```

讀取失敗時：

```text
已對齊：miko-core vX｜正本 NOT_READ（讀取失敗時間 YYYY-MM-DD HH:MM 台北）｜領域：名稱｜Skill：名稱與版本或無｜狀態來源：GitHub NOT_READ
```

不得把 VERSION 第 4 行的 README SHA-256 當成 Git commit。兩者是不同欄位，必須分開記錄。

## 五、失敗處理

| 失敗情況 | 判定 | 動作 |
|---|---|---|
| API Contents 無法讀取 | `NOT_READ` | 停止依賴正本版本的步驟；不得只改用舊 raw 快取 |
| commit 歷史無法讀取 | `UNKNOWN` | 可保存已讀到的 VERSION，但不得宣稱 commit 已核實；固定 commit 由其他可靠證據提供前不做正式放行 |
| 固定 commit 檔案不存在 | `NOT_READ` | 停止該檔案相依步驟，列出檔案路徑與錯誤 |
| API 與固定 commit 內容不同 | `CONFLICT` | 停止治理與寫入，列出差異，交 Claude 總召與 MIKO 裁決 |
| raw main 與 API 版本不同 | `STALE` | 以 API 與固定 commit 為準；保留舊 raw 結果為過期證據，不得作決策依據 |
| 工具允許快取但未能設定零快取 | `BLOCKED` | 改用 GitHub API 與固定 commit；若無替代來源，停止正本相依步驟 |

## 六、提案建立與上傳位置

本規則提案本身只能放在：

```text
repo: icashkin-cmyk/miko
path: knowledge-cards/proposals/
```

建議流程：

1. Manus 在本地建立提案檔。
2. Manus 開新分支，不直推 `main`。
3. 分支只修改 `knowledge-cards/` 或 `knowledge-cards/proposals/`。
4. 執行可用的 `check_repo` 或該路徑允許的檢查，保留輸出。
5. 開 Pull Request。
6. PR 描述列出：修改檔案、舊版差異、Claude API 討論結論、版本／commit、測試結果、未決事項與回滾方式。
7. Claude 總召負責審查與整合；Manus 不自行審查、放行、合併或修改正本。
8. 只有 MIKO 或依正本授權規則完成正式放行後，才可把本提案內容整合到帳號偏好、專案指令、Skill 或正本流程。

## 七、責任分工

| 工作 | Manus | Claude 總召 | MIKO |
|---|---|---|---|
| 建立本提案 | 負責 | 可提供意見 | 知會 |
| 核對 GitHub API／commit／固定內容 | 可執行並保存證據 | 複核 | 必要時裁決 |
| 修改 `knowledge-cards/` | 可在分支＋PR執行 | 審查 | 合併或授權 |
| 修改正本、Skill、tests、sync、版本號 | 不可 | 負責 | 正式授權／裁決 |
| 獨立稽核與正式放行 | 不可自行完成 | 依正本流程執行 | 最終採用裁決 |

## 八、驗收條件

本提案只有在以下條件全部成立時，才可標示「可交 Claude 總召整合」：

- [ ] 已實際讀到 GitHub API Contents `VERSION`。
- [ ] 已實際取得 VERSION 最新修改 commit。
- [ ] 已使用同一固定 commit 讀取 VERSION、CHANGELOG、README、miko-core 與必要 references。
- [ ] raw URL 若使用，已設定 `max_age_seconds=0` 或等效零快取控制。
- [ ] API 內容、固定 commit raw 內容與 SHA-256 已比對。
- [ ] 對齊行含版本、commit、讀取時間與狀態來源。
- [ ] 失敗時依 `NOT_READ`、`UNKNOWN`、`STALE`、`CONFLICT`、`BLOCKED` 分類。
- [ ] 提案只放在 `knowledge-cards/proposals/`，沒有修改其他路徑。
- [ ] 已保留 Claude API 討論與交叉比對結果。
- [ ] 未宣稱正式採用、正式放行或已修改正本。

## 九、目前狀態

本文件是 Manus 候選提案。尚未建立 GitHub 分支、尚未開 PR、尚未交 Claude 總召正式整合，也尚未修改正本或專案指令。

任務四態：**完成但有疑慮**。提案文字已建立；GitHub 寫入、PR、Claude 總召正式審查與 MIKO 採用裁決尚未完成。
