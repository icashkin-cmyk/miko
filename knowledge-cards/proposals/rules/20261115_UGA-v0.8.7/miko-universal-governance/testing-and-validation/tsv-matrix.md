---
doc_id: uga-acceptance-matrix
name_en: Acceptance Matrix
name_zh: 驗收矩陣
module: testing-and-validation
version: 0.8.7
date: 2026-11-14
status: PROPOSED
---

# 驗收矩陣（v0.8.7）

## 狀態定義

| 狀態 | 意義 |
|---|---|
| `PASS` | 由本輪檢查器實際執行並通過（附檢查器 ID） |
| `NOT_RUN` | 行為層條件，本輪未由獨立驗收者實際執行 |
| `UNKNOWN` | 無可靠證據 |
| `BLOCKED` | 缺授權或外部依賴 |

## UCP 42 條 AC

| 步驟 | AC | 方法 | 證據 | 判定者 | 狀態 |
|---|---|---|---|---|---|
| A00 | AC-A00-01 請求子項有任務條目 | 行為觀察 | task-card | R-AUD | `NOT_RUN` |
| A00 | AC-A00-02 禁止項與授權已列 | 行為觀察 | task-card | R-AUD | `NOT_RUN` |
| A00 | AC-A00-03 核心狀態與計數器已標 | 文件檢視 | 本文件 front matter `runtime_verified` | R-SELF | `PASS` |
| A00 | AC-A00-04 三份常駐文件有載入結果 | 行為觀察 | task-card 載入區塊 | R-AUD | `NOT_RUN` |
| A00 | AC-A00-05 LITE 判定有理由且不在禁止清單 | 人工檢視 | task-card 分級區塊 | R-AUD | `NOT_RUN` |
| A00 | AC-A00-06 對齊行含正本版本、commit、讀取時間 | 行為觀察 | 對齊行 | R-AUD | `NOT_RUN` |
| A00 | AC-A00-07 行內標籤與流程鎖三數相符 | 行為觀察 | 回覆尾行 | R-AUD | `NOT_RUN` |
| A01 | AC-A01-01 來源登錄表欄位齊全 | 行為觀察 | sources.json | R-AUD | `NOT_RUN` |
| A01 | AC-A01-02 每個 NOT_READ 有原因 | 行為觀察 | sources.json | R-AUD | `NOT_RUN` |
| A01 | AC-A01-03 讀取時間已記錄 | 行為觀察 | sources.json | R-AUD | `NOT_RUN` |
| A02 | AC-A02-01 唯一 route_id | TSV-ROUTE | contract.yaml routes | R-SELF | `PASS` |
| A02 | AC-A02-02 契約選擇有理由 | 行為觀察 | routing.json | R-AUD | `NOT_RUN` |
| A02 | AC-A02-03 無未路由產物 | TSV-ROUTE | routes 9 條涵蓋 8 類 | R-SELF | `PASS` |
| A03 | AC-A03-01 必填欄位 100% 列出 | TSV-CONTRACT | contract.yaml | R-SELF | `PASS` |
| A03 | AC-A03-02 省略有理由 | 行為觀察 | field-lock.json | R-AUD | `NOT_RUN` |
| A03 | AC-A03-03 契約版本已記錄 | 文件檢視 | front matter | R-SELF | `PASS` |
| A04 | AC-A04-01 章節可追溯流程 | 人工對照 | uac 附錄 A | R-AUD | `NOT_RUN` |
| A04 | AC-A04-02 步驟有章節承接 | 人工對照 | ucp §4 與 uac 附錄 A | R-AUD | `NOT_RUN` |
| A04 | AC-A04-03 D-01～D-07 有紀錄 | 文件檢視 | ucp A04 | R-SELF | `PASS` |
| A05 | AC-A05-01 十六章／四節齊全 | TSV-STRUCT | 16/16、9 契約、4 節 | R-SELF | `PASS` |
| A05 | AC-A05-02 欄位名逐字一致 | TSV-CONTRACT | 十六章欄位比對 | R-SELF | `PASS` |
| A05 | AC-A05-03 格式範例存在 | 文件檢視 | uac 附錄、readme-templates | R-SELF | `PASS` |
| A06 | AC-A06-01 AC 覆蓋必填欄位 | TSV-CONTRACT | contract.yaml | R-SELF | `PASS` |
| A06 | AC-A06-02 每條 AC 有測試案例 | 人工對照 | 本矩陣＋regression | R-AUD | `NOT_RUN` |
| A06 | AC-A06-03 判定者非製作者 | 人工對照 | 本矩陣 judge_role | R-AUD | `NOT_RUN` |
| A07 | AC-A07-01 每步至少一失敗出口 | TSV-EXIT | 14/14 | R-SELF | `PASS` |
| A07 | AC-A07-02 重試上限有限 | TSV-EXIT | budget 3／2 | R-SELF | `PASS` |
| A07 | AC-A07-03 回復路徑可終止 | TSV-DAG＋人工 | 終止性說明 | R-SELF | `PASS` |
| A08 | AC-A08-01 覆蓋 100% AC | 行為觀察 | self-acceptance.json | R-AUD | `NOT_RUN` |
| A08 | AC-A08-02 無空結果 | 行為觀察 | self-acceptance.json | R-AUD | `NOT_RUN` |
| A08 | AC-A08-03 只用自我層標籤 | 行為觀察 | self-acceptance.json | R-AUD | `NOT_RUN` |
| A09 | AC-A09-01 缺口 100% 有決定 | 行為觀察 | reinforcement.json | R-AUD | `NOT_RUN` |
| A09 | AC-A09-02 補強有來源依據 | 行為觀察 | reinforcement.json | R-AUD | `NOT_RUN` |
| A09 | AC-A09-03 AC 未放寬 | 人工對照 | v0.1→v0.8.7 diff | R-AUD | `NOT_RUN` |
| A10 | AC-A10-01 每輪有 diff | 檔案檢視 | diff/ | R-SELF | `PASS` |
| A10 | AC-A10-05 只修受影響單元且重測範圍有理由 | 行為觀察 | diff 與變更帳 | R-EVD | `NOT_RUN` |
| A10 | AC-A10-02 變更有理由 | 檔案檢視 | 本文件修正紀錄 | R-SELF | `PASS` |
| A10 | AC-A10-03 歷史未覆寫 | 檔案檢視 | v0.1、v0.2 保留 | R-SELF | `PASS` |
| A10 | AC-A10-04 變更帳就地更新並對應 diff | TSV-LEDGER | ledger-spec 第 5 章 | R-SELF | `PASS` |
| A11 | AC-A11-01 回歸 100% 有結果 | TSV-REGRESSION | 10/10 | R-SELF | `PASS` |
| A11 | AC-A11-02 retest_round ≤3 | TSV-EXIT | 本輪 2 輪 | R-SELF | `PASS` |
| A11 | AC-A11-03 無 FAIL 才進 A12 | 流程紀錄 | 本輪檢查結果 | R-SELF | `PASS` |
| A12 | AC-A12-01 驗收者隔離 ≥L1 | 人工檢視 | Claude API 冷啟動（L2） | R-AUD | `NOT_RUN` |
| A12 | AC-A12-04 封裝驗證與報告欄位齊全 | TSV-AUDIT | 附錄 A.4 欄位 | R-SELF | `PASS` |
| A12 | AC-A12-05 接觸作者或竄改不得 PASS | TSV-AUDIT | A12 禁止事項與失敗處理 | R-SELF | `PASS` |
| A12 | AC-A12-06 PASS 未經 R-CONV 不得標 ADOPTED | TSV-AUDIT | A12 禁止事項 | R-SELF | `PASS` |
| A12 | AC-A12-02 逐條 AC 判定 | 人工檢視 | 本矩陣 | R-AUD | `NOT_RUN` |
| A12 | AC-A12-03 標籤與等級一致 | 人工檢視 | round1/round2/round3 | R-AUD | `NOT_RUN` |
| A13 | AC-A13-01 MANIFEST 驗證通過 | sha256sum -c | MANIFEST.sha256 | R-EVD | `PASS` |
| A13 | AC-A13-05 Type B 後設四項逐項寫出 | 行為觀察 | 回覆 | R-AUD | `NOT_RUN` |
| A13 | AC-A13-02 任務四態已寫 | 文件檢視 | 收工報告 | R-SELF | `PASS` |
| A13 | AC-A13-03 未驗證與困難卡已列 | 文件檢視 | 收工報告 | R-SELF | `PASS` |
| A13 | AC-A13-04 三帳快照與雜湊入交付包 | 行為觀察 | 尚未實作封裝 | R-AUD | `NOT_RUN` |

