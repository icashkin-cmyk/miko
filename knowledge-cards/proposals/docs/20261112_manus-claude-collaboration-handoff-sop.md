# Manus 與 Claude 協作分工及交接 SOP

## 文件狀態

- 狀態：`PROPOSED`，尚未正式採用。
- 適用範圍：本專案的研究、程式、Skill、文件、治理、PR、驗收與交接。
- 最終授權者：MIKO。
- 正本：開工時動態讀取 GitHub `main/VERSION` 與固定 main HEAD；不得用記憶或舊摘要代替。

## 1. 角色分工

| 角色 | 主要責任 | 不得自行做的事 |
|---|---|---|
| Manus 執行總召 | 接收需求、開工對齊、拆解、執行、建立候選、保存證據、測試、整合、交接（寫入範圍限 `knowledge-cards/`，ADR-088、ADR-092，見下段） | 不得把候選當正本、把工具 ACK 當成果、解除停止、接 Runtime、合併或執行不可逆操作 |
| Claude 治理總召 | 審查正本、版本、邊界、授權、責任、採用條件與衝突 | 不得把自我審查當獨立稽核，不得代替 MIKO 解除停止或作保留決定 |
| 獨立稽核者 | 驗證未參與修改者的證據、測試、讀回與完整性；工具驗收（check_repo、validator、flowlock）與 Claude 複核不算獨立稽核（M2，R-03） | 不得由修改者自我兼任 |
| MIKO | 最終授權、正式放行、停止解除、不可逆決定與衝突裁決 | — |

Gemini 或其他模型只能提供建議；其輸出須標示為模型建議，不是正本、稽核或放行證據。

Manus 執行總召的寫入範圍限 `knowledge-cards/`（含 `knowledge-cards/proposals/`），出處 ADR-088（雙總召試行）、ADR-092（提案區擴大）；Manus 不審查、不放行、不合併、不登錄 ADR、不改版本號。

## 2. 共同不變量

1. Manus 與 Claude 使用同一固定來源、版本、commit、讀取時間與範圍。
2. `PROPOSED`、`REVIEWED`、`ADOPTED`、`RUNTIME_ENABLED`、`WRITTEN` 是不同狀態，不得合併成「完成」。
3. 所有重要主張必須附 miko-core 現行行內證據標籤：來源、工具、使用者、常識、推論、未查證、UNKNOWN。`NOT_READ`、`NOT_RUN`、`BLOCKED`、`CONFLICT` 是狀態用語，不是另一套證據標籤；Claude 的意見要標為 Claude 回報，不代表已獨立驗證。
4. 未取得授權時，停止外部寫入、刪除、分享、權限變更、費用、Runtime 與不可逆操作。
5. 交易、Broker、LIVE、台指期停止狀態與回測暫停狀態依既有硬邊界處理，不得改名或繞過。例外：check_repo 的 C6、C9 用固定樣本跑回測引擎回歸檢查，不算違反回測暫停，照跑（ADR-074）；帶 `--skip-backtest` 時 C6、C9 印 `NOT_RUN`，不算 PASS。

## 3. 標準流程

### 3.1 Manus 開工

1. 讀 miko-core、VERSION、適用 Skill、專案指示與既有 Task。
2. 固定來源 commit，記錄版本、ADR、讀取時間、範圍與 Writer／Owner。
3. 寫出目標、非目標、授權、依賴、驗收條件與失敗出口。
4. 只在 `knowledge-cards/`（ADR-088）授權範圍內執行；候選內容預設落點為 `knowledge-cards/proposals/`（ADR-092）。搬入 `skills/`、`.github/`、`tests/`、`VERSION`、`sync/` 須經原稽核，並須 MIKO 逐件、當次明確批准；常設免問推送授權不算。Manus 只開分支與 PR，不直推 main，不改 `knowledge-cards/` 以外路徑。
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

