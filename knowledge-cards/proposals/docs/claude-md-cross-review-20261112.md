# CLAUDE.md 修復品質交叉審查與正本文件稽核提案

狀態：未驗收提案
目標提交：`910ee38b7e2bf9577e3972685cd1b155c63339f8`
目標正式檔案：`CLAUDE.md`
提案類型：docs

## 提案目的

將 `CLAUDE.md` 修復提交的交叉審查結果送治理總召審查，並提出下一階段對 MIKO 正本文件的唯讀一致性稽核範圍。本提案不是正本規則，也不會直接修改 `README.md`、`VERSION`、`CHANGELOG.md` 或其他正式檔案。

## 已完成且可驗證的基線

- `CLAUDE.md` 在提交 `910ee38` 中新增專案結構與常用驗證命令。
- 將過時的「15 項全過」修正為 C1～C16 共 16 項，並修正歷史段落中的對應描述。
- 本機 `tests/check_repo.py`：16/16 PASS。
- 本機 `skills/miko-core/scripts/test_terms_check.py`：21/21 PASS。
- 本機 `skills/miko-core/scripts/test_flowlock_check.py`：27/27 PASS。
- `git diff --check`：PASS。
- GitHub Actions `check_repo`：success。
- 指定 commit 的 GitHub raw `CLAUDE.md` 與本機版本 byte-level SHA-256 一致。

## Claude 主要審查結果

來源：Claude API，模型 `claude-sonnet-5-5`；審查提示的 SHA-256：`dc104981380f7836bde70d922873137aaf03df44758bb8305a1ac4b10e9511c7`。

結論：**PASS WITH CONCERNS**。

已確認的審查摘要：

1. 沒有發現會誤導操作或違反硬邊界的錯誤。
2. `## 推送前後` 第一條仍混入命令、環境變數、C6/C9 例外、ADR 歷史、`MIKO_BASE`、C11 與私密清單等大量內容，可讀性與維護性偏弱。
3. 建議將執行步驟與歷史背景拆開；此項是後續可改善建議，不是本次提交的阻擋性錯誤。
4. 審查方無法取得原始版本的非淺層歷史，因此未把本次內容判定為可做完整歷史 diff 的修復；這是審查證據限制，不是對目前文件內容的失敗判定。

## Gemini 第二意見狀態

本輪未取得 Gemini 審查內容：

- 初次 API 呼叫回傳 HTTP 429 Too Many Requests。
- 未進行盲目重試，以免把外部服務限流當成成功或無限制重試。
- 後續 Claude 重跑時明確停用 Gemini 呼叫，因此 Gemini 狀態為 `NOT_RUN`。
- 本提案不得寫成「Claude／Gemini 一致通過」。

## 治理判定請求

請治理總召逐項裁決：

1. 是否接受 `910ee38` 的 `CLAUDE.md` 修復作為目前文件導覽的可用版本。
2. 是否採納 Claude 提出的後續可讀性改善：將 `## 推送前後` 的現行操作、歷史背景與例外條件拆成較短的可執行段落。若採納，應另開局部修改與獨立稽核，不在本提案直接改正本。
3. 是否啟動下一階段正本文件的一致性稽核。建議唯讀範圍如下：
   - `README.md`
   - `VERSION`
   - `CHANGELOG.md`
   - `adapters/README.md`
   - `skills/miko-core/SKILL.md`
   - `tests/check_repo.py`
   - `.github/workflows/check.yml`
   - `knowledge-cards/README.md`
4. 下一階段至少核對：版本號與日期、README SHA-256、ADR 出處、`CLAUDE.md` 與正本規則是否矛盾、`check_repo` 實際檢查項數量、CI 與文件命令是否一致、Manus 提案區與 writer 邊界是否一致。
5. Gemini 第二意見是否在 API 限流解除後另行補跑；補跑前不得把目前提案標記為雙模型交叉通過。

## 尚未採用或未驗證事項

- `CLAUDE.md` 推送前後長段落的重排：`PROPOSED`，未採用。
- README、VERSION、CHANGELOG、adapters、miko-core 與 CI 的整體一致性：尚未進行本提案範圍外的完整核對，標 `NOT_RUN`。
- Gemini 第二意見：`NOT_RUN`／外部 API 先前回傳 429。
- 任何治理裁決、ADR 登錄、正式正本搬入：`UNKNOWN`，等待治理總召處理。

## 安全與邊界

- 本提案不包含 API key、token、密碼或個人秘密。
- 本提案不宣稱 Gemini 已審查。
- 本提案不修改正式正本、不升版本、不登錄 ADR、不宣稱已治理採用。
- 若後續要修改 `skills/`、`.github/`、`tests/`、`VERSION`、`sync/` 或正本文件，應依既有局部修改、獨立稽核、CI 與當次明確批准流程執行。
