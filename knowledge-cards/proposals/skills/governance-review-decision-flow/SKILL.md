---
name: governance-review-decision-flow
description: "MIKO 候選治理文件的正式裁決、放行與狀態軸管理流程。Use for: preparing a governance decision package, recording MIKO adoption or release decisions, checking Claude review boundaries, managing PROPOSED/ADOPTED/RUNTIME states, or validating PR evidence without treating API replies as approval."
---

# 治理複核裁決與放行流程（候選 Skill）

本候選 Skill 目前只放在 `knowledge-cards/proposals/skills/`，尚未啟用、尚未正式採用，也不授權 Manus、Claude 或任何工具直接放行、合併、接 Runtime 或修改正式正本。

## 角色邊界

- **Manus 執行總召**：責任限於本專案 `knowledge-cards/`（包含 `knowledge-cards/proposals/`）；在該範圍內固定來源、整理材料、執行可授權檢查、保存證據、建立候選與交接；不得將本 Skill 解讀為全專案 writer 授權，不得指揮 Claude、代替治理裁決、放行、合併或自任獨立稽核。
- **Claude 治理總召**：複核候選內容的來源、規則、責任、授權、狀態與衝突，提出 `PASS`、`REVISE`、`BLOCKED` 或 `UNKNOWN`；不代替 MIKO 正式採用或放行，也不把自我複核當獨立稽核。
- **獨立稽核者**：驗證未參與修改者的證據、測試、讀回與完整性。
- **MIKO**：作正式採用、放行、合併、Runtime 啟用、停止解除、不可逆操作與未解決衝突的最終決定。

## W1～W7 與責任閘門

使用者提供的《總召工作守則｜雙總召行列式最新版》是 W1～W7 的候選參考與可執行細化來源，不是 GitHub 正本、正式 Skill 或正式治理裁決；本輪附件條文未核讀時標 `NOT_READ`，未經審查與放行不得宣稱生效。

若使用者附件 A0.4、W1.2、W1.3、W6.2、W7.1～W7.2 已逐條讀取，才可將其作為候選參考；本輪未核讀時狀態為 `NOT_READ`，不得把它們當驗收依據，也不得列入必要驗收閘門。附件讀取後，參考其責任表時，委派、跨總召、跨平台或寫入前填：來源版本／commit、writer、主要執行者、驗收者、整合者、讀回者、失敗處理者、目標位置、宣告時間（Asia/Taipei）、驗收條件與交付位置；W1.2 的最低派工欄位是目標、來源檔、版本／commit、責任欄、驗收條件與交付位置；必要時再補輸入、禁做、AC、回報格式；W1.3 要求指定驗收者讀回完整結果，不得以摘要或模型自評代替。

若附件已讀，W1～W7 可作候選對照：W1 直接執行或委派；W2 文章、Skill、規則審查；W3 Skill／規則修改；W4 正本推送、合併與回讀；W5 Drive 存檔；W6 回報與建設性下一步；W7 收工、換手與額度將盡。附件未讀時不以此摘要取代正本；W6.2 的下一步與 W7 交接欄位只能在來源核實後採用。

## 六個狀態軸

使用六個彼此獨立的軸，禁止用單一「完成」取代：