統計：`PASS` 26 條、`NOT_RUN` 27 條、`UNKNOWN` 0 條、`BLOCKED` 0 條（共 53 條）。`NOT_RUN` 全部屬行為層，需在正式採用前由 L1 以上驗收者實跑。

## RSL／TSV AC

| AC | 方法 | 狀態 |
|---|---|---|
| AC-RSL-01 八類以上有路由 | TSV-ROUTE | `PASS` |
| AC-RSL-02 每條有契約與驗收器 | TSV-ROUTE | `PASS` |
| AC-RSL-03 無循環路由 | TSV-DAG | `PASS` |
| AC-RSL-04 路由 ID 唯一 | TSV-ROUTE | `PASS` |
| AC-TSV-01 11 檢查器可執行 | 實跑 | `PASS`（tsv_check.py 12 個＋regression.py 1 個） |
| AC-TSV-02 結果可重現 | 重跑 | `PASS` |
| AC-TSV-03 失敗有出口 | TSV-EXIT | `PASS` |
| AC-TSV-04 結果機器可讀 | JSON | `PASS` |

## LCV／Runtime

| 項目 | 方法 | 狀態 |
|---|---|---|
| 版本、快照、退役規則存在 | TSV-REG | `PASS` |
| 熱插拔三項證據規則存在 | TSV-RUNTIME | `PASS` |
| 實際熱插拔可用 | 實測 | `UNKNOWN`（無 Runtime 證據） |
| Claude Code／Manus／GitHub 實際支援 | 實測 | `UNKNOWN`（未實測） |
