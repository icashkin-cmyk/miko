# 未驗收提案

## 批次 0／1 提案包

本目錄是 Manus 提出的候選規則與候選實作資產，不是正式 Skill、不是 miko-core 正本，也不會自動被 Runtime 載入。

### 檔案

- `20261112_batch-0-1-proposal.md`：完整提案、範圍、封鎖摘要、驗收與責任邊界。
- `batch-0-risk-blocks.json`：批次 0 fail-closed 路由設定候選。
- `batch-1-operation-contract.schema.json`：批次 1 共用 Operation Contract JSON Schema。
- `batch-1-state-machine.md`：狀態、任務四態、狀態轉移、不變量與失敗出口。
- `validate_batch_0_1.py`：純唯讀結構驗證器，不連網、不寫入、不修改正式檔案。

### 執行方式

```sh
python3 -I -B knowledge-cards/proposals/rules/20261112_batch-0-1-risk-block-and-shared-contract/validate_batch_0_1.py
```

這個命令只驗證提案資產的 JSON 結構與 fail-closed 不變量，不驗證正式路由，也不代表已接入 Runtime。

### 正式採用前不可做的事

- 不把 JSON 直接複製到 `skills/`、`tests/`、`VERSION`、`sync/` 或 `.github/`。
- 不以此提案解除 `PAUSED_BY_USER`、`BLOCKED` 或其他正本停止。
- 不以 `PASS` 宣稱任何 Skill 已採用、已部署、已載入或已生效。
- 不執行 Gmail、Drive、Git push、付款、預訂、刪除、對外發送或其他外部寫入。
- 不以本提案取代 independent audit、Claude 治理總召審查或 MIKO 逐件批准。

### 後續責任

Manus 只建立本提案包。Claude 治理總召負責審查、決定是否搬入正式路徑、安排 independent audit 與版本治理；MIKO 負責正式採用、路由恢復與任何外部寫入批准。