| 軸 | 合法值 | 轉換規則摘要 |
|---|---|---|
| 來源 | `READ`、`NOT_READ`、`STALE`、`CONFLICT` | 固定來源與必要檔案讀取完成才是 `READ`；落後是 `STALE`；來源或雜湊不一致是 `CONFLICT`；證據不足維持 `NOT_READ`。 |
| 執行 | `NOT_RUN`、`PASS`、`FAIL`、`BLOCKED` | 實際執行後依驗收結果轉換；`FAIL` 修正後必須重跑；`BLOCKED` 解除後先回 `NOT_RUN`。備註不得改造合法值，例如局部結果寫 `PASS`，另列未執行項。 |
| 審查 | `NOT_RUN`、`PASS`、`REVISE`、`BLOCKED`、`UNKNOWN` | `NOT_RUN` 只指正式治理審查尚未開始；有足夠材料且無必修缺口才是 `PASS`；有修訂要求是 `REVISE`；材料不足但可補證據用 `UNKNOWN`；依賴或授權未解除用 `BLOCKED`。API 自查另記，不改寫本軸。 |
| 採用 | `PROPOSED`、`NOT_ADOPTED`、`ADOPTED` | 初始為 `PROPOSED`；只有 MIKO 明確決定且記錄版本、生效日與存放位置才可 `ADOPTED`。 |
| Runtime | `DISABLED`、`ENABLED`、`UNKNOWN` | 沒有實際接線證據不得 `ENABLED`；讀不到狀態是 `UNKNOWN`；啟用須有 MIKO 授權。 |
| 外部效果 | `NONE`、`READ_ONLY`、`WRITTEN`、`UNKNOWN` | 依實際讀寫證據記錄；不以預期結果代替實際效果。 |

每次狀態轉換保存：前值、後值、觸發證據、時間、實際執行者、授權者與讀回位置。任何一軸的 `PASS` 或 `ADOPTED` 都不能自動推導其他軸。

## 標準操作流程

### 1. 固定來源

記錄 repo、branch、固定 commit、VERSION、ADR、讀取時間、檔案範圍與每檔 SHA-256。正本或 ADR 未讀取時標 `NOT_READ` 或 `UNKNOWN`，不得自行補造條文。

### 1.1 建立責任閘門

在委派、跨總召、跨平台或任何寫入前，先填完整責任表。缺少 writer、驗收者、整合者、讀回者、失敗處理者、目標位置或宣告時間時，停在可逆準備，不開始受影響步驟。單一路徑同一階段只能有一個 writer。

### 2. 建立審查包

審查包至少包含：

- 任務目標、範圍、非範圍與授權。
- 候選文件清單、用途、差異與 SHA-256。
- 已執行與未執行的命令、測試、CI、讀回與限制。
- Claude API request／response、模型、時間、HTTP 狀態、stop reason、request／response SHA-256 與保存位置（每次送審前都要先呼叫 API 自查，失敗標 `BLOCKED`，金鑰未設定標 `NOT_RUN`）；自查判定另記 `PASS／REVISE／BLOCKED／NOT_RUN`；自查為 `REVISE` 時正式閘門軸填 `BLOCKED`，不填 `REVISE`（MIKO 2026-11-13 23:55 台北授權由總召決定，M1）。
- UNKNOWN、NOT_READ、NOT_RUN、BLOCKED、CONFLICT 與困難卡。
- 要請 Claude 提供意見的問題；不得把問題寫成指揮 Claude 的指令。

### 3. Claude 治理複核（候選流程，待 MIKO 裁決採用）

Claude 先判斷來源與材料是否足夠，再分別輸出：

```text
審查狀態：PASS／REVISE／BLOCKED／UNKNOWN
UPLOAD_FOR_REVIEW：YES／NO／UNKNOWN
ADOPT：YES／NO／UNKNOWN
RUNTIME：YES／NO／UNKNOWN
```

這四組欄位不得混成單一通過值。`UPLOAD_FOR_REVIEW=YES` 不代表 `ADOPT=YES`，API 回覆成功也不代表任何正式採用。正式 API 閘門值域為 `PASS／BLOCKED／NOT_RUN`；自查若為 `REVISE`，正式閘門標 `BLOCKED` 並不得送治理複核，修訂後須重跑自查；`REVISE` 不適用 `NOT_RUN` 的 MIKO 當次豁免路徑。

### 4. MIKO 正式裁決或放行

只有在 MIKO 明確要作正式裁決時，使用下列格式；Claude 或 Manus 不得代填 MIKO 的決定：

