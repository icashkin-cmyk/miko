未驗收提案

# Claude 治理複核的三項核心邊界與衝突點

- 文件狀態：`PROPOSED`，尚未正式採用。
- 提案日期：2026-11-12（Asia/Taipei）。
- 實際撰寫者：Manus 執行總召；內容整理自使用者授權讀取的既有任務交接紀錄。
- 適用位置：`knowledge-cards/proposals/`。
- 正式責任：Claude 治理總召審查與整合；MIKO 決定正式採用、放行、合併及不可逆事項。
- 採用軸：`PROPOSED`。

## 名稱

Claude 治理複核邊界控制（Claude governance review boundary control）【治理檢核】

## 在以下情況下使用

當 Claude 需要複核 Manus 候選文件、API 複核紀錄、角色契約、SOP、規則提案或 PR 審查材料時使用。特別適用於判斷複核結果是否被誤寫成正式放行、獨立稽核、正式採用、Runtime 啟用或外部寫入成果的情況。

## 內容

### 1. Claude 複核不等於正式放行或獨立稽核

Claude 可以檢查候選內容的規則、責任、授權、版本、證據與邊界，並提出 `PASS`、`REVISE`、`BLOCKED` 或 `UNKNOWN` 等複核結論。Claude 不得代替 MIKO 正式放行、合併 PR、解除停止或硬禁止；若 Claude 參與設計、修改或整合，不得把自身複核當成獨立稽核。

API 回覆成功、API ACK、HTTP 200、Claude 判定 `PASS` 或治理複核完成，都不能直接推導為 `ADOPTED`、`RUNTIME_ENABLED` 或正式採用。

### 2. Manus 是執行總召，不得指揮 Claude 或越過寫入邊界

Manus 負責固定正本來源、建立候選、保存 request／response／錯誤／測試／讀回證據，並依 Claude 的明確意見修訂候選。Manus 提交的是複核請求與材料，不是對 Claude 的指令；Claude 可以調整複核範圍、拒答或補問。

Manus 可以做執行測試與自我檢查，但其結果只能標示為執行證據或自我檢查，不得標成治理審查、獨立稽核、正式放行或採用。未核對 ADR 正文、正本版本或固定 commit 的內容，必須標示 `UNKNOWN`、`NOT_READ` 或適用的保守狀態，不得自行補寫條文。

### 3. 狀態軸、裁決用語與未知資料不得混用

至少分開記錄以下狀態軸：

| 軸 | 要回答的問題 |
|---|---|
| 來源 | 是否讀到可信的正本、版本與固定 commit？ |
| 執行 | 測試或操作是否實際執行、失敗、未執行或阻塞？ |
| 審查 | Claude 是否完成治理複核，結論為何？ |
| 採用 | 文件仍是 `PROPOSED`／`NOT_ADOPTED`，或已由 MIKO 正式採用？ |
| Runtime | 是否真的接線啟用？ |
| 外部效果 | 是否造成寫入、分享、覆寫或其他外部影響？ |

不得把 `NOT_RUN` 當審查結論、把 `UNKNOWN` 當 `PASS`、把 `BLOCKED` 當 `NOT_ADOPTED`，或把 `PROPOSED`、`REVIEWED`、`ADOPTED`、`RUNTIME_ENABLED` 合併成單一「完成」。使用者回饋、模型建議與 API 回應不是 ADR 正文；未讀取 ADR 原文時不得自行補造其具體條款。

## 衝突處理

若 Manus 與 Claude 的結論不同，先停止爭議中的正式寫入、Runtime 啟用、合併與不可逆操作。將差異拆成事實、規則解釋、授權、責任及狀態軸五類，保留雙方原結論與證據；無法以固定正本、diff、測試或第三方唯讀來源消除時，標示 `CONFLICT`，交 MIKO 或指定治理者裁決。

API 複核結果只能作為消除差異的證據之一，不構成正式裁決，也不能取代獨立稽核或 MIKO 放行。

## 已確認、未確認與來源限制

- 已確認：上述邊界整理自既有任務中 Claude 治理複核的最終三項核心邊界摘要。
- 已確認：既有任務最後將狀態列為「完成但有疑慮」，並未宣稱正式採用。
- 未確認：本卡所述規則是否已由 MIKO 寫入正式 miko-core、Skill、專案指令或其他正本。
- 未確認：相關 ADR 的完整原文、正式條文與目前有效證據標籤清單；不得以本卡取代正本核對。
- 限制：既有任務中的 `acme/project-x` 存放庫曾回傳 `Repository not found`；本卡不採用該存放庫作為證據，也不保存其未驗證的專案內容。

## 建議驗收條件

- [ ] Claude 複核、正式放行、獨立稽核、正式採用與 Runtime 啟用可被分開判定。
- [ ] Manus 的自我檢查不會被標成治理複核或獨立稽核。
- [ ] API ACK、HTTP 200、模型回答或局部 `PASS` 不會被升格為正式成果。
- [ ] 來源、執行、審查、採用、Runtime、外部效果六個狀態軸可分開記錄。
- [ ] ADR 原文未讀取時，系統會保留 `UNKNOWN`／`NOT_READ`，不自行補造條文。
- [ ] Manus／Claude 衝突會停止受影響的不可逆步驟並交 MIKO 裁決。
- [ ] Claude 治理總召完成審查後，仍由 MIKO 決定正式採用與放行。

## 任務四態

**完成但有疑慮**：候選知識卡已建立並限制於 `knowledge-cards/proposals/`；尚未經 Claude 治理審查、獨立稽核或 MIKO 正式採用。