未驗收提案

# MIKO Capability Ecosystem Architecture｜提案入口

本文件是 `miko-capability-ecosystem-architecture` 的提案入口。完整內容位於同資料夾：

- `README.md`：範圍、原則、八階段與狀態
- `stages/`：每階段的目的、輸入、輸出、操作、禁止、驗收、失敗、恢復、回歸與閉環
- `schemas/`：Capability Inventory、Concept Record、Asset Record 與 Workflow Record
- `governance/`：Gate、角色分離、狀態字典與證據要求

## 直接審核結論

附件 17 與 18 可整合，但必須採八階段順序，先建立能力目錄，再做資產分類、概念轉化、缺口分析、外部吸收、編排與端到端驗收。不能先大量安裝 Skill，也不能把規劃能力當成實際執行能力。

## 不在本提案內

- 不安裝外部 Skill。
- 不修改既有 MIKO 正本。
- 不修改 `skills/`、`VERSION` 或 Runtime 設定。
- 不宣稱 Manus 已支援熱插拔。
- 不宣稱 Shopee、momo 或任何外部平台已完成授權串接。
- 不建立第二套治理、權限或正式採用制度。