```markdown
# MIKO 正式治理裁決／放行紀錄

## 裁決識別
- 裁決編號：
- 裁決日期（Asia/Taipei）：
- 裁決者：MIKO
- 對象文件／PR：
- 採用軸：PROPOSED／ADOPTED／NOT_ADOPTED

## 固定基線
- repo／branch：
- 固定 commit：
- VERSION／ADR：
- 候選文件 SHA-256：
- 讀取時間與來源：

## 前置驗收
- Claude 治理複核：PASS／REVISE／BLOCKED／UNKNOWN
- UPLOAD_FOR_REVIEW：YES／NO／UNKNOWN
- 獨立稽核：PASS／FAIL／NOT_RUN／UNKNOWN
- check_repo C1～C16：PASS／FAIL／NOT_RUN（逐項列出）
- API 自查閘門：PASS／BLOCKED／NOT_RUN；紀錄位置：
- 未解決 UNKNOWN／NOT_READ／CONFLICT：

## MIKO 明確決定
- 是否採用 Claude API 複核閘門：`YES／NO`
- 是否採用六軸狀態格式：`YES／NO`
- 正式採用：YES／NO
- 正式放行：YES／NO
- 合併 PR：YES／NO
- 接 Runtime：YES／NO
- 解除停止或暫停：YES／NO／不適用
- 生效版本：
- 生效日期：
- 正式存放位置：

## 決定理由與限制
- 理由：
- 必須保留的限制：
- 回滾條件與負責人：

## 狀態轉換後
- 來源：
- 執行：
- 審查：
- 採用：
- Runtime：
- 外部效果：

## 簽認
- MIKO 明確裁決原文／確認方式：
- 實際執行者：
- 讀回證據與 SHA-256：
- 任務四態：完成／完成但有疑慮／需要資料／卡住
```

### 5. 執行放行後動作

依 MIKO 明確決定逐項執行，不擴張授權。每一項都要保存命令、操作者、時間、輸出與讀回結果。若任何讀回、CI、權限或外部服務失敗，停止相依步驟，標 `BLOCKED` 或 `UNKNOWN`，開困難卡，不把局部成功寫成整體完成。

### 6. 衝突處理

Manus 與 Claude 意見不同時，先停止爭議中的正式寫入、Runtime、合併與不可逆操作；保留雙方原結論與證據，按事實、規則、授權、責任與狀態軸拆解。API 複核只能作為證據之一，不構成裁決。無法消除時標 `CONFLICT`，交 MIKO 裁決。

## 驗收閘門

- [ ] 固定來源、VERSION、commit、ADR 與檔案 SHA 已記錄。
- [ ] 已依 A0.4 建立責任表，列出 writer、主要執行者、驗收者、整合者、讀回者、失敗處理者、目標位置與宣告時間。
- [ ] 若有委派，已依 W1.2 填目標、來源檔、版本／commit、責任欄、驗收條件與交付位置；受派結果已依 W1.3 由指定驗收者讀回完整內容。
- [ ] 六個狀態軸已各自填值，沒有以「完成」取代。
- [ ] Claude 複核、獨立稽核、採用、Runtime 與外部效果已分開。
- [ ] MIKO 正式決定欄位由 MIKO 明確填寫，沒有代決。
- [ ] `check_repo` C1～C16 結果已逐項記錄；未執行者標 `NOT_RUN`。
- [ ] API 失敗、截斷、空回覆或 ACK-only 沒有被標成 `PASS`。
- [ ] UNKNOWN／NOT_READ／NOT_RUN／BLOCKED／CONFLICT 與困難卡已揭露。
- [ ] 放行後已保存實際執行與讀回證據。
- [ ] 本 Skill 仍位於 `knowledge-cards/proposals/` 時，不得視為已啟用。

## 限制

本候選 Skill 不修改正式 miko-core、Skill、tests、VERSION、sync 或 Runtime；不授權交易、Broker、LIVE、停止解除、外部不可逆操作或 PR 合併。所有正式採用與放行仍須依 MIKO 明確裁決及正本規則執行。
