未驗收提案

# 直接審核紀錄

## 已確認

- 附件 17 與 18 是上下游關係，不是互斥方案。
- 應先建 Capability Inventory，再做資產分類、概念轉化、缺口分析、外部吸收、編排與 E2E 驗收。
- 不應把所有外部 Skill 直接安裝。
- Skill、知識卡、Adapter、Workflow、Reference、Template、Script 與一次性成果必須可區分。

## 暫時假設

- 本提案先放在 `knowledge-cards/proposals/docs/`，作為未驗收候選文件。
- 目前不建立獨立 Runtime Skill；待階段 Gate 全部通過後再決定資產形態。

## UNKNOWN／NOT_RUN

- Manus Runtime 是否支援本架構的跨 Skill 編排：UNKNOWN。
- 外部平台 API、帳號資格與佣金資料管道：UNKNOWN。
- Anthropic Skill Creator 附件所述全部官方功能：UNKNOWN。
- 本架構的端到端實際執行：NOT_RUN。
- Claude 審核：NOT_RUN，依本輪直接審核指示。

## 邊界修正

- Orchestrator 不取代治理、Router 或 Runtime。
- 研究外部 Skill 不等於取得原始程式授權。
- 計畫、候選、授權、執行、驗證、交付與 Runtime 讀回必須分狀態。
- 持續改善必須有最大迭代次數、停滯條件與回復方式。
