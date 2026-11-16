# Manus 累積式 Skill 整合衝突與邊界報告

## 範圍

本報告涵蓋分支 `manus/integrated-skills-upgrade-20261116` 中導入的 20 個 Skill、治理架構、測試、移轉帳本、歷史快照及 Claude 來源資料。

## 已處理責任邊界

| 邊界 | 裁決 | 處理方式 |
|---|---|---|
| `miko-core` 與領域 Skill | 不重疊 | `miko-core` 保留常駐閉環、治理與路由；領域 Skill 只負責領域行為。 |
| `independent-audit` 與 `three-party-review` | 不合併責任 | 前者負責獨立驗收；後者定義 IMPLEMENTER／TESTER／INDEPENDENT_AUDITOR 三方責任。 |
| anti-fraud 與測試 Skill | 不替代功能測試 | anti-fraud 驗證證據可信度與反造假；各 Skill 仍須執行自己的功能、邊界與回歸測試。 |
| `version-evolution-preservation` 與各 Skill | 前置路由 | 各 Skill 必須先保存歷史、diff、Hash，再進行優化或重構。 |
| `batch-task-completion-and-single-report` 與逐筆測試 | 不跳過逐項驗收 | 批次只控制回報與整體完成條件，不把部分 PASS 當整批 PASS。 |
| Claude 來源資料與 MIKO 正本 | 只複製、不反向覆蓋 | Claude 檔案另存於 `governance/claude-source-import/`；來源檔仍保留於原路徑。 |

## 邊界缺口處理

未有實測證據的 GitHub 遠端採用、Runtime 熱插拔、Claude Code 執行或 Manus Runtime 生效，均保留為 `UNKNOWN`／`NOT_RUN`，不因文件完成而升格。

## 歷史保護

- MIKO main 基線快照：`archive/miko-main-baseline-20261116/skills/`。
- 導入前候選快照：`archive/manus-candidate-pre-upgrade-20261116/skills/`。
- 每個 Skill 的 SHA-256 與行數：`governance/integration-inventory.json`。

## 核心 Skill 格式例外

`miko-core` 為常駐核心 Skill，不套用領域 Skill 的四節／P-C-J linter；此為責任分層例外，不是測試豁免。其核心專用驗收規則見 `governance/validation-policy.md`。
