---
doc_id: auto-uga-architecture
version: 0.8.7
date: 2026-11-14
status: PROPOSED
---

# MIKO Universal Governance Architecture 架構書（候選）

- 文件狀態：PROPOSED（候選，未升格）
- 內部版本：0.8.7
- 對外封裝：UGA ZIP v1.0.2（見交付報告）
- 編號系統：ARC，與 UCP 的 A、UAC 的章節號、USC 的 S 各自獨立

## ARC-0 適用範圍
本架構書適用於產物類型為架構書的文件。依 UAC 第 5 章的類型分流條款，架構書類產物以 ARC-1～ARC-5 取代 UAC 第 5、6、7 章；一般文件仍用 UAC 十六章。本文件不寫製作步驟，執行軸見 UCP。

## ARC-1 系統元件與責任配置

| component_id | 責任 | 不負責 | owner_role |
|---|---|---|---|
| UCP | AI 如何執行：A00～A13 步驟、順序、閘門、交接動作、失敗出口、閉環 | 元件、介面、資料流、欄位定義 | R-CONV |
| 架構書 | 系統如何組成：元件、責任、介面、連接、資料流、失效設計、驗收架構 | 執行順序、欄位格式 | R-DESIGN |
| UAC | 一般文件契約：十六章、必要欄位、格式 | 製作步驟、系統結構 | R-DESIGN |
| USC | Skill 契約：九契約、四節、七欄、P／C／J | 通用流程、系統架構 | R-DESIGN |
| 帳本 | 全域三帳：錯誤、否決、變更；去重鍵合併 | 規則定義 | R-EVD |
| 工具 | ledger、build_packet、check_version、skill_lint、behavior_checks | 規則裁決 | R-EVD |
| Adapter | Runtime 接入（claude-code、manus、github、generic） | 任何已生效宣稱 | R-IMPL |

## ARC-2 系統介面與連接關係

UCP 對 UAC 的介面是契約引用：只取章節標題、編號、欄位名與 AC ID，不取內容定義。UCP 對 USC 的介面相同。架構書對 UCP 的介面是結構查詢：UCP 需要確認某步驟輸出屬於哪個元件時，讀 ARC-1 與 ARC-3，不自建元件表。帳本對全部元件的介面是 `entries.json` 與去重鍵；工具對交付的介面是 MANIFEST 與驗收包。

## ARC-3 系統資料流與依賴關係

資料流為：任務卡 → 契約鎖定 → 文件骨架 → 內容 → 證據 → 驗收包 → 定案。依賴關係是單向的：UCP 依賴 UAC 與 USC 的格式，UAC 不依賴 UCP 的步驟；架構書不被 UCP 依賴，只有查詢。附錄 A 的章節對步驟對應為單向，因此不存在 UCP → UAC → 附錄 A → UCP 的環。

## ARC-4 系統失效模式與復原設計

| 失效 | 設計回應 |
|---|---|
| 契約讀不到 | 標 NOT_READ，只用已讀版本並在文件標示 |
| 契約版本衝突 | 停止相依步驟，回報 R-CONV 裁決 |
| 驗收 FAIL | 回 A10 最小維護，只修受影響單元，再走 A11 有界重測 |
| 驗收包不符 | BLOCKED，重建 MANIFEST 後重驗 |
| Runtime 未實測 | 維持 UNKNOWN，禁止宣稱已支援 |

## ARC-5 系統驗收架構

驗收分三層：文件層用十二個檢查器與二十二題負向回歸；封裝層用 MANIFEST 驗證；行為層由 L1 以上獨立驗收者依 A12 逐條判定，目前行為層五項仍為 NOT_RUN。架構書本身只定義驗收架構，不執行驗收。
