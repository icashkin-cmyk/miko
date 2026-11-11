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

## 擋下條件
- 找不到 `tests/check_repo.py`。
- `MIKO_PRIVATE_WORDS` 為空。
- check_repo 結束碼非 0。
- 輸出含 FAIL 或 NOT_RUN 行。
- 輸出缺「合計」行。

## 限制
- 緊急才用 `git push --no-verify`，用了要在回報中寫明。
- 已 commit 後再跑要帶 `MIKO_BASE=<底本 commit>`（CLAUDE.md 推送前後）。
- 本機 hook 可被略過，不是權威；權威是 CI 與稽核。

## 實跑狀態
- 11-10 在沙盒 6 情境實跑如預期；11-12 在 main 7cb5cd3 重跑，其中情境 A、C 只在舊版 clone（1.2.24）驗過，【未在 7cb5cd3 重驗】。
- 從未裝到真實 repo。

## 搬入條件
搬入 repo 的 githooks／ 屬新增檔，需獨立稽核與 MIKO 當次批准。
