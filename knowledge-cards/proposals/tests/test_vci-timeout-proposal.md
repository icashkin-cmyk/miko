# `test_vci.py` 子程序逾時修復提案

## 文件狀態

- 狀態：候選提案，未正式啟用。
- 正本基準：1.2.69（ADR-092）。
- 基準分支：`adr092`，commit `8773e7715b8e67d86eca38f1b1e1f5ec1d6fbaf2`。
- 提案類型：`tests`。
- 完整替換稿：本目錄的 [`test_vci.py`](./test_vci.py)。
- 正式取代目標：`skills/visual-content-intelligence/scripts/test_vci.py`。
- 正式搬入與啟用：尚未執行，須經 Claude 總召審查，並由 MIKO 逐件、當次明確批准。

## 發現

來源檔共有 14 個 `subprocess.run` 呼叫，原本都沒有 timeout。呼叫涵蓋 Python 子測試、ffmpeg 測資生成、ffprobe 缺失測試，以及 FLV／WMV 等媒體測試。CI 因此可能在子程序無回應時長時間停在 visual-content-intelligence 與 read_ledger 步驟。

## 修復內容

完整替換稿新增統一的 `_run_process()` wrapper：

- Python 子程序預設上限：60 秒。
- ffmpeg／ffprobe 子程序預設上限：120 秒。
- 保留呼叫端明確傳入的 timeout，不覆蓋既有設定。
- 逾時時拋出 `CommandTimeoutError`，由 unittest 記為 ERROR，讓 CI 失敗並顯示明確逾時原因，不把逾時誤判為 PASS 或 NOT_RUN。
- 新增 `test_subprocess_timeout_is_enforced`，確認 timeout 實際生效。
- 不改變原有結束碼語意：全部 PASS 為 0、沒有 FAIL 但有 NOT_RUN 為 5、有 FAIL 或 ERROR 為 1。

## 驗證

在暫時工作樹中，以完整替換稿取代正式目標檔後執行：

```text
python3 -I -B -W ignore skills/visual-content-intelligence/scripts/test_vci.py
```

結果：

```text
Ran 78 tests in 14.662s
OK
PASS 78／NOT_RUN 0／FAIL 0（共 78 題）
exit=0
```

另外完成：

- Python compile：PASS。
- AST 盤點：正式替換稿只保留 wrapper 內一個 `subprocess.run` 呼叫；timeout 由 `kwargs.setdefault('timeout', ...)` 強制注入。
- `git diff --check`：PASS。
- 正式路徑未修改：PASS。

## 邊界

這份提案只處理 `test_vci.py` 內的子程序逾時。它不修改 GitHub Actions workflow，也不修改 `vci_media.py`、`read_ledger.py` 或正式 Skill 路徑。正式搬入前仍應由總召確認 timeout 秒數、CI runner 資源與測試穩定性，並在正式路徑搬入後重新執行完整 CI。
