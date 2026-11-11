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

## 附加工作串整合：名詞與架構判準

附加工作串「評估簡短 Skill 名詞的描述能力」提出的核心判準是：短名可以保留，但第一次出現時要能對應正式名稱，並讓讀者知道觸發條件、執行動作、輸出格式與完成判準。它把規則分成流程、輸出、檢核、限制、處置五類。這項建議與目前 `miko-core v1.71`、正本 `1.2.70` 的現行名詞制度大致一致，因為現行 `SKILL.md` 與 `references/term-definitions.md` 已採用短名、正式名稱與五類標籤。

因此，附加工作串的內容應整合為「架構稽核與可讀性改善建議」，不直接把舊卡片內容搬入正本。附加檔案本身是 `miko-core 代入卡 v2.5／正本 1.2.52` 的歷史材料；目前正本已是 `miko-core v1.71／VERSION 1.2.70`。任何差異都必須先標為歷史證據，不能當成現行規則。

## 建議的文件與 Skill 架構

建議治理總召以以下六層重新整理文件責任；本提案只提出架構，不直接搬動檔案：

1. **權威與治理層**：`README.md`、`VERSION`、`CHANGELOG.md`、`skills/miko-core/SKILL.md`。負責現行規則、版本、裁決、授權、審查與放行。
2. **執行 Skill 層**：`skills/*/SKILL.md`。負責特定任務的觸發條件、執行步驟、輸出與失敗處理；共同短名定義集中由 `miko-core/references/term-definitions.md` 管理。
3. **驗證與 CI 層**：`tests/`、`skills/*/scripts/`、`.github/workflows/check.yml`。負責可重跑的檢查與回歸，不重新定義治理權責。
4. **平台適配層**：`adapters/README.md` 及各平台副本。只負責如何取得正本與啟動，不得另造一套與 miko-core 不同的權限、版本或輸出規則。
5. **提案與候選層**：`knowledge-cards/proposals/` 與 K01～K50。只放未驗收提案或候選卡；不得視為已生效正本。
6. **狀態與歷史層**：`sync/`、歷史 ADR 與測試紀錄。負責協作、證據與歷史脈絡，不取代現行正本。

## 已發現的衝突與邊界風險

### C-1：歷史代入卡與目前正本版本不同

附加工作串使用的代入卡是 v2.5、對應正本 1.2.52；目前 repo 是 miko-core v1.71、正本 1.2.70。這不是現行規則衝突，而是來源時效差異。處理方式應是保留歷史證據、標 `HISTORICAL_NOT_RUNTIME`，並以目前 GitHub 正本重核。

### C-2：平台適配文件的對齊行要求可能低於現行核心要求

`adapters/README.md` 的平台段落主要要求回報正本版本，但目前 miko-core §1.4 另要求對齊行帶 commit 與台北讀取時間。若平台副本仍只要求版本，會形成「平台最低格式」與「現行核心完整格式」的不一致。建議下一階段逐平台核對並由治理總召決定是補齊 adapters，或明確標示平台副本只提供最低啟動格式。

### C-3：Manus 寫入邊界與本次歷史執行方式需要治理記錄

目前正本和 `knowledge-cards/README.md` 都寫明：Manus 只能在 `knowledge-cards/` 內走分支與 PR；其他正式檔案由 Claude 總召寫入。`CLAUDE.md` 的 `910ee38` 曾由本工作串直接推送到 `main`，這與目前文件所述 writer 邊界不一致。這是流程證據衝突，不宜靠事後修改文件消除；請治理總召判定本次是否屬 MIKO 當次明確例外，或登錄為流程偏差並補強後續 writer 閘門。

### C-4：PR 越界檢查目前是提示，不是阻擋

`.github/workflows/check.yml` 對 `manus/` 分支修改 `knowledge-cards/` 以外檔案只產生 warning；`knowledge-cards/README.md` 則要求 Manus PR 只能包含 `knowledge-cards/`，越界時 Claude 不審內容。兩者不是文字直接矛盾，但 CI 沒有把治理邊界變成硬性失敗條件，形成可通過但不應合併的狀態。建議治理總召決定是否保持「只提示、人工攔截」，或新增不改變責任分工的阻擋檢查。

### C-5：版本標記的歷史出處容易被讀成現行版本

`knowledge-cards/README.md` 的「提案區（1.2.69，ADR-092）」與目前 VERSION 1.2.70 並不必然矛盾，因為它是在描述提案區規則的引入版本；但若沒有「引入版本／現行正本」的明確欄位，讀者可能把 1.2.69 誤認為目前版本。建議在下一階段稽核中統一歷史版本標記格式，不直接刪除歷史出處。

## 下一階段稽核順序

先核對權威與治理層，再核對平台適配層，最後檢查驗證與 CI 是否真正執行文件宣稱的邊界。每個衝突要分成「現行語意衝突」「歷史出處易混淆」「流程執行偏差」三類，逐項提出採納、不採納或保留；未經治理裁決不得修改正本。
