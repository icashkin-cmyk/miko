# knowledge-cards｜Manus 任務卡（K01～K50）存放處｜2026-11-11

> 名詞：正本（正式名稱：GitHub 上的正式規則來源與目前採用版本）【限制】；硬禁止（正式名稱：當次指示也不執行的禁止事項：下單、交易、Broker、LIVE）【限制】；治理（正式名稱：規則版本、變更、授權、審查與正式放行管理）【流程】；困難卡（正式名稱：失敗分類與阻塞處置卡）【處置】；定義見 skills/miko-core/references/term-definitions.md（MIKO 核心詞彙與行為定義表）。本檔的「總召」指 MIKO 指定負責協調與寫入範圍的 AI（正本 README §6）；「單一 writer」指一個範圍只有一個寫入者。

## 這個資料夾是什麼

- 存放 MIKO 給 Manus 用的任務卡（正式名稱：Manus 平台的自訂指令卡，每張含「名稱、在以下情況下使用、內容」三欄，內容欄以 Manus 介面 1,000 字元為上限），編號 K01～K50，一張一檔：`K01.md`、`K02.md`……
- 不是 MIKO 正本，也不是 Skill。卡片和正本（README.md、skills/miko-core/SKILL.md）衝突時，以正本為準；卡片不能解除正本的停止、暫緩、硬禁止與授權規則。

## 誰可以寫（雙總召試行，正本 1.2.65，ADR-088）

| 範圍 | 唯一寫入者（單一 writer） | 依據 |
|---|---|---|
| knowledge-cards/ 本資料夾 | **Manus 總召** | MIKO 2026-11-11 17:43（台北）「請直接執行 並 修改改成 manus 換人當當看」、17:43「應該是 claude 總召 跟 manus總召」 |
| 其他所有檔案（README.md、VERSION、CHANGELOG.md、skills/、tests/、sync/、adapters/、projects/；sync/gpt/ 依正本 README §4 為已停用的歷史例外） | Claude 總召 | 正本 README §6 |

- 首批檔案（本 README、K01.md、proposals/README.md）由 Claude 總召依 MIKO 同一則指示代為建立；之後本資料夾由 Manus 總召維護。
- Manus 總召不是治理總召：不審查、不放行門檻、不宣稱已採用、不登錄 ADR、不改正本版本號；正本裡寫「總召」「治理總召」之處都指 Claude 總召。Manus 的困難卡、改善提案放 proposals/，只算提案，要 Claude 總召審查採納後才進正本。
- 卡片 PR 只改本資料夾，不升正本版本、不加 CHANGELOG；Claude 總召合併前照正本 README §6 確認，卡片內容涉及規則改動時改走正本改版與獨立稽核。
- Manus 總召的寫入方式：開分支 → 改本資料夾的檔案 → 開 PR → GitHub Actions check_repo 通過 → Claude 總召審查（只查是否和正本衝突、有無私密字或金鑰）→ MIKO 或 Claude 總召合併。不直推 main，不改本資料夾以外的檔案。
- Manus 要有 GitHub 寫入權，需要 MIKO 親手授權；授權前 Manus 只產出全文，由 MIKO 轉給 Claude 總召代放。金鑰或 Token 不寫進任何檔案、PR 或對話。
- 試行：MIKO 說停止或改回，就恢復成 Claude 總召唯一寫入；已合併的卡片保留。

## 卡片狀態

每張卡的檔頭寫一行「狀態」，只能是下列之一：
- 候選：寫好但未在 Manus 實測。
- 已實測：在 Manus 跑過觸發測試，附測試輸入與結果。
- 停用：不再使用（不刪檔，改這一行並寫原因）。

## 索引

| 編號 | 名稱 | 狀態 | 最後更新 |
|---|---|---|---|
| K01 | 核心任務辨識與後設控制循環 | 候選 | 2026-11-11 |
