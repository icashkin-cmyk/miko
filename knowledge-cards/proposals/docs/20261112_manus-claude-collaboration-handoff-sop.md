# Manus 與 Claude 協作分工及交接 SOP

## 文件狀態

- 狀態：`PROPOSED`，尚未正式採用。
- 適用範圍：本專案的研究、程式、Skill、文件、治理、PR、驗收與交接。
- 最終授權者：MIKO。
- 正本：開工時動態讀取 GitHub `main/VERSION` 與固定 main HEAD；不得用記憶或舊摘要代替。

## 1. 角色分工

| 角色 | 主要責任 | 不得自行做的事 |
|---|---|---|
| Manus 執行總召 | 接收需求、開工對齊、拆解、執行、建立候選、保存證據、測試、整合、交接 | 不得把候選當正本、把工具 ACK 當成果、解除停止、接 Runtime、合併或執行不可逆操作 |
| Claude 治理總召 | 審查正本、版本、邊界、授權、責任、採用條件與衝突 | 不得把自我審查當獨立稽核，不得代替 MIKO 解除停止或作保留決定 |
| 獨立稽核者 | 驗證未參與修改者的證據、測試、讀回與完整性 | 不得由修改者自我兼任 |
| MIKO | 最終授權、正式放行、停止解除、不可逆決定與衝突裁決 | — |

Gemini 或其他模型只能提供建議；其輸出須標示為模型建議，不是正本、稽核或放行證據。

## 2. 共同不變量

1. Manus 與 Claude 使用同一固定來源、版本、commit、讀取時間與範圍。
2. `PROPOSED`、`REVIEWED`、`ADOPTED`、`RUNTIME_ENABLED`、`WRITTEN` 是不同狀態，不得合併成「完成」。
3. 所有重要主張必須有來源或標籤：`VERIFIED_FROM_READ`、`VERIFIED_FROM_COMMAND`、`VERIFIED_FROM_CI`、`NOT_READ`、`NOT_RUN`、`UNKNOWN`、`BLOCKED`、`CONFLICT`。
4. 未取得授權時，停止外部寫入、刪除、分享、權限變更、費用、Runtime 與不可逆操作。
5. 交易、Broker、LIVE、台指期停止狀態與回測暫停狀態依既有硬邊界處理，不得改名或繞過。

## 3. 標準流程

### 3.1 Manus 開工

1. 讀 miko-core、VERSION、適用 Skill、專案指示與既有 Task。
2. 固定來源 commit，記錄版本、ADR、讀取時間、範圍與 Writer／Owner。
3. 寫出目標、非目標、授權、依賴、驗收條件與失敗出口。
4. 只在授權範圍執行；候選內容優先寫入 `knowledge-cards/proposals/`。
5. 保存命令、完整輸出、錯誤、測試、差異與 SHA-256。

### 3.2 Manus 交 Claude

交接包必須包含：

- 任務目標、非目標與授權。
- 固定來源：repo、commit、VERSION、ADR、URL、讀取時間。
- 修改檔案、前後差異、候選狀態與 SHA-256。
- 已執行與未執行的命令、測試、CI、讀回與限制。
- Writer、Owner、獨立稽核者、回滾方式與阻塞條件。
- 明確列出要求 Claude 裁決的問題。

### 3.3 Claude 審查

Claude 依序檢查：

1. 來源是否固定且新鮮。
2. 版本、取代鏈、Scope、責任與 Writer 是否一致。
3. 是否越過硬禁止、停止狀態、授權或外部寫入邊界。
4. 候選是否把計畫、模型建議、局部 PASS 或自我檢查寫成事實。
5. 測試、讀回、SHA、回滾與失敗出口是否足夠。

Claude 必須分開回答：

- `UPLOAD_FOR_REVIEW`：是否可送治理審閱。
- `ADOPT`：是否達正式採用門檻。
- `RUNTIME`：是否可接線啟用。

每項只可為 `YES`、`NO` 或 `UNKNOWN`，並列必修、阻塞、已確認與未確認事項。`UPLOAD_FOR_REVIEW=YES` 不等於 `ADOPT=YES`。

### 3.3.1 Claude API 複核門檻

以下任一情況，Manus 必須呼叫 Claude API，並把結果交給 Claude 治理總召複核：首次送治理審閱；角色、授權、狀態軸、裁決用語、停止狀態或 ADR 改義；材料 SHA-256 變更；或 Manus／Claude 發生衝突。純錯字、標點、格式且不改變規則、責任、狀態、數字、日期或引用的小錯，可延至下一次 API 複核，但須留 diff。

每次必須保存：`request_id`、完整 request payload、完整 response、實際 `model`、Asia/Taipei 請求／回應時間、每份材料 SHA-256、固定來源 commit／VERSION／ADR、`api_status`、`stop_reason`、token、request／response SHA-256 與讀回位置。API 失敗、逾時、截斷或空回應標 `UNKNOWN`，開困難卡；不得以 ACK、HTTP 200、請求送出或其他模型建議代替審查。

Claude API 複核不是獨立稽核，也不授權採用、Runtime、合併或解除停止；完整結果須交 Claude 治理總召複核，正式放行仍由 MIKO 決定。

### 3.4 修訂、驗收與交接

Manus 依 Claude 的明確修訂項更新候選，不能自行改寫 Claude 的裁決。完成後：

1. 重跑相關測試與負向測試。
2. 由指定讀回者核對遠端內容與 SHA-256。
3. 若需要獨立稽核，交由未參與修改者執行。
4. 保存 Claude 審查、測試、稽核與讀回證據。
5. 建立收工交接，列出四態、狀態軸、困難卡、下一步與負責人。

## 4. 衝突與失敗出口

Manus 與 Claude 意見不同時，先停止爭議寫入與 Runtime，將差異拆成事實、規則、授權與責任四類；以固定正本、diff、測試或唯讀來源消除。仍無法消除時標 `CONFLICT`，交 MIKO 裁決，期間維持保守狀態。

工具或來源失敗時，列：現象、證據、類別、影響哪個 AC、解除條件、負責方、首次發現時間。缺資料、缺授權與工具失敗不得互寫；只停止受影響的相依步驟。

## 5. 收工交接最小格式

```markdown
# 協作交接
- 任務／範圍／非範圍：
- 正本 commit／VERSION／ADR／讀取時間：
- Manus 已完成：
- Claude 審查結論：
- 獨立稽核：
- 來源／執行／審查／採用／Runtime／外部效果：
- 已確認：
- UNKNOWN／NOT_READ／NOT_RUN／BLOCKED／CONFLICT：
- 困難卡：
- 下一步、執行者、完成判準、失敗出口：
- 邊界：不自動授權正式採用、Runtime、停止解除或不可逆操作。
```

## 任務四態

**完成但有疑慮**：SOP 已建立；仍須 Claude 正式審查、獨立稽核、負向測試與 MIKO 放行。
