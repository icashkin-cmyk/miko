未驗收提案（ADR-092；提案者：GitHub 專責串；來源：Manus 開發工作流手冊的 Git hooks 想法，改為跑本 repo 的 tests/check_repo.py）

# pre-push hook：本機第一道防線

## 用途
推送前在本機先跑 `python3 -I -B tests/check_repo.py`，沒過就擋下；CI 仍是第二道，不取代。

## 檔案
- `pre-push`：hook 本體。
- `install_hooks.sh`：安裝到 `.git/hooks/`，不改 `core.hooksPath`。

## 安裝（由 MIKO 在 Mac 親手執行；雲端不安裝）
```bash
cd ~/miko
bash knowledge-cards/proposals/workflow/20261112_githooks-pre-push/install_hooks.sh ~/miko
```
私密字清單只用環境變數 `MIKO_PRIVATE_WORDS` 帶入，不寫進 repo、commit 訊息或任何公開檔。

## 檢查規則
- 純刪除分支的推送：沒有內容要檢查，直接放行（不要求清單）。
- 要推送的 ref 必須等於目前 HEAD（一次只推一個分支），工作樹必須乾淨（沒有未提交或未追蹤檔案）；否則擋。原因：check_repo 掃的是工作樹，不是被推送的 ref。
- 找不到 `tests/check_repo.py` 擋。
- `MIKO_PRIVATE_WORDS` 為空擋。
- check_repo 結束碼非 0 擋。
- 輸出含行首 FAIL 或 NOT_RUN 擋（結束碼 0 不能單獨算通過；比對不經管線，避免 SIGPIPE 放行）。
- 輸出缺「合計」行擋。
- 底本 `MIKO_BASE`（C11 用）：遠端已有的 commit；新分支退回與 origin/main 的共同祖先，再退回 HEAD~1，最後用 HEAD，不傳空字串。

## 限制
- 緊急才用 `git push --no-verify`，用了要在回報中寫明。
- 已 commit 後再跑要帶 `MIKO_BASE=<底本 commit>`（CLAUDE.md 推送前後）。
- 本機 hook 可被略過，不是權威；權威是 CI 與稽核。
- 裝在主 repo 的 `.git/hooks`，同一個 repo 的所有 worktree 共用；有設 `core.hooksPath` 時安裝腳本拒絕覆蓋。
- install_hooks.sh 對不是 git repo 的路徑會失敗退出，不寫任何檔案。
- 安裝腳本在該分支存在（checkout）或這份提案合併進 repo 之後才有這個路徑。

## 實跑狀態（2026-11-12，沙盒本機 bare 遠端，不是 MIKO 的 Mac；check_repo 用假檔控制輸出）
| 情境 | 結果 |
|---|---|
| 一般推送、單一 commit、新分支多 commit（底本有值） | 通過 |
| 輸出第一行 FAIL 後接兩萬行（SIGPIPE 情境） | 擋下 |
| 工作樹有未追蹤檔 | 擋下 |
| 同時推 main 與另一分支（HEAD 只對應其一） | 擋下 |
| 推送的 ref 不是 HEAD | 擋下 |
| 刪除分支（含沒帶清單） | 放行 |
| 清單空、缺合計、結束碼 1、NOT_RUN 行 | 擋下（改版後重測） |
| install_hooks.sh：非 git repo | 失敗退出，不寫檔 |
| install_hooks.sh：空 repo、重裝備份 | 安裝成功、備份舊檔 |
未實跑：MIKO 的 Mac、真實 check_repo 在 hook 內的完整一輪（只跑過假檔與本機直接執行）、子模組。真實 repo 從未安裝。

## 搬入條件
這份提案放在 knowledge-cards/proposals/workflow/；要搬成 repo 正式的 githooks 目錄屬新增檔，需獨立稽核與 MIKO 當次批准。
