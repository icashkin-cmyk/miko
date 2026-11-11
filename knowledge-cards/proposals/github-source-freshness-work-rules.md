# GitHub 正本新鮮度工作守則｜行列式候選

文件狀態：候選提案，尚未正式採用  
適用範圍：`icashkin-cmyk/miko` 的版本、ADR、Skill、規則、治理與正式交接查核  
依據：候選 Skill `knowledge-cards/proposals/github-source-freshness/SKILL.md`  
固定來源版本：開工時動態讀取 GitHub `main/VERSION`，不得寫死

| ID | 類型 | 觸發條件 | 必做操作 | 禁止事項 | 完成證據 | 失敗處理 |
|---|---|---|---|---|---|---|
| GF-01 | 開工 | 版本、ADR、Skill、規則、治理、放行、正式交接 | 先讀 GitHub Contents API `contents/VERSION?ref=main`，headers 帶 `Cache-Control: no-cache, no-store, max-age=0, must-revalidate`、`Pragma: no-cache`、`Expires: 0`、`X-GitHub-Api-Version: 2022-11-28`、`User-Agent` | 不可先讀 raw main 後直接當最新正本 | API path、blob SHA、size、base64 content、台北讀取時間 | API 讀不到標 `NOT_READ`，停相依步驟 |
| GF-02 | 版本 | GF-01 成功 | 讀 `commits?path=VERSION&per_page=5`，記錄第一筆完整 commit、短碼、時間與訊息（版本變更證據）；再讀 `commits?sha=main&per_page=1` 取 main 目前 HEAD 完整 commit 作為固定 commit | 不用記憶、附件、舊對話或舊回應補 commit | API commit JSON | 無法取得標 `UNKNOWN`，不做正式放行 |
| GF-03 | 固定內容 | 已取得 main HEAD 固定 commit | 用同一個 main HEAD 完整 commit（不是 VERSION 最新修改 commit，後者可能落後 main）讀 VERSION、CHANGELOG、README、Skill、references；raw 帶零快取 headers，支援時加 `?cachebust=YYYYMMDDHHMMSS` | 同一輪混用 `main/path` 與固定 commit path；固定內容失敗時退回 main raw | 每檔 URL、commit、bytes、SHA-256 | 固定檔案讀不到標 `NOT_READ` |
| GF-04 | SHA 驗證 | VERSION 有第 4 行 README SHA-256 | 比對 API VERSION、固定 commit VERSION，並比對 README 實際 SHA-256 | 不把 README SHA 當 Git commit | 三方比對結果 | 不同標 `CONFLICT`，停止治理與寫入 |
| GF-05 | 過期判定 | main raw 與 API／固定 commit 不同 | 把舊 raw 標 `STALE`，只保留為過期證據，以 API＋固定 commit 為準 | 不以舊快取覆蓋新正本 | 差異、來源 URL、讀取時間 | 只停受影響步驟，不宣稱無變化 |
| GF-06 | 對齊行 | 來源核對結果需回報 | 寫版本、commit、讀取時間、領域、Skill、狀態來源；工具不回 commit 寫 `UNKNOWN` | 不補造 commit 或時間 | 完整對齊行 | 讀不到寫 `正本 NOT_READ` 與失敗時間 |
| GF-07 | Manus 邊界 | Manus 建立或上傳候選 | 只在 `knowledge-cards/`、`knowledge-cards/proposals/` 建立分支與 PR | 不改正本、Skill、tests、sync、版本號；不直推 main；不自行審查、放行、合併 | 分支、PR、檔案清單、檢查輸出 | 超出路徑立即停止並回報 |
| GF-08 | Claude 交接 | 候選需要正式整合 | PR 描述列改動、舊版差異、Claude 討論結論、來源版本／commit、測試、未決與回滾；交 Claude 總召審查 | 不把 Manus 候選當正式規則 | PR URL、審查回覆、整合結果 | 缺欄位標 `BLOCKED`，不進正式採用 |
| GF-09 | 寫入後讀回 | PR 合併或任何授權寫入後 | 由指定讀回者重新讀 API／固定 commit，核對檔案內容與 SHA-256 | 不以 push 成功代替讀回驗證 | 讀回 URL、commit、SHA-256、時間 | 讀回不符標 `FAIL` 或 `CONFLICT`，保留原證據 |
| GF-10 | 狀態收尾 | 每輪查核完成 | 列 `PASS`、`FAIL`、`BLOCKED`、`UNKNOWN`、`NOT_READ`、`STALE`、`CONFLICT`，並列下一步與負責人 | 不把部分成功標成完整完成 | 報告或 HANDOFF | 只停相依步驟，保存可逆狀態 |

## PR 內容最低欄位

- 修改哪些檔案。
- 與舊內容的差異。
- Claude API 討論結論與尚未解決的問題。
- 來源 VERSION、ADR、固定 commit、讀取時間。
- API／固定 commit／SHA-256 比對結果。
- 執行的檢查與完整輸出位置。
- 未完成、未知、阻塞與回滾方式。
- 明確聲明：這是候選提案，尚未正式採用。

## 任務四態

**完成但有疑慮**：候選 Skill、驗證腳本與本行列式守則已建立；仍須 Claude 總召審查、PR 審查與正式放行，不能當成已啟用規則。