每次送治理審閱前，Manus 必須先呼叫 Claude API 自查，並把結果交給 Claude 治理總召複核；首次送審、角色／授權／狀態軸／裁決用語／停止狀態／ADR 改義、材料 SHA-256 變更、Manus／Claude 衝突，都一定要呼叫。只有路徑、標籤、漏句、名詞、格式這類不改意思的小錯，可不重跑 API 複核就修，但須留 diff；來源、數值、日期、結論只要有一點存疑就不算小錯，要標 `UNKNOWN` 或 `NOT_RUN`，不得用「看起來合理」補寫或推定。是否屬小錯由 Claude 判定，Manus 不得自判後跳過複核。修小錯的那一次不需重跑 API 自查；但之後每一次正式送審前，仍須有當次自查（MIKO 2026-11-13 23:55 台北授權由總召決定，M4）。

每次必須保存：`request_id`、完整 request payload、完整 response、實際 `model`、Asia/Taipei 請求／回應時間、每份材料 SHA-256、固定來源 commit／VERSION／ADR、`api_status`、`stop_reason`、token、request／response SHA-256 與讀回位置。API 失敗、逾時、截斷、空回覆或只有 ACK 一律標 `BLOCKED` 並停止送審，開困難卡；金鑰未設定標 `NOT_RUN`；不得以 ACK、HTTP 200、請求送出或其他模型建議代替審查。閘門 `PASS` 只表示呼叫與保存完成，不是審查通過。

自查結果為 `REVISE` 時，正式閘門標 `BLOCKED`，不得送審、須修訂後重跑自查，且不適用 `NOT_RUN` 的當次豁免，Claude 不自行當作豁免（M1）。`NOT_RUN` 時仍可開 PR 當候選，審查包須寫明 `API 自查閘門=NOT_RUN` 與原因；Claude 不答 `UPLOAD_FOR_REVIEW=YES`，除非 MIKO 當次明確豁免。金鑰由 MIKO 親手填到平台密鑰設定，費用由 MIKO 親手處理；Manus 不索取、不複述、不保存金鑰。

Claude API 複核不是獨立稽核，也不授權採用、Runtime、合併或解除停止；完整結果須交 Claude 治理總召複核，正式放行仍由 MIKO 決定。

### 3.4 修訂、驗收與交接

Manus 依 Claude 的明確修訂項更新候選，不能自行改寫 Claude 的裁決。完成後：

1. 重跑相關測試與負向測試。
2. 由指定讀回者核對遠端內容與 SHA-256。
3. 若需要獨立稽核，交由未參與修改者執行。
4. 保存 Claude 審查、測試、稽核與讀回證據。
5. 建立收工交接，列出四態、狀態軸、困難卡、下一步與負責人。
6. 小錯規則（MIKO 2026-11-12 17:41）：路徑、標籤、漏句、名詞、格式、機械性 C3 FAIL、檔頭這類小錯，Claude 可直接在 Manus 自己的分支修，只動 `knowledge-cards/` 內檔案，條件是 check_repo C1～C16 全過（C15 只提示不擋）、列變更清單、不改意思，事後報告；改意思、新權限、硬邊界、碰 `skills/`、`.github/`、`tests/`、`VERSION`、`sync/`、任何外部寫入與刪除，一律停下問 MIKO。是否屬小錯由 Claude 判定，Manus 不得自判後跳過複核。

## 4. 衝突與失敗出口

Manus 與 Claude 意見不同時，先停止爭議寫入與 Runtime，將差異拆成事實、規則、授權與責任四類；以固定正本、diff、測試或唯讀來源消除。仍無法消除時標 `CONFLICT`，交 MIKO 裁決，期間維持保守狀態。

工具或來源失敗時，列：現象、證據、類別、影響哪個 AC、解除條件、負責方、首次發現時間。類別用 miko-core 現行四類：缺資料、缺決定／授權／付費、技術失敗、外部依賴，不得互寫；來源衝突不另立類別，並列呈現、標 `CONFLICT`，交 MIKO 裁決；只停止受影響的相依步驟。

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
